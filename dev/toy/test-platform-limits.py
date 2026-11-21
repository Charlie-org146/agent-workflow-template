#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/unattended.py skills/workflow-monitoring/scripts/sessions.py
"""OPS-1: the platform limits are counted before they are reached. In a throwaway git repo with a fake session tool: every
send is counted with its time and the owner's words reset the count (a peer's do not); one event is one message per distinct
worker session; at 15 of 20 the check-in says when the cap runs out, once; a worker comes only from a free (archived)
session and a new one is refused; both scripts stay no larger than main and under the package gate."""
import atexit
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-monitoring", "scripts")
unattended, sessions = os.path.join(scripts, "unattended.py"), os.path.join(scripts, "sessions.py")
fails = 0
DROP_PREFIXES = ("LOOP_", "CLAUDE", "ANTHROPIC")
DROP_NAMES = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
              "GIT_CONFIG_GLOBAL", "GIT_CONFIG_COUNT", "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE", "GIT_TEMPLATE_DIR", "XDG_CONFIG_HOME", "PYTHONSTARTUP", "GIT_CONFIG_PARAMETERS", "GIT_PREFIX")
DROP_PREFIXES = DROP_PREFIXES + ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
REAL_HOME = os.path.realpath(os.path.expanduser("~"))  # before any HOME swap: cleanup() must never remove it
THROWAWAY = tempfile.mkdtemp(prefix="limits-toy-")  # one mkdtemp area for the home, the fixture and the decoy; cleanup() removes only this
HOME = os.path.join(THROWAWAY, "home")
os.makedirs(HOME)


