#!/bin/bash
# reads: skills/workflow-delivery/scripts/planwait.py skills/workflow-delivery/scripts/flow.py skills/workflow-delivery/scripts/fit.py
# DEL-22.3: a finished plan reply is NOT handed on (no NEXT line) while the level's reviews are still running inside their time limit; it is handed on
# once they finish. The stand-in planner finishes at once; the stand-in review waits for a release file. Own temp HOME; stand-ins only. usage: test-plan-hold.sh
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION CLAUDE_CODE_HOST_SESSION_ID CLAUDE_CODE_SESSION_ID CLAUDE_SESSION_ID LOOP_POD_ID
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) USERPROFILE="$HOME"
export TMPDIR="$HOME/tmp"; mkdir -p "$TMPDIR"
export LOOP_PRIVATE_NAMES=/dev/null
d=$(mktemp -d)
toy_on_exit 'rm -rf "$HOME" "$d"'
"$here/dev/toy/make.sh" "$d" || exit 1
S="$here/skills/workflow-delivery/scripts"
goal="python3 $S/goal.py"; F="python3 $S/flow.py"
export PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh"
cd "$d/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
git clone -q . "$d/up"; git remote set-url origin "$d/up"; git fetch -q origin  # origin is a non-bare local clone: nothing is sent anywhere
up() { git -C "$d/up" fetch -q "$d/repo" "$1" && git -C "$d/up" merge -q --ff-only FETCH_HEAD && git fetch -q origin; }
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
R="$(cd "$(git rev-parse --git-common-dir)" && pwd)/loop/runs"
export FAKE_DIR="$d"
python3 - "$d" <<'PY'
import json, sys
d = sys.argv[1]
c = json.load(open(".loop/config.json"))
c["plan_levels"] = {"small": {"needs": ["eng"], "minutes": 10}, "review_command": ["bash", "-c", 'while [ ! -f "$FAKE_DIR/release" ]; do sleep 0.2; done; exit 0']}
json.dump(c, open(".loop/config.json", "w"), indent=2)
json.dump({"command": ["bash", d + "/planner.sh"], "env": {"FAKE_MODE": "unattended"}, "probe": ["bash", "-c", "echo $FAKE_MODE"], "probe_expect": "unattended",
           "steps": {s: "stand-in-" + s for s in ("idea", "plan", "review", "qa", "ship")}}, open(d + "/flow.json", "w"))
PY
git add -A; git commit -qm "plan settings"; up main
printf '#!/bin/bash\nsleep 3\nprintf "PLAN: the plan\\nDEPTH: full\\nSTEP: done\\n"\n' > "$d/planner.sh"
export LOOP_FLOW="$d/flow.json"
git switch -q -c loop/hold; $goal new hold --here --goal "Change calc" --done "calc adds" --touches calc.py >/dev/null || { echo "FAIL: could not freeze the goal"; exit 1; }
$F hold idea --wait 20 >/dev/null; $goal record hold idea --file "$R/hold.idea.txt" >/dev/null
# calls while the review waits for its release file: the planner ends MID-WAIT of one call (it sleeps 3 s, each call waits 2 s), and no call may print NEXT
early=""
for _ in 1 2 3 4 5 6; do early="$early$($F hold plan --wait 2 2>&1)"; done
check "while the review is still running, the finished plan reply is not handed on (no NEXT line)" '! grep -q "^NEXT:" <<<"$early"'
check "the call says the reviews are still running and to run the same command again" 'grep -q "reviews are still running" <<<"$early"'
: > "$d/release"
for _ in $(seq 60); do [ -f "$R/hold.plan-reviews.json" ] && break; sleep 0.2; done
late=""
for _ in 1 2 3 4; do late=$($F hold plan --wait 8 2>&1); grep -q "^NEXT:" <<<"$late" && break; done
check "control: once the review has finished, the same call hands the reply on (NEXT)" 'grep -q "^NEXT:" <<<"$late"'
# a check that cannot run holds: an unexpected error inside the hold prints RUNNING and returns held, and a step other than plan is never held
exc=$(python3 - "$S" <<'PY'
import os, sys, tempfile, types
sys.path.insert(0, sys.argv[1])
import fit
job = tempfile.mkstemp(dir=os.environ["TMPDIR"], suffix=".job")[1]
print(fit.plan_hold(types.SimpleNamespace(step="plan"), "r", "r/x.txt", job), fit.plan_hold(types.SimpleNamespace(step="qa"), "r", "r/x.txt", job))
PY
)
check "an unexpected error inside the hold holds (RUNNING, held) instead of handing on" '[ "${exc#*$'"'"'\n'"'"'}" = "True False" ] && grep -q "^RUNNING" <<<"$exc"'
[ "$fails" = 0 ] && echo "ALL PASS" || echo "$fails FAILED"
[ "$fails" = 0 ]
