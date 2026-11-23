#!/usr/bin/env python3
# reads: skills/steps.py skills/workflow-delivery/scripts/goal.py skills/workflow-release/scripts/release.py
# reads: skills/workflow-monitoring/scripts/sessions.py skills/workflow-monitoring/scripts/board_log.py
# reads: skills/workflow-docs/scripts/steps_page.py skills/workflow-release/scripts/autorelease.py
# windows: skip (fcntl)
"""DEL-19 (v110-fast-steps-2), part 3 of 3: the save refuses a lock held too long and a record it cannot read, discovery of records fails
loudly, the step list never rewrites a flow-file key, a stop does not change the budget's numbers, a release through CI is its own row.
`CASE <name> PASS|FAIL` per case. usage: test-steps-safe.py"""
import datetime
import fcntl
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SKILLS = os.path.join(ROOT, "skills")
sys.path[:0] = [SKILLS] + [os.path.join(SKILLS, d, "scripts") for d in ("workflow-monitoring", "workflow-release", "workflow-docs")]
steps, board_log = importlib.import_module("steps"), importlib.import_module("board_log")
failed, made = [], []


def case(name, ok, why=""):
    print("CASE %s %s%s" % (name, "PASS" if ok else "FAIL", "" if ok else ": " + why))
    ok or failed.append(name)


def repo():
    path = tempfile.mkdtemp()
    made.append(path)
    subprocess.run(["git", "init", "-q", path], capture_output=True)
    os.makedirs(os.path.join(path, ".git", "loop", "runs"))
    return path


def save(mod, root, extra="", env=None, hold=None):
    """One real save by the writer `mod` of record hk in `root` (a throwaway repo); the finished process."""
    scripts = {"goal": "workflow-delivery", "release": "workflow-release", "sessions": "workflow-monitoring"}[mod]
    code = "import sys; sys.path.insert(0, %r); import %s as w; st = {'slug': 'hk', 'step': 'build', 'status': 'running', 'log': []}; w.save(st, 'one')" \
           % (os.path.join(SKILLS, scripts, "scripts"), mod)
    keep = {k: v for k, v in os.environ.items() if k in ("PATH", "LANG")}
    run = dict(keep, HOME=root, USERPROFILE=root, LOOP_PRIVATE_NAMES="/dev/null", LOOP_ROLE="worker", STEPS_LOCK_WAIT="1", **(env or {}))
    try:
        return subprocess.run([sys.executable, "-B", "-c", code], cwd=root, capture_output=True, text=True, env=run, timeout=20)
    except subprocess.TimeoutExpired:
        return None


