#!/bin/bash
# reads: skills/workflow-monitoring/scripts/ skills/workflow-delivery/scripts/
# Issue 159: worker.py's last save rereads the run record, so a merge recorded from outside while gh answers is kept.
# A stand-in merged() records the merge mid-call. No model or network. usage: test-worker-save.sh [DIR]
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
d=${1:-$(mktemp -d)}; rm -rf "${d:?}"; mkdir -p "$d/repo"; cd "$d/repo" || exit 1
git init -q -b main
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
# Value: protects=#159; fails_when=worker.py saves the record it loaded before asking gh; why_new=defect test; seam=a
# stand-in merged(); no_claim=gh's real timing
mkdir -p .git/loop/runs .git/loop/logs
printf '{"slug": "w", "status": "done", "pr": "https://example.test/pull/1", "log": []}' > .git/loop/runs/w.json
out=$(python3 - "$here/skills/workflow-monitoring/scripts" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1]); import worker
def merged(pr):  # while gh answers, the release step records the merge from outside
    s = json.load(open(".git/loop/runs/w.json")); s.update(report={"status": "merged", "pr": pr, "text": "merged from outside", "at": "x"})
    json.dump(s, open(".git/loop/runs/w.json", "w")); return False
worker.merged = merged; worker.release_step = lambda state: None
class A: slug = "w"; command = ["true"]
worker.cmd_loop(A())
print(json.load(open(".git/loop/runs/w.json"))["report"]["status"])
PY
)
check "worker.py's last save keeps a merge recorded from outside while gh answered (issue 159)" '[ "$(tail -1 <<<"$out")" = merged ]'

# #5350: role.py save and fit.py save merge only the fields they changed, so a budget goal.py set after the load survives.
out=$(python3 - "$here/skills/workflow-delivery/scripts" <<'PY'
import json, os, subprocess, sys, tempfile
d = tempfile.mkdtemp(); os.chdir(d)
subprocess.run(["git", "init", "-q"], check=True)
runs = os.path.join(d, ".git", "loop", "runs"); os.makedirs(runs)
rec = os.path.join(runs, "g.json")
def disk(**more):  # goal.py set, after the worker loaded its record
    s = json.load(open(rec)); s.update(more); json.dump(s, open(rec, "w"))
json.dump({"slug": "g", "step": "idea", "budget_minutes": 240, "log": []}, open(rec, "w"))
sys.path.insert(0, sys.argv[1])
import role, fit
state = role.goal_state(runs, "g"); disk(budget_minutes=360)
state["step"] = "plan"; role.save(rec, state); a = json.load(open(rec))
state = role.goal_state(runs, "g"); disk(budget_minutes=480)
state["step"] = "build"; fit.run_saver(runs)(state, "fit save"); b = json.load(open(rec))
print("OK" if (a["budget_minutes"], a["step"], b["budget_minutes"], b["step"]) == (360, "plan", 480, "build") else "BAD %s %s" % (a, b))
PY
)
check "role.py save and fit.py save keep a budget goal.py set after the worker loaded its record (issue 5350)" '[ "$(tail -1 <<<"$out")" = OK ]'

# #5350: lanekit.hit (a budget hit written by flow.py/lane.py) rereads and writes the record under goal.py's lock, so a budget
# goal.py set while it runs is never lost. A writer process bumps the budget under the lock while hit() records 300 hits.
out=$(python3 - "$here/skills/workflow-delivery/scripts" <<'PY'
import fcntl, json, os, subprocess, sys, tempfile
d = tempfile.mkdtemp(); runs = os.path.join(d, "runs"); os.makedirs(runs)
rec = os.path.join(runs, "g.json")
json.dump({"slug": "g", "budget_minutes": 0, "log": []}, open(rec, "w"))
N = 300
writer = subprocess.Popen([sys.executable, "-c", """
import fcntl, json, os, sys
rec = sys.argv[1]
for _ in range(%d):
    with open(rec + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        s = json.load(open(rec)); s["budget_minutes"] += 1
        json.dump(s, open(rec + ".w", "w")); os.replace(rec + ".w", rec)
""" % N, rec])
sys.path.insert(0, sys.argv[1]); import lanekit
for i in range(N):
    lanekit.hit(runs, "g", "build", "step", 30, "left %d" % i)
writer.wait()
s = json.load(open(rec))
print("OK" if s["budget_minutes"] == N and s["budget_hits"][0]["left"] == "left %d" % (N - 1) else "BAD %s" % s["budget_minutes"])
PY
)
check "lanekit.hit keeps a budget goal.py set while a budget hit is recorded (issue 5350)" '[ "$(tail -1 <<<"$out")" = OK ]'

# #5350: mend.py save rereads the record under the lock and writes only what its caller changed, so a budget goal.py set after
# the caller loaded its (old) state survives, and the caller's own change and log line land.
out=$(python3 - "$here/skills/workflow-monitoring/scripts" <<'PY'
import json, os, subprocess, sys, tempfile
d = tempfile.mkdtemp(); os.chdir(d)
subprocess.run(["git", "init", "-q"], check=True)
runs = os.path.join(d, ".git", "loop", "runs"); os.makedirs(runs)
rec = os.path.join(runs, "g.json")
json.dump({"slug": "g", "status": "running", "budget_minutes": 240, "log": ["a"]}, open(rec, "w"))
sys.path.insert(0, sys.argv[1]); import mend
state = mend.load("g")
s = json.load(open(rec)); s["budget_minutes"] = 360; s["log"].append("b"); json.dump(s, open(rec, "w"))  # goal.py set, after the load
state["status"] = "stopped"; mend.save(state, "mended")
r = json.load(open(rec))
print("OK" if (r["budget_minutes"], r["status"], r["log"][:2], len(r["log"])) == (360, "stopped", ["a", "b"], 3) else "BAD %s" % r)
PY
)
check "mend.py save keeps a budget goal.py set after its caller loaded the record (issue 5350)" '[ "$(tail -1 <<<"$out")" = OK ]'

[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
