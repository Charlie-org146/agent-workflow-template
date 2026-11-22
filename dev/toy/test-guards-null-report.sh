#!/bin/bash
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/guards.py skills/workflow-monitoring/scripts/worker.py
# reads: skills/workflow-monitoring/scripts/mend.py
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
check() { if eval "$2"; then ok "$1"; else bad "$1"; [ -z "${DEBUG:-}" ] || printf "%s\n" "$out" | head -8; fi; }
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
echo "== no new file under skills/"
base=$(git -C "$here" merge-base HEAD origin/main 2>/dev/null || git -C "$here" rev-parse HEAD)
out=$(git -C "$here" diff --diff-filter=A --name-only "$base" HEAD -- skills)
# owner o790: the one file o788 allows may be added; o719 and TD721: brief.py is the implementation's file (o718/o719); any other new skills/ file still fails
ALLOWED=$(printf "%s\n%s" skills/workflow-monitoring/scripts/board_tasks.py skills/workflow-release/scripts/brief.py)
check "this change adds no file under skills/ except board_tasks.py (o790) and brief.py (o719)" '[ -z "$(grep -vxF "$ALLOWED" <<<"$out")" ]'
out=$(printf "%s\n%s\n%s\n" skills/workflow-monitoring/scripts/board_tasks.py skills/workflow-release/scripts/brief.py skills/x/scripts/other.py)
check "negative control: a second new skills/ file still fails" '! [ -z "$(grep -vxF "$ALLOWED" <<<"$out")" ] && [ -n "$out" ]'
# full-auto-no-new-file admits exactly brief.py (o718, o719; TD1093): the row's own command on a toy repo
rowcmd=$(awk -F'\t' '$1 == "full-auto-no-new-file" {print $3}' "$here/.loop/regression.tsv")
nf="$T/nofile"; mkdir -p "$nf"; git -C "$nf" init -q -b main; git -C "$nf" config user.email t@example.test; git -C "$nf" config user.name Toy
mkdir -p "$nf/skills/workflow-release/scripts"; echo x > "$nf/f"; git -C "$nf" add -A; git -C "$nf" commit -qm base; git -C "$nf" switch -qc topic
rowis() { ( cd "$nf" && bash -c "$rowcmd" ) >/dev/null 2>&1; }
echo 1 > "$nf/skills/workflow-release/scripts/brief.py"; git -C "$nf" add -A; git -C "$nf" commit -qm "brief"
rowis && echo "PASS: the row admits brief.py" || { echo "FAIL: the row admits brief.py"; fails=$((fails+1)); }
echo 1 > "$nf/skills/workflow-release/scripts/other.py"; git -C "$nf" add -A; git -C "$nf" commit -qm "other"
rowis && { echo "FAIL: negative control: the row passes another new skills file"; fails=$((fails+1)); } || echo "PASS: negative control: another new skills file still fails the row"
git -C "$nf" reset -q --hard HEAD~1; echo '{}' > "$nf/listing.json"; git -C "$nf" add -A; git -C "$nf" commit -qm "listing"
rowis && { echo "FAIL: negative control: the row passes a new listing.json"; fails=$((fails+1)); } || echo "PASS: negative control: a new listing.json still fails the row"
fi
[ "$fails" = 0 ] && echo "ALL PASS" || echo "$fails FAILED"
[ "$fails" = 0 ]
