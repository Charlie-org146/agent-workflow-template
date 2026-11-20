#!/bin/bash
# reads: skills/workflow-monitoring/scripts/ skills/workflow-setup/scripts/setup.py
# Proves the board and the check-in survive a run record with one aware and one zone-less stamp: neither crashes (it was
# "can't subtract offset-naive and offset-aware datetimes" in board_log.flow_seconds), and the zone-less stamp is named in
# both outputs, never given a guessed zone. A stamp that is not a time is named the same way. No model is called.
# usage: test-board-tz.sh [DIR]
set -u
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID
unset LOOP_ROLE LOOP_SESSION LOOP_SESSION_TOOL LOOP_OPERATION_SESSION
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
T=${1:-$(mktemp -d)}; rm -rf "${T:?}"; mkdir -p "$T"
S="$here/skills/workflow-monitoring/scripts"
export HOME="$T/home" LOOP_BOARD_HEALTH=green PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$T/gh"; mkdir -p "$HOME"
export USERPROFILE="$HOME"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
"$here/dev/toy/make.sh" "$T" >/dev/null || exit 1
cd "$T/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
C=$(cd "$(git rev-parse --git-common-dir)" && pwd); R="$C/loop/runs"; mkdir -p "$R"
NOW=$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"))')
python3 - "$R" "$NOW" <<'PY'
import json, os, sys
runs, now = sys.argv[1:3]
def write(slug, log):
    json.dump({"slug": slug, "goal": "Goal " + slug, "status": "running", "step": "build", "tries": 0, "pr": "", "waits_on": [],
               "updated": now + "Z", "log": log, "pid": os.getpid()}, open(os.path.join(runs, slug + ".json"), "w"))
write("mixed", [now + "Z start idea", now + " start build"])     # one aware stamp, one with no zone
write("junk", [now + "Z start idea", "notatime start build"])    # a stamp that is not a time
PY
python3 "$S/board.py" board > "$T/board.out" 2> "$T/board.err"; echo "exit $?" >> "$T/board.err"
python3 "$S/checkin.py" > "$T/checkin.out" 2> "$T/checkin.err"; echo "exit $?" >> "$T/checkin.err"
echo "== a zone-less stamp beside an aware one"
check "board.py board does not crash on one zone-less and one aware stamp" 'grep -qx "exit 0" "$T/board.err" && ! grep -q "offset-naive" "$T/board.err"'
check "checkin.py does not crash on one zone-less and one aware stamp" 'grep -qx "exit 0" "$T/checkin.err" && ! grep -q "offset-naive" "$T/checkin.err"'
echo "== a stamp that cannot be read as aware is named"
check "board.py board names the zone-less stamp, with the reason" 'grep -qx "UNREAD stamp not read (no time zone): $NOW" "$T/board.out"'
check "checkin.py names the zone-less stamp, with the reason" 'grep -qx -- "- stamp not read (no time zone): $NOW" "$T/checkin.out"'
check "board.py board names a stamp that is not a time" 'grep -qx "UNREAD stamp not read (not a time): notatime" "$T/board.out"'
check "no zone is guessed: the zone-less stamp counts no time toward a step" 'python3 - "$S" "$NOW" <<PY
import sys, datetime
sys.path.insert(0, sys.argv[1]); import board_log as bl
at = datetime.datetime.now(datetime.timezone.utc)
print(bl.flow_seconds({"status": "running", "step": "build", "log": [sys.argv[2] + " start build"]}, at))
sys.exit(0 if bl.stamp(sys.argv[2]) is None else 1)
PY'
[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
