#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/tests.py skills/workflow-regression/scripts/actions.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/lanes.py skills/workflow-monitoring/scripts/operate.py .github/workflows/regression.yml
"""lane-scrub (#5700, goal lane-scrub-2): a row run by the lane runner never sees the host session variables.

Done 1: a fake row that reports each host session variable, run through runs.execute with fake values set, sees none of them.
Done 1 also holds for the pr step's lane_checks (tests.py): a plain job's `run:` step sees none of them.
Done 2: the row also tries to write every id it sees into an operation.id the toy plants in its OWN temp repo (through operate.add_id,
        the writer a leaked id would reach); scrubbed, the planted file is unchanged, and with the scrub reverted in a scratch copy of
        the scripts it holds the fake ids, so this toy fails there. The real .git/loop/operation.id is only read (an informational line).

Who owns the name list: actions.SESSION_DROP in skills/workflow-regression/scripts/actions.py. To add a name: add it there, regenerate
the embedded copy (regression.py workflow), run this toy. If this toy names a variable it does not drop (the drift scan), either add it
to SESSION_DROP or, when it is not a host session variable, add it to ALLOW below with the reason.
Red demonstration: regression.py red defect-5700-lane-scrub --break "<python -c that replaces 'ROW_DROP + SESSION_DROP' with 'ROW_DROP' in actions.py>".
There is no opt-out: a row that needs a session id takes it from its own arguments, never from the environment."""
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

sys.dont_write_bytecode = True
started = time.time()
root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
real = os.path.join(root, "skills", "workflow-regression", "scripts")
OPERATE = os.path.join(root, "skills", "workflow-monitoring", "scripts", "operate.py")
ACTIONS = "skills/workflow-regression/scripts/actions.py"
sys.path.insert(0, real)
import actions  # noqa: E402

HOST = tuple(actions.SESSION_DROP)
FAKE = {name: "fake-" + name.lower() for name in HOST}
# Edge values on purpose: an empty value, surrounding and doubled spaces, a newline (LOOP_PRIVATE_NAMES keeps a real path: row_env defaults it).
KEEP = {"LOOP_PRIVATE_NAMES": "/toy/private-names", "LOOP_ROLE": "", "LOOP_SESSION_TOOL": " toy  tool ", "TOY_KEEP": "line one\nline two"}
ALLOW = {}  # name -> reason it matches the session-name pattern without being a host session variable (empty on purpose)
NAME = re.compile(r"[A-Z][A-Z0-9_]*(SESSION_ID|POD_ID|OPERATION_SESSION)")
TIMEOUT = 60
REPAIR = "add the name to SESSION_DROP in " + ACTIONS + " and run `python3 skills/workflow-regression/scripts/regression.py workflow`"

PROBE = """import importlib.util, inspect, json, os, sys
operate_path, base, host, keep = sys.argv[1], sys.argv[2], sys.argv[3].split(","), sys.argv[4].split(",")
sys.path.insert(0, os.path.dirname(operate_path))
spec = importlib.util.spec_from_file_location("operate", operate_path)
operate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(operate)
print("SIG " + ",".join(inspect.signature(operate.add_id).parameters))
offered = 0
for name in host:
    if os.environ.get(name):
        operate.add_id(base, os.environ[name])
        offered += 1
print("PROBE " + json.dumps({n: os.environ.get(n) for n in host + keep + ["PATH"]}))
print("OFFERED %d" % offered)
"""
DRIVER = """import json, shlex, sys
sys.path.insert(0, sys.argv[1])
import runs
row = {"id": "fake", "command": shlex.join(sys.argv[3:])}
results, _ = runs.execute(sys.argv[2], [row], ["fake"], {}, None, 60, {}, True)
print("RESULT " + json.dumps(results[0]["tail"]))
"""
CI = """name: ci
on: [push]
jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - run: python3 probe.py
"""
CHECKS = """import sys
sys.path.insert(0, sys.argv[1])
import tests
top = sys.argv[2]
tests.lane_checks(top, ["checks"])
print("SEEN " + open(top + "/seen.json").read())
"""
PLAIN = "import json, os\njson.dump({n: os.environ.get(n) for n in %r}, open('seen.json', 'w'))\n"
failed = []
made = []


def check(ok, text, detail=""):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)
        if detail:
            print("      " + detail)


def tmp():
    path = tempfile.mkdtemp(prefix="lane-scrub-")
    made.append(path)
    return path


