#!/bin/bash
# reads: skills/workflow-delivery/scripts/cover.py skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/flow.py
# reads: skills/workflow-delivery/scripts/flow_steps.py skills/workflow-delivery/scripts/goal_steps.py skills/workflow-delivery/scripts/sizing.py
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/row_reach.py
# reads: .github/workflows/regression-pr.yml dev/toy/fakegh/gh dev/toy/fakegh/fake.py dev/toy/make.sh dev/toy/reap.sh
# Proves the L1 cover (SKP-1.1, o939): a goal whose PR gets L1 on GitHub records no local run of the rows L1 covers, runs only the
# rest (a partial lane, run --ids), and names L1 as the cover; any unknown keeps the whole lane. Parts: ids (the regression-skill
# lane flag and the moves), cover (the claim, the predicates, the ratchet, the certificates), all. No model is called.
# usage: test-cover.sh [ids|cover|all]
set -u
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID LOOP_SESSION_TOOL LOOP_OPERATION_SESSION GH_TOKEN GITHUB_TOKEN LOOP_COVER_IDS
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GIT_AUTHOR_NAME=T GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=T GIT_COMMITTER_EMAIL=t@example.com
export USERPROFILE="$HOME"
d=$(mktemp -d)
toy_on_exit 'rm -rf "$d" "$HOME"'
part=${1:-all}
"$here/dev/toy/make.sh" "$d" >/dev/null || exit 1
export LOOP_FLOW="$d/flow.json" PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh" TOY_LOG="$d/ran.log"
S="$here/skills/workflow-regression/scripts"; D="$here/skills/workflow-delivery/scripts"
reg() { python3 "$S/regression.py" "$@"; }
cd "$d/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
ran() { sort "$TOY_LOG" 2>/dev/null | tr '\n' ' '; }
fresh() { : > "$TOY_LOG"; }
common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
mkdir -p dev src .github/workflows "$common/loop/runs" "$d/gh"
for r in a b c s n; do printf 'ok\n' > "src/$r.txt"; printf 'echo %s >> "$TOY_LOG"; grep -q ok src/%s.txt\n' "$r" "$r" > "dev/$r.sh"; done
printf '# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n' > .loop/regression.tsv
for r in a b c s n; do printf '%s\tland\tbash dev/%s.sh\tX-1\t2026-01-01\t%s works.\tcriterion\t\n' "$r" "$r" "$r" >> .loop/regression.tsv; done
printf 's\tmacOS only: GitHub runs Ubuntu\nt\tmacOS only: GitHub runs Ubuntu\n' > .loop/regression-skips.tsv
printf 'n\tnightly\tkept out of the PR shards\n' > .loop/regression-limits.tsv
cp "$here/.github/workflows/regression-pr.yml" .github/workflows/
python3 - <<'PY'
import json
c = json.load(open(".loop/config.json")); c["regression_runs"] = "actions"; c["base"] = "main"; c["min_free_memory_gb"] = 0
json.dump(c, open(".loop/config.json", "w"), indent=2)
PY
git add -A; git commit -qm "Rows and workflow"
mkdir -p "$d/github.com"; mv "$d/origin.git" "$d/github.com/o-r.git"; git remote set-url origin "$d/github.com/o-r.git"; git push -q origin main
printf '%s\n' '[{"type":"merge_queue"},{"type":"required_status_checks","parameters":{"required_status_checks":[{"context":"affected","integration_id":15368},{"context":"small","integration_id":15368}]}}]' > "$d/gh/rules.json"
export FAKE_GH_PRIVATE=false
git switch -q -c feat
for r in a b c s n; do printf 'changed\n' > "src/$r.txt"; done
git add -A; git commit -qm "Change every row's file"

