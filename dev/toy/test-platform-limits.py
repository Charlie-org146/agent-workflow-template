#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/unattended.py skills/workflow-monitoring/scripts/sessions.py
"""OPS-1: the platform limits are counted before they are reached. In a throwaway git repo with a fake session tool: every
send is counted with its time and the owner's words reset the count (a peer's do not); one event is one message per distinct
worker session; at 15 of 20 the check-in says when the cap runs out, once; a worker comes only from a free (archived)
session and a new one is refused; both scripts stay no larger than main and under the package gate."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-monitoring", "scripts")
unattended, sessions = os.path.join(scripts, "unattended.py"), os.path.join(scripts, "sessions.py")
fails = 0
HOME = tempfile.mkdtemp(prefix="limits-home-")


def real_id_hash():
    """Hash of the checkout's own .git/loop/operation.id (or "absent"); never its contents."""
    import hashlib
    try:
        out = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"], capture_output=True, text=True).stdout.strip()
        path = os.path.join(os.path.abspath(os.path.join(root, out)), "loop", "operation.id")
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return "absent"


REAL_BEFORE = real_id_hash()


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def run(top, script, *args, **env):
    # hermetic: no host session id or loop setting, and a throwaway HOME so the owner's ~/.claude.json and ~/.workflow-loop are never read
    keep = {k: v for k, v in os.environ.items() if not k.startswith(("LOOP_", "CLAUDE"))}
    keep.update(HOME=HOME, USERPROFILE=HOME)
    done = subprocess.run([sys.executable, script] + list(args), cwd=top, capture_output=True, text=True, env=dict(keep, **env))
    return done.returncode, done.stdout + done.stderr


def count(top):
    try:
        with open(os.path.join(top, ".git", "loop", "sends.json")) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


top = tempfile.mkdtemp(prefix="limits-toy-")
subprocess.run(["git", "init", "-q", "-b", "main"], cwd=top, capture_output=True)
loop = os.path.join(top, ".git", "loop")
os.makedirs(os.path.join(loop, "runs"))
os.makedirs(os.path.join(top, ".loop"))
with open(os.path.join(top, ".loop", "config.json"), "w") as handle:
    json.dump({"base": "main"}, handle)
log = os.path.join(top, "tool.log").replace("\\", "/")
fake = os.path.join(top, "fake.py").replace("\\", "/")
with open(fake, "w") as handle:
    handle.write("import sys\nopen(sys.argv[1], 'a').write(' '.join(sys.argv[2:]) + '\\n')\nprint('new-1' if sys.argv[2] == 'start' else 'ok')\n")
tool = {"LOOP_SESSION_TOOL": "%s %s %s" % (sys.executable.replace("\\", "/"), fake, log)}


def calls():
    try:
        with open(log) as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def goal(slug, sid):
    state = {"slug": slug, "status": "running", "worker": "session", "step": "build", "session": {"id": sid, "name": "worker \u00b7 " + slug}}
    with open(os.path.join(loop, "runs", slug + ".json"), "w") as handle:
        json.dump(state, handle)


for slug, sid in (("a", "s1"), ("b", "s1"), ("c", "s2")):
    goal(slug, sid)
with open(os.path.join(loop, "session-pool.json"), "w") as handle:
    json.dump({"s1": {"name": "worker \u00b7 a", "slug": "a", "state": "busy"}, "s2": {"name": "worker \u00b7 c", "slug": "c", "state": "busy"}}, handle)

# (a) every send is counted with its time
for _ in range(3):
    run(top, unattended, "sends", "add", "w")
held = count(top)
check("a: three sends are counted, each with its time", held.get("count") == 3 and len(held.get("times", [])) == 3)

# (b) one event, one message per distinct worker session
code, out = run(top, sessions, "send", "a,b,c", "ship it", **tool)
sent = [x for x in calls() if x.startswith("send ")]
check("b: goals a and b share a session, so three goals are two messages", code == 0 and len(sent) == 2)
check("b: the shared session's one message names both goals", any("s1" in x and "a, b" in x and "ship it" in x for x in sent))
check("b: each message actually sent is counted once", count(top).get("count") == 5)

# (a) a worker's report is one counted send
run(top, sessions, "report", "c", "--status", "running", "--text", "building")
check("a: a worker's report is counted", count(top).get("count") == 6)

# (a) the owner's words reset the count; a peer's do not
code, out = run(top, sessions, "owner-words", "go on", "--ids", "OPS-1", "--from", "peer")
check("a: a peer's words are refused and the count stays", code != 0 and count(top).get("count") == 6)
code, out = run(top, sessions, "owner-words", "go on", "--ids", "OPS-1", "--from", "owner")
check("a: the owner's words reset the count with no hand reset", code == 0 and count(top).get("count") == 0)

# (c) 15 of 20: one line, once
for _ in range(15):
    run(top, unattended, "sends", "add", "w")
probe = ("import sys; sys.path.insert(0, %r); import unattended; print(unattended.lines()[1])" % scripts.replace("\\", "/"))
first = subprocess.run([sys.executable, "-c", probe], cwd=top, capture_output=True, text=True).stdout
second = subprocess.run([sys.executable, "-c", probe], cwd=top, capture_output=True, text=True).stdout
check("c: at 15 of 20 the check-in carries one line with the projected time the cap runs out", "Send cap near" in first and "runs out about" in first)
check("c: it is printed once", "Send cap near" not in second)
run(top, unattended, "sends", "reset")
check("c: a reset starts the count and the warning again", "SENDS 0 of 20" in run(top, unattended, "sends")[1] and not count(top).get("warned"))

# (d) a worker comes only from a free session
with open(os.path.join(loop, "runs", "d.json"), "w") as handle:
    json.dump({"slug": "d", "status": "queued", "worker": "", "worktree": top}, handle)
before = len(calls())
code, out = run(top, sessions, "assign", "d", **tool)
check("d: with no free session a new one is refused with the reason", code == 1 and out.startswith("REFUSED d:") and "owner's typing" in out)
check("d: the tool was never asked to start a session", not any(x.startswith("start") for x in calls()[before:]) and len(calls()) == before)
with open(os.path.join(loop, "session-pool.json")) as handle:
    pool = json.load(handle)
pool["s9"] = {"name": "worker \u00b7 old", "slug": "old", "state": "free"}
with open(os.path.join(loop, "session-pool.json"), "w") as handle:
    json.dump(pool, handle)
code, out = run(top, sessions, "assign", "d", **tool)
check("d: a free (archived) session is woken, renamed and sent the goal", code == 0 and any(x.startswith("rename s9") for x in calls()) and any(x.startswith("send s9") for x in calls()))

# (e) no larger than main, under the package gate (LF bytes)
for path in (unattended, sessions):
    with open(path, "rb") as handle:
        size = len(handle.read().replace(b"\r\n", b"\n"))
    old = subprocess.run(["git", "show", "origin/main:" + os.path.relpath(path, root).replace("\\", "/")], cwd=root, capture_output=True)
    limit = len(old.stdout.replace(b"\r\n", b"\n")) if old.returncode == 0 and old.stdout else 20000
    check("e: %s is %d bytes, no larger than main (%d) and under 20,000" % (os.path.basename(path), size, limit), size <= min(limit, 20000))

check("hermetic: the checkout's own .git/loop/operation.id is byte-identical before and after this toy", real_id_hash() == REAL_BEFORE)
print("PLATFORM LIMITS TOY " + ("OK" if not fails else "FAILED %d" % fails))
sys.exit(1 if fails else 0)