path = lambda root: os.path.join(root, ".git", "loop", "runs", "hk.json")
for mod in ("goal", "release", "sessions"):
    root = repo()
    with open(path(root) + ".lock", "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX)
        done = save(mod, root)
    case("lock-%s-times-out-and-refuses" % mod, done is not None and done.returncode != 0 and "LOCK_TIMEOUT" in done.stderr and not os.path.exists(path(root)), str(done and done.stderr[-200:]))
    root = repo()
    open(path(root), "w").write('{"slug": "hk", "step": "bui')
    done = save(mod, root)
    case("unreadable-record-is-refused-by-%s" % mod, done is not None and done.returncode != 0 and "RECORD_UNREADABLE" in done.stderr
         and open(path(root)).read() == '{"slug": "hk", "step": "bui', str(done and done.stderr[-200:]))
tmp = path(repo())
case("update-refuses-an-unreadable-record-and-reports-a-missing-one", steps.update(tmp, lambda r: None) is False, "missing")
refusals = []
for text in ("[1, 2]", "{"):  # valid JSON that is not a record, and a record cut short
    open(tmp, "w").write(text)
    try:
        steps.update(tmp, lambda r: None)
        refusals.append(False)
    except SystemExit as stop:
        refusals.append("RECORD_UNREADABLE" in str(stop) and open(tmp).read() == text)
case("update-refuses-a-record-that-is-not-a-record", refusals == [True, True], str(refusals))

# discovery of records: a repository git cannot find fails; a folder with no records is a valid empty store
sp = importlib.import_module("steps_page")
outside = tempfile.mkdtemp()
made.append(outside)
try:
    sp.records(outside)
    found = "returned"
except SystemExit as stop:
    found = str(stop)
case("records-fails-where-git-finds-no-repository", "DISCOVERY_FAILED" in found, found)
empty = repo()
shutil.rmtree(os.path.join(empty, ".git", "loop"))
case("records-of-a-repository-with-none-is-empty", sp.records(empty) == {}, "")
root = repo()
open(os.path.join(root, ".git", "loop", "runs", "bad.json"), "w").write("{")
try:
    sp.records(root)
    found = "returned"
except SystemExit as stop:
    found = str(stop)
case("records-fails-on-an-unreadable-record", "RECORD_UNREADABLE" in found, found)

# flow-file keys and lane names are command arguments: say() keeps them
keep = ["review: full_markers for review in the flow file is not a list", "a full_markers string for qa is missing", "the qa lane has not passed"]
case("say-keeps-flow-file-keys-and-lane-names", [steps.say(t) for t in keep] == keep, str([steps.say(t) for t in keep]))

# a stop does not change the budget's numbers: the telemetry lines never sit between a stopped entry and the entry that resumes it
rec = {"step": "plan", "status": "running", "log": ["2026-11-22T10:00:00Z start idea", "2026-11-22T10:10:00Z idea done", "2026-11-22T10:20:00Z start plan"]}
steps.transition({}, rec, "2026-11-22T10:20:00Z")
old = json.loads(json.dumps(rec))
rec.update(status="stopped")
rec["log"].append("2026-11-22T10:40:00Z stopped: waiting")
steps.transition(old, rec, "2026-11-22T10:40:00Z")
rec.update(status="running")
rec["log"].append("2026-11-22T11:20:00Z resumed")
bare = [l for l in rec["log"] if " began " not in l and " end " not in l]
at = datetime.datetime(2026, 11, 22, 11, 30, tzinfo=datetime.timezone.utc)
ours = board_log.flow_seconds(dict(rec, status="running"), at)
case("a-stop-leaves-the-budget-numbers-alone", ours == board_log.flow_seconds({"log": bare, "status": "running", "step": "plan"}, at) and bool(ours), str((ours, rec["log"])))

# the merge queue: the release is CI's, and its row is the release row, not a second merge
ar = importlib.import_module("autorelease")
root = repo()
saved = {}
ar.release = type("R", (), {"save": staticmethod(lambda state, note=None: (state.setdefault("log", []).append("2026-11-22T12:00:00Z " + note) if note else None, steps.commit(path(root), state, "2026-11-22T12:00:00Z")))})
st = {"slug": "hk", "step": "pr", "status": "done", "release": "merged", "pr": "x", "log": [], "release_part": "patch"}
ar.finish(root, {"merge_queue": True}, st)
rows = {r["step"]: r for r in steps.entries(st)}
case("a-release-through-ci-records-the-release-row", rows["release"]["state"] == "ran" and rows["after the merge"]["state"] == "ran" and rows["merge"]["attempts"] == 0, str(rows["release"]) + str(rows["merge"]))


# owner-facing lines say the list's step names: the watcher's status, asks and needs, the free refusal, the notices, the done-run report
root = tempfile.mkdtemp()
made.append(root)
env = {"PATH": os.environ["PATH"], "HOME": root, "LOOP_PRIVATE_NAMES": "/dev/null", "LOOP_ROLE": "worker", "LANG": "en_US.UTF-8"}
git = lambda *a: subprocess.run(["git", *a], cwd=root, check=True, capture_output=True, env=env)
git("init", "-q"), git("config", "user.email", "t@t.t"), git("config", "user.name", "t"), open(os.path.join(root, "f"), "w").write("x"), git("add", "."), git("commit", "-qm", "i")
subprocess.run([sys.executable, "-B", os.path.join(SKILLS, "workflow-setup", "scripts", "setup.py"), "--bare"], cwd=root, check=True, capture_output=True, env=env)
runs = os.path.join(root, ".git", "loop", "runs")
os.makedirs(runs, exist_ok=True)
for slug, more in (("ff", {"status": "failed", "finding": "Failed 3 tries. Last: review failed: boom"}),
                   ("ww", {"status": "waiting", "waiting": {"ask": "review left this for you: approve", "words": ["go"]}})):
    json.dump(dict({"slug": slug, "goal": "g", "step": "review", "worker": "session", "pid": None, "updated": "2026-11-22T10:00:00Z", "log": []}, **more), open(os.path.join(runs, slug + ".json"), "w"))
mon = os.path.join(SKILLS, "workflow-monitoring", "scripts")
free = subprocess.run([sys.executable, "-B", os.path.join(mon, "sessions.py"), "free", "ww"], cwd=root, capture_output=True, text=True, env=env)
watch = subprocess.run([sys.executable, "-B", os.path.join(mon, "watch.py"), "watch", "--once"], cwd=root, capture_output=True, text=True, env=env, timeout=120).stdout
notice = " ".join(str(e) for e in importlib.import_module("notify").events(root, ""))
shown = importlib.import_module("live_board").next_line({"status": "done", "report": {"text": "worker x: step ship done"}})
seen = [free.stderr + free.stdout, watch, notice, shown]
case("owner-facing-lines-say-the-list-names", all(w in " ".join(seen) for w in ("(tests left this for you", "WAITS ON YOU ww: tests left", "NEEDS YOU ff: Failed 3 tries. Last: tests failed", "ff failed step=tests", "step tests done"))
     and not any(w in " ".join(seen) for w in ("review left", "review failed", "step=review", "step ship")), str(seen)[:600])

for folder in made:
    shutil.rmtree(folder, ignore_errors=True)
print("ALL PASS" if not failed else "FAILED: %s" % ", ".join(failed))
sys.exit(1 if failed else 0)