# The harness: cover.lane around a stub lane that records its calls; cover.need around stub need_lane and over_caps.
H=$(cat <<'PYEND'
import json, os, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import cover
runs, slug, cfg = sys.argv[2], "g1", json.load(open(".loop/config.json"))
calls = []
def stub(runs_, slug_, step, spec, cfg_, wait=90):
    calls.append(os.environ.get("LOOP_COVER_IDS", ""))
    return "pass", "LANE stub", []
mode, step = sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "qa"
if mode == "lane":
    status, line, ids = cover.lane(stub, runs, slug, step, {}, cfg)
    print("STATUS", status); print(line); print("CALLS", json.dumps(calls))
elif mode == "need":
    over = lambda: ("over_caps called", "fix", "TEST_CAPS")
    ref = lambda r, s, reply, st: ("no lane", "fix", "LANE_MISSING") if not os.environ.get("HAVE_OK") else None
    print("NEED", json.dumps(cover.need(ref, over, runs, slug, "reply.txt", step)))
elif mode == "late":
    print("LATE", cover.late(runs, slug, cfg))
elif mode == "part":
    print(cover.pr_part(runs, slug))
PYEND
)
cov() { python3 -B -c "$H" "$D" "$common/loop/runs" "$@" 2>&1; }
reset() { rm -f "$common"/loop/runs/g1.cover.json; }

