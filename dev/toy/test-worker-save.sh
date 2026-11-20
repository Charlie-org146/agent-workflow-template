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


[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