def clean_env(**more):
    """The environment every subprocess of this toy gets: no host session or loop setting, no git location variable, a throwaway HOME."""
    keep = {k: v for k, v in os.environ.items() if not k.startswith(DROP_PREFIXES) and k not in DROP_NAMES}
    keep.update(HOME=HOME, USERPROFILE=HOME, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    keep.update(more)
    return keep


def real_id_hash():
    """Hash of the checkout's own .git/loop/operation.id; never its contents. One id per line (the format govern_hook.operation_ids reads).
    A failed git discovery or an unreadable file is "unverified:..." (a FAIL line), only a missing file at a discovered path is "absent"."""
    done = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"], capture_output=True, text=True, env=clean_env())
    out = done.stdout.strip()
    if done.returncode != 0 or not out:
        return "unverified:discovery"
    path = os.path.join(os.path.abspath(os.path.join(root, out)), "loop", "operation.id")
    if not os.path.lexists(path):
        return "absent"
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return "unverified:unreadable"


REAL_BEFORE = real_id_hash()


def cleanup():
    """Remove the one directory this toy created, and only that: it must lie under the real temp directory and be neither HOME nor the cwd."""
    try:
        target = os.path.realpath(THROWAWAY)
        temp = os.path.realpath(tempfile.gettempdir())
        if target.startswith(temp + os.sep) and target not in (REAL_HOME, os.path.realpath(os.getcwd())):
            shutil.rmtree(target, ignore_errors=True)
    except OSError:
        pass


atexit.register(cleanup)


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def run(top, script, *args, **env):
    # hermetic: clean_env() (no host session or loop setting, a throwaway HOME so the owner's ~/.claude.json and ~/.workflow-loop are never read)
    done = subprocess.run([sys.executable, script] + list(args), cwd=top, capture_output=True, text=True, env=clean_env(**env))
    return done.returncode, done.stdout + done.stderr


def count(top):
    try:
        with open(os.path.join(top, ".git", "loop", "sends.json")) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def repo(name):
    """A disposable repository under the throwaway directory, built with clean_env() so nothing inherited names another repository."""
    path = os.path.join(THROWAWAY, name)
    os.makedirs(path)
    subprocess.run(["git", "init", "-q", "-b", "main", "--template="], cwd=path, capture_output=True, env=clean_env())
    os.makedirs(os.path.join(path, ".git", "loop", "runs"))
    os.makedirs(os.path.join(path, ".loop"))
    with open(os.path.join(path, ".loop", "config.json"), "w") as handle:
        json.dump({"base": "main"}, handle)
    return path


top = repo("top")
loop = os.path.join(top, ".git", "loop")
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
first = subprocess.run([sys.executable, "-c", probe], cwd=top, capture_output=True, text=True, env=clean_env()).stdout
second = subprocess.run([sys.executable, "-c", probe], cwd=top, capture_output=True, text=True, env=clean_env()).stdout
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
    old = subprocess.run(["git", "show", "origin/main:" + os.path.relpath(path, root).replace("\\", "/")], cwd=root, capture_output=True, env=clean_env())
    if old.returncode != 0 or not old.stdout:
        print("NOTE: no baseline for %s on origin/main (git show exit %d): the 20,000-byte gate alone applies" % (os.path.basename(path), old.returncode))
    limit = len(old.stdout.replace(b"\r\n", b"\n")) if old.returncode == 0 and old.stdout else 20000
    check("e: %s is %d bytes, no larger than main (%d) and under 20,000" % (os.path.basename(path), size, limit), size <= min(limit, 20000))

# control: a host session variable put back in the parent environment does not reach the fixture, and the real operation.id stays as it was
decoy = repo("decoy")
before = count(top).get("count") or 0
os.environ["CLAUDE_CODE_HOST_SESSION_ID"] = "host-probe"
os.environ["GIT_DIR"] = os.path.join(decoy, ".git")  # a disposable repository: a scrub regression must never be able to write the checkout's own state
try:
    run(top, unattended, "sends", "add", "w")
finally:
    os.environ.pop("CLAUDE_CODE_HOST_SESSION_ID", None)
    os.environ.pop("GIT_DIR", None)
check("control: with a host session id and GIT_DIR in the environment the fixture still counts its send", count(top).get("count") == before + 1 and not count(decoy))
check("control: and the checkout's own operation.id is unchanged", real_id_hash() == REAL_BEFORE)

# control (#5700 redirect): with the parent GIT_DIR naming a second valid repository, the scrubbed call counts in its own repository and leaves the
# decoy alone; the same command without the scrub lands its send in the decoy, which is the cross-repository write the scrub prevents
top_n, decoy_n = count(top).get("count"), count(decoy).get("count") or 0
os.environ["GIT_DIR"] = os.path.join(decoy, ".git")
try:
    run(top, unattended, "sends", "add", "w")
    scrubbed_top, scrubbed_decoy = count(top).get("count"), count(decoy).get("count") or 0
    direct_env = clean_env(GIT_DIR=os.path.join(decoy, ".git"))
    subprocess.run([sys.executable, unattended, "sends", "add", "w"], cwd=top, capture_output=True, text=True, env=direct_env)
finally:
    os.environ.pop("GIT_DIR", None)
check("control: with GIT_DIR naming another repository, the scrubbed call counts in its own repository and leaves the other alone", scrubbed_top == top_n + 1 and scrubbed_decoy == decoy_n)
check("control: the same call without the scrub lands its send in the other repository and not its own", (count(decoy).get("count") or 0) == decoy_n + 1 and count(top).get("count") == top_n + 1)

# control: one canary per scrubbed family in the parent environment; a child of clean_env() prints only booleans and sees none of them
canaries = ("CLAUDE_TOY_CANARY", "ANTHROPIC_TOY_CANARY", "LOOP_TOY_CANARY", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG_GLOBAL", "GIT_TEMPLATE_DIR", "XDG_CONFIG_HOME", "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE", "GIT_CONFIG_KEY_0", "PYTHONSTARTUP")
for name in canaries:
    os.environ[name] = "canary"
try:
    seen = subprocess.run([sys.executable, "-c", "import os; print(any(os.environ.get(k) == 'canary' for k in %r))" % (canaries,)], capture_output=True, text=True, env=clean_env()).stdout.strip()
    leaked = subprocess.run([sys.executable, "-c", "import os; print(any(os.environ.get(k) == 'canary' for k in %r))" % (canaries,)], capture_output=True, text=True).stdout.strip()
finally:
    for name in canaries:
        os.environ.pop(name, None)
check("control: no canary variable of a scrubbed family reaches a child of the scrubbed environment", seen == "False")
check("control: negative: the same child without the scrub does see them", leaked == "True")

check("hermetic: the checkout's own .git/loop/operation.id is byte-identical before and after this toy (%s)" % ("verified" if not REAL_BEFORE.startswith("unverified") else REAL_BEFORE), not REAL_BEFORE.startswith("unverified") and real_id_hash() == REAL_BEFORE)

# cleanup: only the directory this toy made, then asserted gone (counted before the tally)
home_dir, throwaway_dir = HOME, THROWAWAY
os.chdir(tempfile.gettempdir())
cleanup()
check("cleanup: the throwaway HOME is gone", not os.path.lexists(home_dir))
check("cleanup: the fixture repositories are gone", not os.path.lexists(throwaway_dir))
print("PLATFORM LIMITS TOY " + ("OK" if not fails else "FAILED %d" % fails))
sys.exit(1 if fails else 0)
