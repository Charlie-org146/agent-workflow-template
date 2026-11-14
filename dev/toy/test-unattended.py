#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/unattended.py skills/workflow-docs/scripts/permissions.py
"""MON-18: unattended.py in throwaway git repos: the send count and its warning, the check-in loop's expiry, a standing
merge instruction (a worker cannot add one), and the start-up self-check's three MISSING lines."""
import datetime
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
script = os.path.join(root, "skills", "workflow-monitoring", "scripts", "unattended.py")
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(args), cwd=cwd, capture_output=True, text=True)


def repo():
    top = tempfile.mkdtemp(prefix="unatt-toy-")
    git(top, "init", "-q", "-b", "main")
    return top


def run(top, *args, role=""):
    env = dict(os.environ, LOOP_ROLE=role)
    done = subprocess.run([sys.executable, script] + list(args), cwd=top, capture_output=True, text=True, env=env)
    return done.returncode, done.stdout + done.stderr


top = repo()
for _ in range(15):
    run(top, "sends", "add", "w")
code, out = run(top, "sends")
check("sends: 15 of 20, 5 left, no warning", "15 of 20" in out and "(5 left)" in out and "WARNING" not in out)
run(top, "sends", "add", "w")
check("sends: the 16th warns and asks for an owner message", "WARNING" in run(top, "sends")[1])
run(top, "sends", "reset")
check("sends: an owner message resets the count", "SENDS 0 of 20" in run(top, "sends")[1])

check("loop: nothing recorded says so", "none recorded" in run(top, "loop")[1])
check("loop: created records 7 days", "expires in 6d" in run(top, "loop", "created")[1])
path = os.path.join(top, ".git", "loop", "checkin-loop.json")
for hours, word in ((5, "RECREATE"), (-1, "EXPIRED")):
    end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    with open(path, "w") as handle:
        json.dump({"expires": end.strftime("%Y-%m-%dT%H:%M:%SZ")}, handle)
    check("loop: %s inside the last day / after the end" % word, word in run(top, "loop")[1])

code, out = run(top, "standing", "add", "merge any green pr", "--goals", "a,b", role="worker")
check("standing: a worker cannot add one", code != 0 and "REFUSED" in out)
code, out = run(top, "standing", "add", "merge any green pr", "--goals", "a,b")
check("standing: the operation session adds one", code == 0 and "STANDING s1" in out)
check("standing: a covered goal reads STANDING", run(top, "standing", "check", "a", role="worker")[0] == 0)
check("standing: an uncovered goal waits", run(top, "standing", "check", "z", role="worker")[0] == 1)
run(top, "standing", "add", "all of them", "--goals", "all")
check("standing: all covers every goal", "STANDING s2" in run(top, "standing", "check", "z")[1])
run(top, "standing", "revoke", "s2")
check("standing: a revoked one no longer covers", run(top, "standing", "check", "z")[0] == 1)

top = repo()
os.makedirs(os.path.join(top, ".claude"))
with open(os.path.join(top, ".claude", "settings.local.json"), "w") as handle:
    json.dump({"permissions": {"defaultMode": "default"}}, handle)
code, out = run(top, "selfcheck")
check("selfcheck: defaultMode default is MISSING and exits 1", code == 1 and "MISSING permission mode" in out)
with open(os.path.join(top, ".claude", "settings.local.json"), "w") as handle:
    json.dump({"permissions": {"defaultMode": "acceptEdits"}}, handle)
check("selfcheck: acceptEdits passes the mode", "permission mode" not in run(top, "selfcheck")[1])

os.makedirs(os.path.join(top, ".loop"))
with open(os.path.join(top, ".loop", "routines.tsv"), "w") as handle:
    handle.write("round\tFeature\n")
with open(os.path.join(top, ".loop", "permissions.tsv"), "w") as handle:
    handle.write("other\tallow\tBash(ls:*)\tx\n")
code, out = run(top, "selfcheck")
check("selfcheck: a routine with no rows is MISSING routine rules", code == 1 and "MISSING routine rules: UNDECLARED round" in out)

origin = tempfile.mkdtemp(prefix="unatt-origin-")
git(origin, "init", "-q", "--bare", "-b", "main")
work = repo()
with open(os.path.join(work, "a"), "w") as handle:
    handle.write("1")
git(work, "add", "a")
git(work, "commit", "-q", "-m", "one")
git(work, "remote", "add", "origin", origin)
git(work, "push", "-q", "origin", "main")
other = tempfile.mkdtemp(prefix="unatt-other-")
git(other, "clone", "-q", origin, "c")
clone = os.path.join(other, "c")
with open(os.path.join(clone, "a"), "w") as handle:
    handle.write("2")
git(clone, "commit", "-qam", "two")
git(clone, "push", "-q", "origin", "main")
with open(os.path.join(work, ".claude.json"), "w"):
    pass
os.makedirs(os.path.join(work, ".claude"))
with open(os.path.join(work, ".claude", "settings.local.json"), "w") as handle:
    json.dump({"permissions": {"defaultMode": "auto"}}, handle)
code, out = run(work, "selfcheck")
check("selfcheck: a main checkout behind origin is MISSING", code == 1 and "MISSING main checkout: 1 commit(s) behind origin/main" in out)
git(work, "pull", "-q", "origin", "main")
code, out = run(work, "selfcheck")
check("selfcheck: a current checkout with its rules is SELFCHECK OK", code == 0 and "SELFCHECK OK" in out)

print("UNATTENDED TOY: %d failed" % fails if fails else "UNATTENDED TOY OK")
sys.exit(1 if fails else 0)