def run(argv, env=None, cwd=None):
    """The output of a subprocess (list form, never a shell), or None after the timeout."""
    try:
        return subprocess.run(argv, env=env, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None


def tagged(out, tag):
    line = [x for x in (out or "").splitlines() if x.startswith(tag + " ")]
    return line[0][len(tag) + 1:] if line else None


def leaked(seen):
    return [n for n in HOST if (seen or {}).get(n) is not None]


def kept(seen, env, label):
    bad = [n for n, v in KEEP.items() if (seen or {}).get(n) != v]
    check(not bad, "%s: LOOP_PRIVATE_NAMES, LOOP_ROLE, LOOP_SESSION_TOOL and TOY_KEEP come through unchanged (empty, spaced and newline values included)" % label,
          "changed or dropped (names only): " + ", ".join(bad))
    check((seen or {}).get("PATH") == env["PATH"], "%s: PATH comes through unchanged" % label)


def edit(path, old, new, what):
    """A scratch edit that must apply exactly once and change the copy (so a negative control cannot pass vacuously)."""
    text = open(path).read()
    ok = text.count(old) == 1 and old != new
    check(ok, "the scratch copy has %s" % what, "found %d times in %s (want exactly 1); the text moved, update this toy" % (text.count(old), os.path.basename(path)))
    open(path, "w").write(text.replace(old, new))
    return ok


def real_state():
    """Informational only: the real operation.id as 'absent' or a hash (never printed), read, never written."""
    common = (run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root) or "").strip()
    path = os.path.join(common, "loop", "operation.id")
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if common and os.path.isfile(path) else "absent", common


def lane(scripts, repo, base):
    """The row's environment as the lane runner hands it over, with fake host values set around it (the toy's own os.environ is never edited)."""
    env = dict(os.environ, **KEEP, **FAKE)
    probe = os.path.join(repo, "probe.py")
    open(probe, "w").write(PROBE)
    out = run([sys.executable, "-c", DRIVER, scripts, repo, sys.executable, probe, OPERATE, base, ",".join(HOST), ",".join(KEEP)], env=env)
    tail = json.loads(tagged(out, "RESULT") or '""')
    seen = tagged(tail, "PROBE")
    return {"seen": json.loads(seen) if seen else None, "sig": tagged(tail, "SIG"), "offered": tagged(tail, "OFFERED")}, env


def lane_checks(scripts):
    """What a plain CI job's step sees when tests.lane_checks runs it here, with fake host values set."""
    env = dict(os.environ, **KEEP, **FAKE)
    top = tmp()
    os.makedirs(os.path.join(top, ".github", "workflows"))
    open(os.path.join(top, ".github", "workflows", "ci.yml"), "w").write(CI)
    open(os.path.join(top, "probe.py"), "w").write(PLAIN % (list(HOST) + list(KEEP) + ["PATH"],))
    seen = tagged(run([sys.executable, "-c", CHECKS, scripts, top], env=env), "SEEN")
    return (json.loads(seen) if seen else None), env


def planted_ids(path):
    return open(path).read().split()


def planted_repo():
    """The toy's own temp repo with an operation.id planted in it; the row can only reach this one through add_id(base, ...)."""
    repo = tmp()
    base = os.path.join(repo, ".git")
    os.makedirs(os.path.join(base, "loop"))
    path = os.path.join(base, "loop", "operation.id")
    open(path, "w").write("planted-session-id\n")
    return repo, base, path


def drift(tree):
    """Every string constant under tree/**/*.py that looks like a session variable name: (path, line, name)."""
    hits = []
    for dirpath, _, files in os.walk(tree):
        for name in sorted(files):
            if name.endswith(".py"):
                path = os.path.join(dirpath, name)
                try:
                    nodes = ast.walk(ast.parse(open(path).read(), path))
                except (SyntaxError, ValueError) as err:
                    hits.append((path, 0, "UNPARSEABLE: %s" % err))
                    continue
                hits += [(path, n.lineno, n.value) for n in nodes if isinstance(n, ast.Constant) and isinstance(n.value, str) and NAME.fullmatch(n.value)]
    return hits


def embedded(top):
    """The two embedded copies of tests.py in the workflow, dedented."""
    text = open(os.path.join(top, ".github", "workflows", "regression.yml")).read()
    return [textwrap.dedent(m) for m in re.findall(r"<<'TESTS_PY_EOF'\n(.*?)\n\s*TESTS_PY_EOF", text, re.S)]


# ---- the runner path, with the planted operation.id
before, common = real_state()
repo, base, planted = planted_repo()
pre = hashlib.sha256(open(planted, "rb").read()).hexdigest()
check(bool(open(planted).read().strip()), "the planted operation.id is non-empty before the run")
temp = os.path.realpath(tempfile.gettempdir())
check(os.path.realpath(base).startswith(temp + os.sep) and os.path.realpath(base) != os.path.realpath(common or "/nonexistent"),
      "the planted base is under the temp dir and is not the real common git dir")
check(isinstance(actions.SESSION_DROP, tuple) and len(HOST) == len(set(HOST)) and all(HOST), "actions.SESSION_DROP is a tuple of distinct names")
got, env = lane(real, repo, base)
check(got["seen"] is not None and got["offered"] is not None,
      "the fake row ran under the lane runner and finished (the probe reached its last line)",
      "no PROBE or OFFERED line: the probe crashed or operate.py no longer imports here (operate.add_id moved or changed?)")
