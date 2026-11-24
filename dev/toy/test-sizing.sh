#!/bin/bash
# reads: skills/workflow-delivery/scripts/ skills/workflow-monitoring/scripts/ skills/workflow-release/scripts/
# reads: skills/workflow-delivery/references/commands.md
# Proves CBS-1.1 to CBS-1.4 and ASZ-1.1 to ASZ-1.3, each with a fixture that breaks only its rule. A toy repo, a bare origin
# and a second clone that plays the base branch; no network, no model. usage: test-sizing.sh [DIR]
set -u
unset LOOP_BATCH LOOP_SESSION_TOOL LOOP_OPERATION_SESSION GH_TOKEN GITHUB_TOKEN _LOOP_LANE_HELD LOOP_LANE_LIMIT
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
T=${1:-$(mktemp -d)}; rm -rf "${T:?}"; mkdir -p "$T"
export HOME="$T/home"; mkdir -p "$HOME"; export USERPROFILE="$HOME"
"$here/dev/toy/make.sh" "$T" >/dev/null
D="$here/skills/workflow-delivery/scripts"; M="$here/skills/workflow-monitoring/scripts"; R="$here/skills/workflow-release/scripts"
git clone -q "$T/origin.git" "$T/admin"; git -C "$T/admin" config user.email t@example.test; git -C "$T/admin" config user.name Toy
cd "$T/repo" || exit 1
git switch -q -c loop/g
RUNS="$(git rev-parse --git-common-dir)/loop/runs"; mkdir -p "$RUNS"; RUNS=$(cd "$RUNS" && pwd)
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2" 2>/dev/null; then ok "$1"; else bad "$1"; [ -z "${out:-}" ] || head -3 <<<"$out" | sed "s/^/    out: /"; fi; }
# admin 'PYTHON' edits the base config dict c from a second clone, commits and pushes
admin() { (cd "$T/admin" && git pull -q origin main 2>/dev/null; python3 - "$D" "$1" <<'PY'
import json, os, sys
sys.path.insert(0, sys.argv[1]); import sizing
p = ".loop/config.json"
c = json.load(open(p)) if os.path.exists(p) else {"base": "main"}
c.setdefault("base", "main")
exec(sys.argv[2])
os.makedirs(".loop", exist_ok=True); json.dump(c, open(p, "w"), indent=2)
PY
git add -A; git commit -qm cfg >/dev/null; git push -q origin HEAD:main) >/dev/null 2>&1; git fetch -q origin; }
TB='c["checks_by_size"] = json.loads(json.dumps(sizing.DEFAULTS)); '; TABLE=${TB%; }
cat > "$T/h.py" <<'PY'
# A harness over the real functions. usage: h.py sized|check|resize|ratchet|atpr|stage SLUG ARG...
import json, os, sys
sys.path.insert(0, sys.argv[1]); import guards, sizing
cmd, slug, arg = sys.argv[2], sys.argv[3], (sys.argv[4:] or [""])
runs = os.path.join(os.path.abspath(sizing.git("rev-parse", "--git-common-dir").stdout.strip()), "loop", "runs")
path = os.path.join(runs, slug + ".json")
state = json.load(open(path))
if cmd == "sized":
    print(json.dumps(state["sized"].get(arg[0]) if arg[0] else state["sized"]))
elif cmd == "check":
    text = open(arg[1]).read()
    got = guards.check_record(state, arg[0], text, {"base": "main"}, "done")
    print("REFUSED %s: %s" % (got[1][2], got[1][0]) if got[1] else "OK%s" % got[0])
elif cmd == "resize":
    state["step"] = arg[0]; sizing.resize(state, arg[0]); print(state["sized"]["size"])
elif cmd == "ratchet":
    table = sizing.read_table()[0]
    sizing.update(slug, lambda old: sizing.build(old, arg[0], "owner", table, {}))
elif cmd == "atpr":
    class G:
        class guards:
            refuse_no_try = staticmethod(lambda *a: sys.exit(2))
        save = None
    sizing.at_pr(G, state)
elif cmd == "stage":
    state.update(json.loads(arg[0])); json.dump(state, open(path, "w"))
