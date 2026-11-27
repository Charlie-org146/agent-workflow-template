#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/actions.py
# reads: skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/narrow.py dev/check-row-merge.py
"""budget-order (TD476): inside a shard's time budget the selected rows run closest to the change first: rows whose command
names a changed file, then rows for a requirement the diff touches, then the rest by measured time, shortest first. A toy
repo changes one toy; its row sits last in the file and used to be LEFT by a budget that fits two rows."""
import os
import subprocess
import sys
import tempfile

# the caller's git environment is not passed on; its git config choices and discovery limit are kept
for name in [n for n in os.environ if n.startswith("GIT_") and not n.startswith("GIT_CONFIG_") and n != "GIT_CEILING_DIRECTORIES"]:
    del os.environ[name]
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
sys.dont_write_bytecode = True
import actions  # noqa: E402
import runs  # noqa: E402
import tiers  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git(tmp, *args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t"] + list(args), cwd=tmp, check=True, capture_output=True)


with tempfile.TemporaryDirectory() as tmp:
    git(tmp, "init", "-q", "-b", "main")
    os.makedirs(os.path.join(tmp, "dev", "toy"))
    for name in ("a.sh", "b.sh", "c.sh", "d.sh"):
        open(os.path.join(tmp, "dev", "toy", name), "w").write("echo 1\n")
    open(os.path.join(tmp, "spec.md"), "w").write("REQ-7 holds\n")
    git(tmp, "add", ".")
    git(tmp, "commit", "-q", "-m", "base")
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True, text=True).stdout.strip()
    open(os.path.join(tmp, "dev", "toy", "d.sh"), "w").write("echo 2\n")  # the changed toy
    open(os.path.join(tmp, "spec.md"), "w").write("REQ-7 holds, changed\n")  # the touched requirement
    git(tmp, "commit", "-q", "-am", "change")
    rows = [{"id": "slow-a", "command": "bash dev/toy/a.sh", "goal": "REQ-1"}, {"id": "fast-b", "command": "bash dev/toy/b.sh", "goal": "REQ-2"},
            {"id": "req-c", "command": "bash dev/toy/c.sh", "goal": "REQ-7"}, {"id": "toy-d", "command": "bash dev/toy/d.sh", "goal": "REQ-3"}]
    secs = {"slow-a": 50, "fast-b": 5, "req-c": 30, "toy-d": 40}
    near = tiers.closeness(tmp, rows, base, {k: {"seconds": v} for k, v in secs.items()})
    ids = [r["id"] for r in rows]
    ordered = sorted(ids, key=lambda k: near[k])
    check(ordered == ["toy-d", "req-c", "fast-b", "slow-a"], "the changed toy's row first, then the touched requirement's, then the rest shortest first: %s" % ordered)
    keep, left = runs.fit(ids, secs, 90)
    check(left == ["toy-d"], "before: file order and a 90 s budget leaves the changed toy's row LEFT: %s" % left)
    keep, left = runs.fit(ordered, secs, 90)
    check("toy-d" in keep and sorted(keep + left) == sorted(ids), "after: the changed toy's row runs and nothing is dropped: keep %s, left %s" % (keep, left))
    check(tiers.closeness(tmp, rows, None, {}) == {k: (2, 0, 0) for k in ids}, "with no merge-base every row is the rest, in file order")
os.environ["LOOP_ROW_TIMES"] = "/nowhere/t.tsv"  # a row that runs regression.py itself must not write this shard's times file
check("LOOP_ROW_TIMES" not in actions.row_env(), "a row never inherits the shard's times file, so no row can overwrite its marks")
handoff = ("_LOOP_LANE_NOTE", "_LOOP_LANE_QUEUED", "_LOOP_LANE_STARTED")  # lane.py sets these for the lane's own runner
kept_before = {name: os.environ.get(name) for name in handoff + ("_LOOP_LANE_LABEL",)}
os.environ.update({name: "/nowhere/lane" for name in handoff}, _LOOP_LANE_LABEL="x/g qa")
given = actions.row_env()
check(not [name for name in handoff if name in given], "a row never inherits a lane's note, queued or started path")
check(given.get("_LOOP_LANE_LABEL") == "x/g qa", "and a row still gets the lane's label")
for name, value in kept_before.items():
    if value is None:
        del os.environ[name]
    else:
        os.environ[name] = value
theirs = {"GIT_DIR": "/nowhere/git", "GIT_INDEX_FILE": "/nowhere/index", "GIT_WORK_TREE": "/nowhere/tree", "GIT_CONFIG": "/nowhere/one",
          "GIT_AUTHOR_NAME": "caller"}