check(got["sig"] == "base,sid", "operate.add_id keeps its call shape (base, sid)", "operate.add_id changed: its parameters are now %r; update the probe in this toy" % got["sig"])
check(not leaked(got["seen"]) and got["seen"] is not None, "the row sees none of the host session variables",
      "leaked (names only): %s. Repair: %s" % (", ".join(leaked(got["seen"])), REPAIR))
kept(got["seen"], env, "runner")
check(got["offered"] == "0", "the row had no session id to offer to operate.add_id", "it offered %s ids" % got["offered"])
check(hashlib.sha256(open(planted, "rb").read()).hexdigest() == pre, "the planted operation.id is byte-identical after the lane run (compared by hash)",
      "a lane run wrote to an operation.id: a host session variable reached the row. Repair: " + REPAIR)
seen, env = lane_checks(real)
check(seen is not None and not leaked(seen), "lane_checks runs a plain job's step without the host variables",
      "leaked (names only): %s. Repair: %s" % (", ".join(leaked(seen)), REPAIR))
kept(seen, env, "lane_checks")

# ---- negative controls: the scrub reverted in a scratch copy of the scripts
with_scratch = tmp()
scratch = os.path.join(with_scratch, "scripts")
shutil.copytree(real, scratch, ignore=shutil.ignore_patterns("__pycache__"))
if edit(os.path.join(scratch, "actions.py"), "ROW_DROP + SESSION_DROP", "ROW_DROP", "the scrub removed from row_env"):
    repo2, base2, planted2 = planted_repo()
    got2, _ = lane(scratch, repo2, base2)
    check(not [n for n in HOST if (got2["seen"] or {}).get(n) != FAKE[n]] and got2["seen"] is not None,
          "negative control: with the scrub reverted the row sees every host variable")
    written = planted_ids(planted2)
    check(all(FAKE[n] in written for n in HOST) and got2["offered"] == str(len(HOST)),
          "negative control: with the scrub reverted the row writes every fake id into the planted operation.id (this toy fails there)")
if edit(os.path.join(scratch, "tests.py"), "k not in actions.SESSION_DROP", "True", "lane_checks' scrub removed"):
    seen, _ = lane_checks(scratch)
    check(seen is not None and all((seen or {}).get(n) == FAKE[n] for n in HOST),
          "negative control: lane_checks with the scrub reverted lets the step see every host variable")

# ---- drift: every session-looking name the scripts spell out is dropped (or allowed with a reason)
skills = os.path.join(root, "skills")
found = drift(skills)
bad = [h for h in found if h[2] not in HOST and h[2] not in ALLOW]
check(not bad, "every session-variable name spelled in skills/**/*.py is in actions.SESSION_DROP or ALLOW (owner: goal lane-scrub-2, #5700)",
      "; ".join("%s:%d names %s, which is not dropped. Repair: %s, or add it to ALLOW in dev/toy/test-lane-scrub.py with a reason"
                % (os.path.relpath(p, root), n, v, REPAIR) for p, n, v in bad))
check(all(name in {h[2] for h in found} for name in ALLOW), "every ALLOW entry still appears in skills/ (a stale entry is removed)")
plant = os.path.join(with_scratch, "drift")
os.makedirs(plant)
open(os.path.join(plant, "x.py"), "w").write('NEW = "CLAUDE_FAKE_SESSION_ID"\nOK = "NOT_A_NAME"\n')
check([h[2] for h in drift(plant)] == ["CLAUDE_FAKE_SESSION_ID"], "negative control: a new session-variable name in a scratch file is found by the drift scan")

# ---- the embedded copy in the workflow never calls lane_checks (it would import actions, which that copy does not ship)
copies = embedded(root)
check(len(copies) == 2, "the workflow embeds two copies of tests.py", "found %d" % len(copies))
for i, text in enumerate(copies, 1):
    try:
        tree = ast.parse(text)
    except SyntaxError as err:
        check(False, "embedded copy %d compiles" % i, str(err))
        continue
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) == "lane_checks"]
    defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "lane_checks"]
    check(not calls and len(defs) == 1 and text.count("actions.SESSION_DROP") == 1,
          "embedded copy %d defines lane_checks, calls it nowhere, and filters on actions.SESSION_DROP once" % i,
          "%d call(s) to lane_checks: the embedded copy cannot import actions (latent trap, #5703)" % len(calls))

# ---- the real operation.id is only read; informational, never a gate
after, _ = real_state()
print("INFO: the real operation.id was %s across this toy (not a gate: the planted file above is the gate; a legitimate claim by another session changes it)"
      % ("absent before and after" if before == after == "absent" else "unchanged" if before == after else "changed"))

for path in made:
    shutil.rmtree(path, ignore_errors=True)
check(not [p for p in made if os.path.exists(p)], "no temp dir is left behind")
check(time.time() - started < 30, "the toy finishes inside 30 seconds", "took %.1f s" % (time.time() - started))
if failed:
    sys.stderr.write("test-lane-scrub: %d check(s) failed: %s\n" % (len(failed), "; ".join(failed)))
sys.exit(1 if failed else 0)