if [ "$part" = all ] || [ "$part" = cover ]; then
echo "== the claim: covered rows run no local row, the rest run as a partial lane"
reset; out=$(cov lane qa); echo "$out"
check "a covered goal's qa names L1 as the cover and runs only the uncovered rows" 'grep -q "^COVERED 3 rows by L1; running 2 locally: n, s (claimed; pending PR recheck and GitHub execution)" <<<"$out" && grep -q "^CALLS \[\"n,s\"\]" <<<"$out"'
check "no covered row (a, b, c) is in the local lane's ids" '! grep -Eq "^CALLS .*\"[^\"]*\b[abc]\b" <<<"$out"'
check "the skip-listed row s and the nightly-limited row n stay local" 'grep -q "running 2 locally: n, s" <<<"$out"'
check "the claim is kept in the run folder, naming L1, the covered rows and the local rows" 'python3 -c "
import json; d=json.load(open(\"$common/loop/runs/g1.cover.json\"))[\"claim\"]
raise SystemExit(0 if d[\"name\"]==\"L1\" and d[\"covered\"]==[\"a\",\"b\",\"c\"] and d[\"local\"]==[\"n\",\"s\"] else 1)"'
check "the printed cover line never says SKIPPED, NOTRUN or ENV (lane.py and fit.py parse those words)" '! grep -Eq "^(NOTRUN|SKIPPED|ENV) " <<<"$out"'

echo "== every unknown keeps the whole lane (the cover is off, nothing is lost)"
# off NAME CODE: run cov lane qa with a mutation applied already; the lane stub must get no ids and the line must show no COVERED
off() { reset; out=$(cov lane qa); echo "--- $1"; echo "$out" | head -3
  check "$1: the whole lane runs (no ids)" 'grep -q "^CALLS \[\"\"\]" <<<"$out" && ! grep -q "^COVERED" <<<"$out"'
  [ -z "${2:-}" ] || check "$1: the code printed is $2, never a name or a URL" 'grep -Eq "^COVER OFF: '"$2"'\. (private repo: no cover\. )?Nothing is lost: the local lane runs in full; rerun flow.py g1 qa" <<<"$out"'; }
# a non-GitHub origin and a base that is not main: silent codes
git remote set-url origin "$d/elsewhere.git"; off "a non-GitHub origin"; git remote set-url origin "$d/github.com/o-r.git"
cp .loop/config.json "$d/config.keep"; python3 -c "
import json; c=json.load(open('.loop/config.json')); c['regression_runs']='local'; json.dump(c,open('.loop/config.json','w'))"
off "regression_runs is not actions"; cp "$d/config.keep" .loop/config.json
python3 -c "
import json; c=json.load(open('.loop/config.json')); c['base']='dev'; json.dump(c,open('.loop/config.json','w'))"
off "a base that is not main"; cp "$d/config.keep" .loop/config.json
git remote set-url origin "$d/github.com/none.git"; off "a failed fetch" FETCH; git remote set-url origin "$d/github.com/o-r.git"
# workflow variants on the base branch
wf() { git switch -q main; python3 -c "
import sys; p='.github/workflows/regression-pr.yml'; t=open(p).read(); a,b=sys.argv[1],sys.argv[2]
assert a in t, a
open(p,'w').write(t.replace(a,b,1))" "$1" "$2"; git commit -qam "variant"; git push -q origin main; git switch -q feat; }
unwf() { git switch -q main; git revert --no-edit HEAD >/dev/null; git push -q origin main; git switch -q feat; }
wf '  pull_request:
' '  pull_request:
    branches: [main]
'; off "a pull_request filter" WF; unwf
wf "if: always() && github.event_name != 'merge_group'" "if: false"; off "a job that can be skipped" WF; unwf
wf "if: always() && github.event_name != 'merge_group'" "if: github.event_name == 'merge_group'"; off "affected runs only in the merge queue" WF; unwf
wf "run nightly --reuse --tier goal" "run nightly --tier goal"; off "a no-op shard (no --reuse)" WF; unwf
wf 'test "${{ needs.shard.result }}" = success' 'true'; off "a missing aggregate" WF; unwf
git switch -q main; git rm -q .github/workflows/regression-pr.yml; git commit -qm "no workflow"; git push -q origin main; git switch -q feat
off "no workflow on the base" WF; git switch -q main; git revert --no-edit HEAD >/dev/null; git push -q origin main; git switch -q feat
# the ruleset
cp "$d/gh/rules.json" "$d/rules.keep"
printf '%s\n' '[{"type":"required_status_checks","parameters":{"required_status_checks":[{"context":"small","integration_id":15368}]}}]' > "$d/gh/rules.json"; off "affected is not required" RULE
printf '%s\n' '[{"type":"required_status_checks","parameters":{"required_status_checks":[{"context":"affected"},{"context":"small"}]}}]' > "$d/gh/rules.json"; off "the required checks are not pinned to an app" RULE
printf '%s\n' '[{"type":"required_status_checks","parameters":{"required_status_checks":[{"context":"affected","integration_id":1},{"context":"small","integration_id":1}]}}]' > "$d/gh/rules.json"; off "the checks are pinned to another app" RULE
cp "$d/rules.keep" "$d/gh/rules.json"
FAKE_GH_PRIVATE=true off "a private repository" PRIV
export FAKE_GH_PRIVATE=false
# the diff
git switch -q -c docs main; printf 'doc\n' >> README.md; git commit -qam "docs"; off "a documents-only diff" DOC
git switch -q feat; git switch -q -c ghdir feat; mkdir -p .github/workflows; printf 'on: push\n' > .github/workflows/extra.yml; git add -A; git commit -qm "workflow"
off "a change under .github" GHDIR
git switch -q feat; git switch -q -c tool feat; mkdir -p skills/workflow-regression/scripts; printf '#\n' > skills/workflow-regression/scripts/x.py; git add -A; git commit -qm "tooling"
off "a change to the regression scripts (the tooling-cover line)" TOOL
git switch -q feat
echo "== the ratchet, the lost cover and the certificates"
reset; out=$(cov lane pr); echo "$out" | head -3
check "pr never grants a cover the claim did not hold at qa or ship" 'grep -q "^CALLS \[\"\"\]" <<<"$out" && ! grep -q "^COVERED" <<<"$out"'
reset; cov lane qa >/dev/null
lanes=$(python3 -c "
import sys; sys.path.insert(0,'$D'); sys.dont_write_bytecode=True
import lanekit
print(' '.join(lanekit.lane_base('$common/loop/runs','g1',n) for n in ('qa','ship','pr')))")
for b in $lanes; do : > "$b.ok"; : > "$b.last"; done
git switch -q main; git rm -q .github/workflows/regression-pr.yml; git commit -qm "no workflow"; git push -q origin main; git switch -q feat
out=$(cov lane pr); echo "$out" | head -4
check "a lost cover is a notice, not a refusal: COVER_LOST, the full lane runs" 'grep -q "^COVER LOST (COVER_LOST): WF\. Non-fatal: the local lane now runs in full" <<<"$out" && grep -q "^CALLS \[\"\"\]" <<<"$out"'
check "a lost cover drops the qa, ship and pr lane passes and nothing else" 'for b in $lanes; do [ ! -e "$b.ok" ] && [ ! -e "$b.last" ] || exit 1; done; [ -e "$common/loop/runs/g1.cover.json" ]'
git switch -q main; git revert --no-edit HEAD >/dev/null; git push -q origin main; git switch -q feat
# a branch that adds a row to the skip list: GitHub reads that list from the merge ref, so the row is local
git switch -q -c skipb feat; printf 'a\tmacOS only\n' >> .loop/regression-skips.tsv; git commit -qam "Skip a"
reset; out=$(cov lane qa); check "a row this branch adds to the skip list is local, or the cover is off (never covered)" 'grep -Eq "^COVER OFF: REACH|^COVERED [0-9]+ rows by L1; running [0-9]+ locally: .*\ba\b" <<<"$out"'
git switch -q feat

echo "== the record: a covered row is waived, an uncovered row still needs its own pass"
reset; cov lane qa >/dev/null
out=$(cov need qa); echo "$out"
check "uncovered rows (n, s) with no passing local lane are refused: LANE_MISSING_UNCOVERED, naming the rows" 'grep -q "LANE_MISSING_UNCOVERED" <<<"$out" && grep -q "n, s have no passing local lane" <<<"$out" && grep -q "skills/workflow-delivery/scripts/cover.py lane g1 qa" <<<"$out"'
out=$(HAVE_OK=1 cov need qa); check "the lane's own pass for the uncovered rows is accepted" 'grep -q "^NEED null" <<<"$out"'
git switch -q -c feat2 feat; printf 't\tland\tbash dev/t.sh\tX-1\t2026-01-01\tt works.\tcriterion\t\n' >> .loop/regression.tsv; printf 'echo t >> "$TOY_LOG"; grep -q ok src/t.txt\n' > dev/t.sh; printf 'ok\n' > src/t.txt; git add -A; git commit -qm "A new reachable row"
out=$(HAVE_OK=1 cov need qa); echo "$out"
check "a row that became reachable after the claim runs locally: the old lane pass is not enough" 'grep -q "LANE_MISSING_UNCOVERED" <<<"$out" && grep -q "t have no passing local lane" <<<"$out"'
lb() { python3 -c "import sys; sys.path.insert(0,'$D'); sys.dont_write_bytecode=True; import lanekit; print(lanekit.lane_base('$common/loop/runs','g1','$1'))"; }
git switch -q feat; reset; cov lane qa >/dev/null; : > "$(lb qa).ok"; git switch -q feat2; cov lane qa >/dev/null
check "local rows that grew drop the earlier partial pass" '[ ! -e "$(lb qa).ok" ]'
git switch -q feat
git switch -q -c allc main; for r in a b c; do printf 'again\n' > "src/$r.txt"; done; git add -A; git commit -qm "Only covered rows change"
git switch -q feat; reset; cov lane qa >/dev/null; git switch -q allc; cov lane ship >/dev/null; out=$(cov part)
check "the PR text keeps every row that ran locally at any step, though the last step planned none" 'grep -q "Run locally: 2 rows (n, s)" <<<"$out"'
out=$(python3 -B "$D/cover.py" lane g1 qa 2>&1); rc=$?
check "the lane command with nothing left to run locally says so and starts no lane" '[ $rc = 0 ] && grep -q "^COVERED: every selected row is covered by L1; nothing is left to run locally" <<<"$out"'
reset; out=$(cov lane qa); echo "$out" | head -3
check "when every selected row is covered the local lane is not run at all" 'grep -q "^COVERED 3 rows by L1; running 0 locally: none" <<<"$out" && grep -q "^CALLS \[\]" <<<"$out" && grep -q "^STATUS pass" <<<"$out"'
out=$(cov need qa); check "a covered goal's record still runs over_caps at qa" 'grep -q "over_caps called" <<<"$out"'
out=$(cov need ship); check "a covered goal's ship record needs no lane" 'grep -q "^NEED null" <<<"$out"'
git switch -q feat
reset; out=$(cov need qa); check "no claim: the record is exactly what role.need_lane says" 'grep -q "LANE_MISSING\"" <<<"$out" || grep -q "LANE_MISSING" <<<"$out"'
echo "== the final head: a late loss, the PR text, the prompt, the lane command"
reset; cov lane qa >/dev/null; out=$(cov late pr); check "the cover still holds on the final head: no late loss" 'grep -q "^LATE False" <<<"$out"'
out=$(cov part pr); echo "$out"
check "the PR text names L1, says pending GitHub execution, lists both sets and an estimate" 'grep -q "Covered by L1, the PR.s pull_request run (regression-pr), pending GitHub execution, head [0-9a-f]\{12\}: 3 rows (a, b, c)" <<<"$out" && grep -q "Run locally: 2 rows (n, s)" <<<"$out" && grep -q "estimated avoided: unavailable" <<<"$out"'
git switch -q -c rr feat; mkdir -p skills/workflow-regression/scripts; printf '#\n' > skills/workflow-regression/scripts/row_reach.py; git add -A; git commit -qm "moves the reach finder"
out=$(cov part pr); git switch -q feat
check "the PR that moves the reach finder states its limits: cold first runs, macOS rows, its own cover off, the two untested paths" 'grep -q "first PRs after this merges run cold" <<<"$out" && grep -q "not on the skip list go unrun on macOS" <<<"$out" && grep -q "its own cover is off" <<<"$out" && grep -q "flow.py qa end to end" <<<"$out"'
git switch -q main; git rm -q .github/workflows/regression-pr.yml; git commit -qm "no workflow"; git push -q origin main; git switch -q feat
out=$(cov late pr); check "a lost cover on the final head is a late loss" 'grep -q "^LATE True" <<<"$out" && grep -q "COVER LOST (COVER_LOST): WF" <<<"$out"'
git switch -q main; git revert --no-edit HEAD >/dev/null; git push -q origin main; git switch -q feat
reset; cov lane qa >/dev/null
LANE='The regression lane (label regression, command `x`) already passed on this content: reuse that run through your own check of recorded test runs instead of running the suite again; if your own test step runs that exact command, it reuses the record and returns at once.'
out=$(python3 -B -c "import sys; sys.path.insert(0,'$D'); sys.dont_write_bytecode=True; import cover; print(cover.prompt('a. $LANE b.', '$common/loop/runs', 'g1'))")
check "the qa and ship prompt says the covered rows are covered and the rest run by flow.py" 'grep -q "^a. 3 rows are covered by L1 (claimed; pending PR recheck and GitHub execution); the 2 other rows run by flow.py; run no suite yourself. b.$" <<<"$out"'
out=$(python3 -B -c "import sys; sys.path.insert(0,'$D'); sys.dont_write_bytecode=True; import cover; print(cover.prompt('a. $LANE b.', '$common/loop/runs', 'nope'))")
check "with no claim the prompt is byte for byte as today" 'grep -q "already passed on this content" <<<"$out"'
RULE_TXT='  full-test-run: form full, 1 pass. Covers: the full test run passes. Run: python3 skills/workflow-regression/scripts/regression.py run'
out=$(python3 -B -c "import sys; sys.path.insert(0,'$D'); sys.dont_write_bytecode=True; import cover; print(cover.rule_fix('$RULE_TXT', '$common/loop/runs', 'g1'))")
check "the sizing rule's full-test-run line says what L1 covers and what still runs locally" 'grep -q "Run: covered by L1 (claimed; pending PR recheck and GitHub execution): 3 rows; the other 2 rows still run locally$" <<<"$out"'
out=$(cd "$D" && LOOP_COVER_IDS=n,s python3 -B -c "import sys; sys.dont_write_bytecode=True; import lane; print(lane.lane_argv()[-2:], lane.lane_argv(5)[-4:])")
check "the lane command takes --ids from LOOP_COVER_IDS and adds nothing without it" 'grep -q "\[.--ids., .n,s.\]" <<<"$out" && ! (cd "$D" && python3 -B -c "import sys; sys.dont_write_bytecode=True; import lane; print(lane.lane_argv())") | grep -q -- "--ids"'
fi
exit $((fails > 0))
