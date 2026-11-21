#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/actions.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/lanes.py
"""lane-scrub (#5700): a row run by the lane runner never sees the host session variables.

Done 1: a fake row that reports each host session variable, run through runs.execute with fake values set, sees none of them.
Done 2: the real .git/loop/operation.id hashes the same before and after the lane run (the hash is compared, never printed);
        with the scrub reverted in a scratch copy of the scripts the same row sees every variable, so this toy fails there."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
real = os.path.join(root, "skills", "workflow-regression", "scripts")
HOST = ("CLAUDE_CODE_HOST_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "CLAUDE_SESSION_ID", "LOOP_POD_ID", "LOOP_OPERATION_SESSION")
KEEP = {"LOOP_PRIVATE_NAMES": "/toy/private-names", "LOOP_ROLE": "worker", "LOOP_SESSION_TOOL": "toy-tool", "TOY_KEEP": "kept"}
PROBE = """import json, os, sys
names = sys.argv[1:]
print("PROBE " + json.dumps({n: os.environ.get(n) for n in names + ["PATH"]}))
"""
DRIVER = """import json, os, sys, tempfile
sys.path.insert(0, sys.argv[1])
import runs
with tempfile.TemporaryDirectory() as tmp:
    probe = os.path.join(tmp, "probe.py")
    open(probe, "w").write(sys.argv[2])
    row = {"id": "fake", "command": '"%s" "%s" %s' % (sys.executable, probe, " ".join(sys.argv[3:]))}
    results, _ = runs.execute(tmp, [row], ["fake"], {}, None, 60, {}, True)
print("RESULT " + json.dumps(results[0]["tail"]))
"""
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def lane(scripts):
    """The row's environment as the lane runner hands it over, with fake host values set around it."""
    env = dict(os.environ, **KEEP)
    env.update({name: "fake-" + name.lower() for name in HOST})
    done = subprocess.run([sys.executable, "-c", DRIVER, scripts, PROBE] + list(HOST) + list(KEEP), env=env, capture_output=True, text=True)
    line = [x for x in done.stdout.splitlines() if x.startswith("RESULT ")]
    tail = json.loads(line[0][7:]) if line else ""
    seen = [x for x in tail.splitlines() if x.startswith("PROBE ")]
    return (json.loads(seen[0][6:]) if seen else None), env


def operation_hash():
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root, capture_output=True, text=True).stdout.strip()
    path = os.path.join(common, "loop", "operation.id")
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if os.path.exists(path) else "absent"


before = operation_hash()
got, env = lane(real)
after = operation_hash()
check(got is not None, "the fake row ran under the lane runner")
got = got or {}
check(all(got.get(name) is None for name in HOST), "the row sees none of the host session variables")
check(all(got.get(name) == value for name, value in KEEP.items()), "LOOP_PRIVATE_NAMES and the other variables come through unchanged")
check(got.get("PATH") == env["PATH"], "PATH comes through unchanged")
check(before == after, "the real .git/loop/operation.id is byte-identical before and after the lane run")

# negative control: the scrub reverted in a scratch copy of the scripts
with tempfile.TemporaryDirectory() as tmp:
    scratch = os.path.join(tmp, "scripts")
    shutil.copytree(real, scratch, ignore=shutil.ignore_patterns("__pycache__"))
    path = os.path.join(scratch, "actions.py")
    text = open(path).read()
    broken = text.replace("ROW_DROP + SESSION_DROP", "ROW_DROP")
    check(broken != text, "the scratch copy has the scrub removed")
    open(path, "w").write(broken)
    got, _ = lane(scratch)
    got = got or {}
    check(all(got.get(name) == "fake-" + name.lower() for name in HOST), "negative control: with the scrub reverted the row sees every host variable")
sys.exit(1 if failed else 0)