PY
H="python3 $T/h.py $D"
plan() { mkdir -p .loop/goals; printf '# Plan\nFiles: %s\nLines: %s\nGates: %s\nClasses: %s\n' "$2" "$3" "$4" "$5" > .loop/goals/$1.plan.md; }
new() { plan "$@"  # new SLUG FILES LINES GATES CLASSES: a goal state and its plan file
  python3 - "$RUNS" "$1" "$PWD" <<'PY'
import json, sys
json.dump({"slug": sys.argv[2], "step": "plan", "flow": {}, "worktree": sys.argv[3], "release": "v1.1.0", "rules_at": {}}, open("%s/%s.json" % (sys.argv[1], sys.argv[2]), "w"))
PY
}
reply() { printf '%s\nSTEP: done\n' "$2" > "$T/$1.txt"; echo "$T/$1.txt"; }
admin "$TABLE"

new a1 "docs/a.md, docs/b.md" 40 none none; out=$(python3 $D/sizing.py size a1 2>&1)
check "ASZ-1.1 a goal touching 2 files and no gate is sized small with its reason" '[ "$($H sized a1 size)" = "\"small\"" ] && echo "$out" | grep -q "SIZE small: 2 files, 40 lines, 0 gates" && ! echo "$out" | grep -qi "question"'
new a2 "docs/a.md" 40 "the build gate" none; python3 $D/sizing.py size a2 >/dev/null 2>&1
check "ASZ-1.1 a plan with a gate is not small" '[ "$($H sized a2 size)" = "\"medium\"" ]'
new a3 "docs/" 40 none none; out=$(python3 $D/sizing.py size a3 2>&1)
new a5 "docs/a.md" 40 none "security"; python3 $D/sizing.py size a5 >/dev/null 2>&1
check "ASZ-1.2 a goal in a safety class is always large" '[ "$($H sized a5 size)" = "\"large\"" ]'