kept_before = {name: os.environ.get(name) for name in theirs}
os.environ.update(theirs)
given = actions.row_env()
check(not [name for name in theirs if name in given], "a row never inherits the caller's git environment")
check([given.get(name) for name in ("GIT_TERMINAL_PROMPT", "GIT_EDITOR", "GIT_ASKPASS")] == ["0", "true", "true"],
      "and a row's git still never waits for a person")
for name, value in kept_before.items():
    if value is None:
        del os.environ[name]
    else:
        os.environ[name] = value
chosen = {"GIT_CONFIG_GLOBAL": "/nowhere/global", "GIT_CONFIG_SYSTEM": "/nowhere/system", "GIT_CONFIG_NOSYSTEM": "1"}
kept_before = {name: os.environ.get(name) for name in chosen}
os.environ.update(chosen)
given = actions.row_env()
check({name: given.get(name) for name in chosen} == chosen, "a row keeps the caller's choice of git config files")
for name, value in kept_before.items():
    if value is None:
        del os.environ[name]
    else:
        os.environ[name] = value
limits = {"GIT_CEILING_DIRECTORIES": "/nowhere/ceiling", "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.hooksPath",
          "GIT_CONFIG_VALUE_0": "/nowhere/hooks", "GIT_CONFIG_PARAMETERS": "'core.hooksPath=/nowhere/hooks'"}
kept_before = {name: os.environ.get(name) for name in limits}
os.environ.update(limits)
given = actions.row_env()
check({name: given.get(name) for name in limits} == limits, "a row keeps the caller's git limit and injected git settings")
for name, value in kept_before.items():
    if value is None:
        del os.environ[name]
    else:
        os.environ[name] = value
names = ("_LOOP_LANE_NOTE", "_LOOP_LANE_QUEUED", "_LOOP_LANE_STARTED", "GIT_AUTHOR_NAME")
with tempfile.TemporaryDirectory() as tmp:
    git(tmp, "init", "-q", "-b", "main")
    os.makedirs(os.path.join(tmp, "dev", "toy"))
    os.makedirs(os.path.join(tmp, ".loop"))
    with open(os.path.join(tmp, "dev", "toy", "probe.py"), "w") as handle:
        handle.write("import os\nheld = [n for n in %r if n in os.environ]\nprint('FAIL: held ' + ' '.join(held) if held else 'PASS: clean')\n" % (names,))
    merged = 'out=$(python3 dev/toy/probe.py 2>&1); printf "%s\\n" "$out" | grep -qF "PASS: clean" && ! printf "%s\\n" "$out" | grep -q "^ *FAIL"'
    with open(os.path.join(tmp, ".loop", "regression.tsv"), "w") as handle:
        handle.write("probe\tland\t%s\tREG-4\n" % merged)
    git(tmp, "add", ".")
    git(tmp, "commit", "-q", "-m", "base")
    done = subprocess.run([sys.executable, os.path.join(root, "dev", "check-row-merge.py"), "HEAD"], cwd=tmp, capture_output=True, text=True,
                          env=dict(os.environ, **{name: "caller" for name in names}))
    # the checker runs a row only where /bin/dash exists; there it must report this one as passed
    ran = "dash PASS probe" in done.stdout if os.path.exists("/bin/dash") else "dash " not in done.stdout
    check(done.returncode == 0 and ran, "the row-merge checker starts rows with the row environment")
if sys.argv[1:] != ["--inner"]:
    with tempfile.TemporaryDirectory() as tmp:
        other = os.path.join(tmp, "second")
        subprocess.run(["git", "init", "-q", "-b", "main", other], check=True, capture_output=True)
        with open(os.path.join(other, "kept.txt"), "w") as handle:
            handle.write("kept\n")
        as_t = ["-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false"]
        for args in (["add", "kept.txt"], as_t + ["commit", "-q", "-m", "kept"]):
            subprocess.run(["git", "-C", other] + args, check=True, capture_output=True)

        def held():
            found = {}
            for folder, _, files in os.walk(other):
                for name in files:
                    with open(os.path.join(folder, name), "rb") as handle:
                        found[os.path.relpath(os.path.join(folder, name), other)] = handle.read()
            return found

        before = held()
        gitdir = os.path.join(other, ".git")
        env = dict(os.environ, GIT_DIR=gitdir, GIT_INDEX_FILE=os.path.join(gitdir, "index"))
        done = subprocess.run([sys.executable, os.path.abspath(__file__), "--inner"], env=env, capture_output=True,
                              stdin=subprocess.DEVNULL, timeout=200)
        same = held() == before
    text = "run with a git environment naming a second repository, this toy passes and leaves that repository as it was"
    if done.returncode or not same:
        text += " (the second repository: %s; the inner run: %s)" % ("unchanged" if same else "changed",
                                                                     "did not pass" if done.returncode else "passed")
    check(not done.returncode and same, text)
sys.exit(1 if failed else 0)
