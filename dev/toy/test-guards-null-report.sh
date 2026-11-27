#!/bin/bash
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/guards.py skills/workflow-monitoring/scripts/worker.py
# reads: skills/workflow-monitoring/scripts/mend.py dev/toy/hist.py skills/workflow-delivery/scripts/dlf.py
# History codes, each printed with its fix (dev/toy/hist.py): HIST-E01 the base ref is missing; HIST-E02 the history is shallow;
# HIST-E03 a git command failed; HIST-E04 a fixture could not be built. A history that can't be read fails this test.
# A goal reset never writes a null report, and goal.py's state file is written under a lock so two writers lose neither
# write. A temp repo, no model, no network. usage: test-guards-null-report.sh [reset|writers|fresh|nofiles ...]   (default all)
set -u
unset LOOP_ROLE CLAUDE_SESSION_ID LOOP_POD_ID
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
S=${GNR_SKILLS:-$here/skills}
cases=("$@"); [ ${#cases[@]} = 0 ] && cases=(reset writers fresh nofiles)
want() { for c in "${cases[@]}"; do [ "$c" = "$1" ] && return 0; done; return 1; }
T=$(mktemp -d); fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; [ -z "${DEBUG:-}" ] || printf "%s\n" "$out" | head -8 | python3 "$here/dev/toy/hist.py" redact; fi; }
r() { out=$(eval "$@" 2>&1); rc=$?; }
if want reset; then
echo "== a reset leaves report as an empty record"
r "python3 - $S/workflow-delivery/scripts <<'PY'
import sys; sys.path.insert(0, sys.argv[1]); import guards
s = {'slug': 'g', 'status': 'failed', 'report': {'text': 'x'}}
guards.revive(s, 'resume', 'operation', 'why')
print('REPORT', repr(s['report']))
PY"
check "guards.revive (goal.py resume) writes {} not None" 'grep -q "REPORT {}" <<<"$out"'
out=$(grep -rn 'report=None' "$S"/*/scripts/*.py; grep -n '"running", None' "$S/workflow-monitoring/scripts/mend.py")
check "the bind and mend resets write no null report either" '[ -z "$out" ]'
fi
if want writers; then
echo "== two concurrent writers lose neither write"
git init -q -b main "$T/repo"; mkdir -p "$T/repo/.git/loop/runs"
echo '{"slug":"g","status":"running","step":"build","tries":0,"log":["start"]}' > "$T/repo/.git/loop/runs/g.json"
writer() { ( cd "$T/repo" && python3 - "$S/workflow-delivery/scripts" "$1" "$2" <<'PY'
import sys, time; sys.path.insert(0, sys.argv[1]); import goal
state = goal.load("g")
time.sleep(1.0)  # both writers hold the same older copy before either saves
state[sys.argv[2]] = "mine"
goal.save(state, "note " + sys.argv[2])
PY
) ; }
writer alpha alpha & writer beta beta & wait
out=$(cat "$T/repo/.git/loop/runs/g.json")
check "both writers' fields and both log lines are in the file" 'python3 -c "
import json; d = json.load(open(\"$T/repo/.git/loop/runs/g.json\"))
assert d[\"alpha\"] == \"mine\" and d[\"beta\"] == \"mine\", d
assert sum(\"note alpha\" in l for l in d[\"log\"]) == 1 and sum(\"note beta\" in l for l in d[\"log\"]) == 1, d[\"log\"]
assert d[\"log\"][0] == \"start\""'
check "the file is valid JSON and no temp file is left" 'python3 -c "import json;json.load(open(\"$T/repo/.git/loop/runs/g.json\"))" && [ -z "$(ls $T/repo/.git/loop/runs | grep tmp)" ]'
( cd "$T/repo" && python3 - "$S/workflow-delivery/scripts" <<'PY' )
import sys; sys.path.insert(0, sys.argv[1]); import goal
state = goal.load("g"); state["held_at"] = "x"; goal.save(state); state.pop("held_at"); goal.save(state)
PY
out=""; check "a key a writer removes stays removed (bind clears held_at)" 'python3 -c "
import json; d = json.load(open(\"$T/repo/.git/loop/runs/g.json\")); assert \"held_at\" not in d, d"'
for i in 1 2 3 4 5 6; do ( cd "$T/repo" && python3 - "$S/workflow-delivery/scripts" "k$i" <<'PY' ) & done; wait
import sys; sys.path.insert(0, sys.argv[1]); import goal
state = goal.load("g"); state[sys.argv[2]] = 1; goal.save(state, "w" + sys.argv[2])
PY
out=""; check "six unsynchronised writers all land" 'python3 -c "
import json; d = json.load(open(\"$T/repo/.git/loop/runs/g.json\"))
assert all(d.get(\"k%d\" % i) == 1 for i in range(1, 7)), d"'
fi
if want fresh; then
echo "== a record made in this process is written whole"
git init -q -b main "$T/fresh"; mkdir -p "$T/fresh/.git/loop/runs"
( cd "$T/fresh" && python3 - "$S/workflow-delivery/scripts" <<'PY' )
import sys; sys.path.insert(0, sys.argv[1]); import goal
goal.save({"slug": "n", "status": "running", "flow": {}, "waiting": None, "log": [], "tries": 0})
PY
out=""; check "empty and null values of a new record are kept (flow {}, waiting null)" 'python3 -c "
import json; d = json.load(open(\"$T/fresh/.git/loop/runs/n.json\")); assert d[\"flow\"] == {} and \"waiting\" in d and d[\"tries\"] == 0, d"'
fi
if want nofiles; then
echo "== no new file under skills/ from the two merges this row guards"
# o863, TD1194: the row reads the change it was written for and v110-tasks' own merge, each against its first parent on origin/main;
# GRD-21's package cap (200 files) stays in force.
ALLOWED=skills/workflow-monitoring/scripts/board_tasks.py
HIST=$here/dev/toy/hist.py
unread() { printf '%s\n' "${1:-FAILED: a history could not be read}"; exit 1; }  # $1 is the code's line; last, since the row shows one
added_by() {  # $1 repo, $2 branch name: the skills files added by the first-parent merge of that branch's pull request on origin/main
  python3 "$HIST" added "$1" "/loop/$2\$"
}
out=$(python3 "$HIST" require "$here") || unread "$out"
out=$(added_by "$here" guards-null-report) || unread "$out"
check "the change this row was written for adds no file under skills/" '[ -z "$out" ]'
out=$(added_by "$here" v110-tasks) || unread "$out"
check "v110-tasks' own merge adds no file under skills/ except board_tasks.py (o790, o863)" '[ -n "$out" ] && [ "$out" != NOMERGE ] && [ -z "$(grep -vxF "$ALLOWED" <<<"$out")" ]'
fgit() {  # a git command that builds the fixture repo $fx
  local said; said=$(python3 "$HIST" fixture "$fx" "$@") || unread "$said"
}
newfx() { fx=$1; mkdir -p "$fx"; fgit init -q -b main .; fgit commit -q --allow-empty -m base; }
newfx "$T/nofiles"
mkmerge() {  # $1 branch, rest: files added under skills/ by its merge
  local b=$1; shift; fgit checkout -q -b "loop/$b" main
  for f in "$@"; do mkdir -p "$fx/$(dirname "$f")"; echo x > "$fx/$f"; done
  fgit add -A; fgit commit -q --allow-empty -m "add $b"; fgit checkout -q main
  fgit merge -q --no-ff -m "Merge pull request #1 from o/loop/$b" "loop/$b"; fgit update-ref refs/remotes/origin/main HEAD
}
mkmerge v110-tasks "$ALLOWED"
out=$(added_by "$fx" v110-tasks) || unread "$out"
check "a fixture of v110-tasks' merge adding only board_tasks.py reads as allowed" '[ "$out" = "$ALLOWED" ]'
mkmerge guards-null-report skills/x/scripts/other.py
out=$(added_by "$fx" guards-null-report) || unread "$out"
check "negative control: a fixture of the row's own change adding a skills file still fails" '[ -n "$out" ] && [ "$out" != NOMERGE ] && [ "$out" = skills/x/scripts/other.py ] && ! [ -z "$(grep -vxF "$ALLOWED" <<<"$out")" ]'
newfx "$T/nofiles2"
mkmerge v110-tasks "$ALLOWED" skills/x/scripts/other2.py
out=$(added_by "$fx" v110-tasks) || unread "$out"
check "negative control: a fixture of v110-tasks' merge adding another skills file still fails" '[ -n "$(grep -vxF "$ALLOWED" <<<"$out")" ]'
fi
[ "$fails" = 0 ] && echo "ALL PASS" || echo "$fails FAILED"
[ "$fails" = 0 ]
