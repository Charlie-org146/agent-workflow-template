#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/actions.py
# reads: skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/narrow.py
"""budget-order (TD476): inside a shard's time budget the selected rows run closest to the change first: rows whose command
names a changed file, then rows for a requirement the diff touches, then the rest by measured time, shortest first. A toy
repo changes one toy; its row sits last in the file and used to be LEFT by a budget that fits two rows."""
import os
import subprocess
import sys
import tempfile

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
sys.exit(1 if failed else 0)