want=$(python3 -c "
import json,sys; sys.path.insert(0,'$D'); import sizing
print(json.dumps({c:f for c,f in sizing.DEFAULTS['small'].items()},sort_keys=True))")
got=$(python3 -c "
import json; s=json.load(open('$RUNS/a1.json'))['sized']['checks']; print(json.dumps({c:v['form'] for c,v in s.items()},sort_keys=True))")
check "CBS-1.1 a small goal's record shows exactly the small checks, each in its named form" '[ "$want" = "$got" ]'
want_m=$(python3 -c "
import json,sys; sys.path.insert(0,'$D'); import sizing
print(json.dumps(sizing.DEFAULTS['medium'],sort_keys=True))")
got_m=$(python3 -c "
import json; s=json.load(open('$RUNS/a2.json'))['sized']['checks']; print(json.dumps({c:v['form'] for c,v in s.items()},sort_keys=True))")
check "CBS-1.1 a medium goal gets the medium row" '[ "$want_m" = "$got_m" ] && [ "$want" != "$got_m" ]'
check "CBS-1.1 the shipped defaults in sizing.py equal the repo config table" 'python3 -c "
import json,sys; sys.path.insert(0,\"$D\"); import sizing
c=json.load(open(\"$here/.loop/config.json\"))[\"checks_by_size\"]; assert c==json.loads(json.dumps(sizing.DEFAULTS))"'

admin "$TB"'c["checks_by_size"]["small"]["full-test-run"] = "skip"'
out=$(python3 $D/sizing.py size a1 2>&1); code=$?
check "CBS-1.2 a row that skips the full test run for small is refused naming the row and the check" '[ $code = 2 ] && echo "$out" | grep -q "SIZING_BAD_TABLE" && echo "$out" | grep -q "row small drops or lightens full-test-run"'
admin "$TABLE"
git switch -q -c wk; mkdir -p .loop; echo '{"base": "main", "checks_by_size": {"small": {}}}' > .loop/config.json
out=$(python3 $D/sizing.py size a1 2>&1)
check "CBS-1.2 a table row on a worker branch is not read" 'echo "$out" | grep -q "^SIZE small"'
echo '{"base": "wk"}' > .loop/config.json; git add .loop/config.json; git commit -qm wk; out=$(python3 $D/sizing.py rule a2 plan 2>&1)
check "CBS-1.2 a worker-named base keeps sizing on" 'echo "$out" | grep -q "^CHECKS at plan"'
git reset -q --hard HEAD~1; rm -f .loop/config.json; git switch -q loop/g; git branch -q -D wk

f=$(reply ok3 $'CHECK: plan-review full 3\nCHECK: red-team one-pass-no-rerun 1\nDEPTH: full'); out=$($H check a2 plan $f 2>&1)
check "CBS-1.3 a medium goal's plan record names its red team form and shows one pass" 'echo "$out" | grep -q "^OK.*light: red-team one-pass-no-rerun"'
f=$(reply bad3 $'CHECK: plan-review full 3\nCHECK: red-team full 2\nDEPTH: full'); out=$($H check a2 plan $f 2>&1)
check "CBS-1.3 a medium goal's red team written in the full form is refused" 'echo "$out" | grep -q "REFUSED SIZING_LINE sizing: red-team is not in its stored form one-pass-no-rerun"'
f=$(reply bad3c $'CHECK: plan-review full 3\nDEPTH: full'); out=$($H check a2 plan $f 2>&1)
check "CBS-1.3 a missing CHECK line is refused" 'echo "$out" | grep -q "REFUSED SIZING_MISSING sizing: the plan reply has no CHECK line for red-team"'
printf 'CHECK: plan-review full 3\nCHECK: red-team one-pass-no-rerun 1\nSTEP: skipped\n' > "$T/sk.txt"; out=$($H check a2 plan "$T/sk.txt" 2>&1)
check "CBS-1.3 a CHECK line on a skipped step is refused" 'echo "$out" | grep -q "REFUSED SIZING_CHECK_STEP"'
f=$(reply bud $'CHECK: plan-review full 3\nDEPTH: full'); $H stage a2 '{"budget_hits":[{"step":"plan","kind":"step"}]}' >/dev/null 2>&1
out=$($H check a2 plan $f 2>&1)
check "CBS-1.3 a budget-stopped reply still needs the lines" 'echo "$out" | grep -q "REFUSED SIZING_MISSING"'
printf 'DEPTH: full\nPENDING: ask\nSTEP: pending\n' > "$T/pe.txt"; out=$($H check a2 plan "$T/pe.txt" 2>&1)
check "CBS-1.3 a pending reply with no lines is refused" 'echo "$out" | grep -q "REFUSED SIZING_MISSING"'
new nosize "docs/a.md" 10 none none
python3 - "$RUNS" <<'PY'
import json, sys
p = sys.argv[1] + "/nosize.json"; s = json.load(open(p)); s["rules_at"] = {"plan": ["depth-line"]}; json.dump(s, open(p, "w"))
PY
f=$(reply old $'DEPTH: full'); out=$($H check nosize plan $f 2>&1)
check "CBS-1.3 an old goal is not refused" 'echo "$out" | grep -q "^OK"'
python3 - "$RUNS" <<'PY'
import json, sys
p = sys.argv[1] + "/nosize.json"; s = json.load(open(p)); s["rules_at"] = {"plan": ["depth-line", "sizing"]}; json.dump(s, open(p, "w"))
PY
out=$($H check nosize plan $f 2>&1)
check "CBS-1.3 an unsized goal is refused at the plan record" 'echo "$out" | grep -q "REFUSED SIZING_NOT_SIZED sizing"'
admin 'c.pop("checks_by_size", None)'
out=$($H check nosize plan $f 2>&1)
check "CBS-1.3 a repo with no key behaves as today" 'echo "$out" | grep -q "^OK"'
admin "$TABLE"

for g in c1 c2 c3; do new $g "docs/a.md, docs/b.md, docs/c.md, docs/d.md" 40 none none; python3 $D/sizing.py size $g >/dev/null 2>&1; done
out=$(python3 $R/cutcheck.py c1 c2 c3 2>&1)
check "CBS-1.4 cutcheck lists the light check of all three goals with its form" '[ $(echo "$out" | grep -c "red-team ran light (one-pass-no-rerun)") = 3 ]'
admin "$TB"'c["checks_by_size"]["forms"] = {"red-team": {"full": {"run": "true"}}}'
out=$(python3 $R/cutcheck.py c1 c2 c3 --require-full red-team 2>&1); code=$?
check "CBS-1.4 require-full runs the check's full form first and passes when it passes" '[ $code = 0 ] && [ $(echo "$out" | grep -c "^PASS red-team") = 3 ]'
admin "$TB"'c["checks_by_size"]["forms"] = {"red-team": {"full": {"run": "false"}}}'
out=$(python3 $R/cutcheck.py c1 c2 c3 --require-full red-team 2>&1); code=$?
check "CBS-1.4 require-full exits non-zero and names each goal when the check fails" '[ $code = 1 ] && echo "$out" | grep -q "^FAIL red-team c2"'
mkdir -p .loop; python3 - <<'PY'
import json; json.dump({"base": "main", "checks_by_size": {"forms": {"red-team": {"full": {"run": "true"}}}}}, open(".loop/config.json", "w"))
PY
out=$(python3 $R/cutcheck.py c1 --require-full red-team 2>&1); code=$?; rm -f .loop/config.json
check "CBS-1.4 the run command is read from the base only" '[ $code = 1 ]'
admin "$TABLE"; out=$(python3 $R/cutcheck.py c1 --require-full red-team 2>&1); code=$?
check "CBS-1.4 a check with no real test command prints NO COMMAND and exits non-zero" '[ $code != 0 ] && echo "$out" | grep -q "^NO COMMAND red-team" && ! echo "$out" | grep -q "^PASS"'
admin "$TB"'c["checks_by_size"]["forms"] = {"red-team": {"full": {"run": "echo RUNNING"}}}'; out=$(python3 $R/cutcheck.py c1 --require-full red-team 2>&1); code=$?
check "CBS-1.4 a run that is still RUNNING is never a PASS" '[ $code = 1 ] && echo "$out" | grep -q "^FAIL red-team c1"'
admin "$TABLE"

new s1 "docs/a.md, docs/b.md" 40 none none; python3 $D/sizing.py size s1 >/dev/null 2>&1
git add -A >/dev/null 2>&1; git commit -qm paperwork; for i in 1 2 3 4 5; do echo "x" > docs-$i.md; done
out=$($H resize s1 review 2>&1)
check "ASZ-1.2 a small goal whose diff passes the small line is re-sized to medium at review" '[ "$out" = "medium" ]'
check "ASZ-1.2 the added checks are stored" '[ "$($H sized s1 added)" = "[{\"check\": \"plan-review\", \"form\": \"full\"}]" ]'
f=$(reply sh2 ""); out=$($H check s1 ship $f 2>&1)
check "ASZ-1.2 ship names the added check with no evidence" 'echo "$out" | grep -q "REFUSED SIZING_ADDED_UNMET sizing: ship refused: added checks have no evidence line: plan-review"'
out=$($H atpr s1 2>&1); code=$?
check "ASZ-1.2 the pull request step refuses while an added check has no evidence line" '[ $code = 2 ]'
f=$(reply sh3 $'CHECK: plan-review full 3\nDEPTH: full'); out=$($H check s1 ship $f 2>&1)
check "ASZ-1.2 with its line the ship record is accepted" 'echo "$out" | grep -q "^OK"'
out=$($H atpr s1 2>&1); code=$?
check "ASZ-1.2 the PR step passes once the evidence is there" '[ $code = 0 ]'
rm -f docs-*.md; new s2 "docs/a.md" 10 none none; python3 $D/sizing.py size s2 >/dev/null 2>&1; $H ratchet s2 large
plan s2 "docs/a.md" 10 none none; python3 $D/sizing.py size s2 >/dev/null 2>&1
check "ASZ-1.2 a large plan edited down to small keeps its size and its large checks" '[ "$($H sized s2 size)" = "\"large\"" ] && [ "$($H sized s2 checks | python3 -c "import json,sys; print(json.load(sys.stdin)[\"red-team\"][\"form\"])")" = "full" ]'
git stash -q -u 2>/dev/null; git branch -m loop/g loop/g-old; git switch -q -c nodiff origin/main
mv "$T/origin.git" "$T/origin.gone" 2>/dev/null; git update-ref -d refs/remotes/origin/main 2>/dev/null; git branch -q -m main main-gone 2>/dev/null
out=$($H resize s2 review 2>&1); code=$?
check "ASZ-1.2 a failed diff read refuses SIZING_READ_FAILED" '[ $code = 2 ] && echo "$out" | grep -q "SIZING_READ_FAILED"'
mv "$T/origin.gone" "$T/origin.git" 2>/dev/null; git branch -q -m main-gone main 2>/dev/null; git fetch -q origin; git switch -q loop/g-old 2>/dev/null; git branch -q -m loop/g-old loop/g; git branch -q -D nodiff; git stash pop -q 2>/dev/null
admin "$TABLE"
# the lock: two writers race, the larger size and the union of checks survive; at_pr is one of the writers
ratchet_race() { for i in 1 2 3 4 5 6; do new r$i "docs/a.md" 10 none none; python3 $D/sizing.py size r$i >/dev/null 2>&1
  git add -A >/dev/null 2>&1; git commit -qm p$i; for j in 1 2 3 4 5; do echo x > race-$j.md; done
  ($H atpr r$i >/dev/null 2>&1 &); ($H ratchet r$i large >/dev/null 2>&1 &); sleep 1.5; rm -f race-*.md
  [ "$($H sized r$i size)" = "\"large\"" ] && [ "$($H sized r$i checks | python3 -c "import json,sys; c=json.load(sys.stdin); print(c['review']['form'], c['red-team']['form'])")" = "full full" ] || return 1; done; }
check "ASZ-1.2 two writers racing on one goal (the PR step and an owner raise) keep the larger size and the union of checks" 'ratchet_race'

new o1 "docs/a.md" 10 none none; python3 $D/sizing.py size o1 >/dev/null 2>&1
printf 'o7\t2026-11-24T00:00:00Z\toperation\t"size o1 up"\to1\n' > "$(git rev-parse --git-common-dir)/loop/owner-words.tsv"
out=$(python3 $M/sizeline.py set o1 large 2>&1); code=$?
check "ASZ-1.3 an owner line without the owner's words is refused" '[ $code = 2 ] && echo "$out" | grep -q "SIZING_NO_RECORD" && [ "$($H sized o1 size)" = "\"small\"" ]'
out=$(python3 $M/sizeline.py set o1 large --owner-record o7 2>&1); code=$?
check "ASZ-1.3 the owner's line sizes the goal up and prints the old and new size with the added checks" '[ $code = 0 ] && echo "$out" | grep -q "SIZE small -> large (record o7); added: plan-review, red-team, review"'
printf 'o9\t2026-11-24T00:00:00Z\toperation\t"smaller"\to1\n' >> "$(git rev-parse --git-common-dir)/loop/owner-words.tsv"
out=$(python3 $M/sizeline.py set o1 small --owner-record o9 2>&1); code=$?
check "ASZ-1.3 a smaller size is refused" '[ $code = 2 ] && echo "$out" | grep -q "SIZING_DOWN"'
out=$(python3 - "$M" "$RUNS" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1]); import board_tasks
run = json.load(open(sys.argv[2] + "/o1.json"))
print("\n".join(board_tasks.sizeline.alone([run], set())))
PY
)
check "ASZ-1.3 the board shows the new size with the owner's record for a goal with no task brief" 'echo "$out" | grep -q "^- o1: SIZE large (.*) checks: plan-review full, red-team full, review full; owner: o7"'
out=$(python3 - "$M" "$RUNS" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1]); import board_tasks
run = json.load(open(sys.argv[2] + "/o1.json"))
import tempfile, os
root = tempfile.mkdtemp(); os.makedirs(root + "/.loop/tasks")
open(root + "/.loop/tasks/t.md", "w").write("# T\n- Feature: F\n- Release: v1\n- Goals: o1\n- Source: s\n")
print("\n".join(board_tasks.task_lines(root, [run], None)))
PY
)
check "ASZ-1.3 the board shows the size under a task goal" 'echo "$out" | grep -q "o1 .*| SIZE large"'

out=$(python3 $D/sizing.py rule a2 plan 2>&1)
check "CBS-1.3 the rule prints each check, its form and the grammar" 'echo "$out" | grep -q "red-team: form one-pass-no-rerun, 1 pass. Covers: one pass, no rerun. Run:" && echo "$out" | grep -q "CHECK: <check> <form> <passes>" && echo "$out" | grep -q "^DEPTH: full"'
dr() { (cd "$T/repo" && python3 -c "
import json,sys; sys.path.insert(0,'$D'); import flow
print(flow.depth_rule(sys.argv[1], json.load(open('$RUNS/a1.json')), '$RUNS'))" "$1" 2>&1); }
out=$(dr plan)
check "CBS-1.3 a named plan skill gets the sizing command" 'echo "$out" | grep -q "sizing.py size a1" && echo "$out" | grep -q "CHECK: <check> <form> <passes>"'
out=$(dr review)
check "CBS-1.3 the review prompt follows the stored size" 'echo "$out" | grep -q "follows its size" && echo "$out" | grep -q "DEPTH: condensed"'
admin 'c["checks_by_size"] = True'; f=$(reply mal $'CHECK: x'); out=$($H check a2 plan $f 2>&1)
check "CBS-1.2 a malformed table refuses, no crash" 'echo "$out" | grep -q "REFUSED SIZING_BAD_TABLE"'
admin "$TABLE"; python3 - "$RUNS" <<'PY'
import json, sys
p = sys.argv[1] + "/a2.json"; s = json.load(open(p)); s["sized"]["checks"]["red-team"]["form"] = "retired"; json.dump(s, open(p, "w"))
PY
f=$(reply ret $'CHECK: plan-review full 3'); out=$($H check a2 plan $f 2>&1)
check "CBS-1.3 a stored form that left the table refuses cleanly" 'echo "$out" | grep -q "REFUSED SIZING_BAD_TABLE sizing: form retired of red-team left the table"'
new l1 "docs/a.md" "~1,200" none none; out=$(python3 $D/sizing.py size l1 2>&1)
check "ASZ-1.1 a comma in Lines counts as 1200" 'echo "$out" | grep -q "^SIZE medium: 1 files, 1200 lines"'
plan l1 "docs/a.md" "100-300" none none; out=$(python3 $D/sizing.py size l1 2>&1)
check "ASZ-1.1 a Lines range counts its largest" 'echo "$out" | grep -q "^SIZE medium: 1 files, 300 lines"'
f=$(reply ign $'STEP: skipped'); out=$($H check a3 plan $f 2>&1)
check "CBS-1.3 the last STEP line decides the CHECK need" 'echo "$out" | grep -q "REFUSED SIZING_MISSING"'
out=$(python3 $R/cutcheck.py nosize --require-full review 2>&1); code=$?
check "CBS-1.4 require-full fails for a goal with no stored size" '[ $code != 0 ] && echo "$out" | grep -q "NOT SIZED nosize"'
new s3 "docs/a.md" 10 none none; python3 $D/sizing.py size s3 >/dev/null 2>&1; git add -A >/dev/null 2>&1; git commit -qm p3; for i in 1 2 3 4 5; do echo x > rec-$i.md; done
f=$(reply rv $'CHECK: review normal 1\nDEPTH: condensed'); $H check s3 review $f >/dev/null 2>&1; rm -f rec-*.md
check "ASZ-1.2 the review record re-sizes from the diff" '[ "$($H sized s3 size)" = "\"medium\"" ]'
$H stage a1 '{"depth_override": {"depth": "full", "why": "owner"}}' >/dev/null; out=$(dr review)
check "ASZ-1.3 the owner's depth override wins" 'echo "$out" | grep -q "owner override" && ! echo "$out" | grep -q "follows its size"'
admin "$TABLE"
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "FAILED $fails"; exit 1; }
