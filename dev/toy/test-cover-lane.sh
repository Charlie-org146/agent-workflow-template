#!/bin/bash
# reads: skills/workflow-delivery/scripts/cover.py skills/workflow-delivery/scripts/cover_text.py skills/workflow-delivery/scripts/lane.py skills/workflow-delivery/scripts/lane_run.py
# reads: skills/workflow-delivery/scripts/lanekit.py skills/workflow-delivery/scripts/role.py skills/workflow-delivery/scripts/goal_steps.py skills/workflow-regression/scripts/tiers.py
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/row_reach.py
# reads: .github/workflows/regression-pr.yml dev/toy/fakegh/gh dev/toy/fakegh/fake.py dev/toy/make.sh dev/toy/reap.sh
# Proves the L1 cover's lane certificates and its fail-safes, the checks its review rounds added (split from test-cover.sh): a
# narrowed lane runs only the rows the standing claim lists and its pass counts only while the claim lists exactly them; a cut,
# failed, skipped, flaky or unproven row stays local; the whole base workflow is pinned; an unread list or a refusal that is not
# about the lane never becomes a cover; a late loss's bookkeeping commit changes no tested input. No model is called.
# usage: test-cover-lane.sh
set -u
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID LOOP_SESSION_TOOL LOOP_OPERATION_SESSION GH_TOKEN GITHUB_TOKEN LOOP_COVER_IDS
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GIT_AUTHOR_NAME=T GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=T GIT_COMMITTER_EMAIL=t@example.com
export USERPROFILE="$HOME"
d=$(mktemp -d)
toy_on_exit 'rm -rf "$d" "$HOME"'
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
    ref = lambda r, s, reply, st: (("over a cap", "fix", "TEST_CAPS") if os.environ.get("REF_CAPS") else ("no lane", "fix", "LANE_MISSING")) if not os.environ.get("HAVE_OK") else None
    print("NEED", json.dumps(cover.need(ref, over, runs, slug, "reply.txt", step)))
elif mode == "late":
    print("LATE", cover.late(runs, slug, cfg))
elif mode == "part":
    print(cover.pr_part(runs, slug))
PYEND
)
cov() { python3 -B -c "$H" "$D" "$common/loop/runs" "$@" 2>&1; }
reset() { rm -f "$common"/loop/runs/g1.cover.json; }


echo "== the fail-safes the review rounds added (whole workflow pin, unread lists)"
# off NAME CODE: run cov lane qa with a mutation applied already; the lane stub must get no ids and the line must show no COVERED
off() { reset; out=$(cov lane qa); echo "--- $1"; echo "$out" | head -3
  check "$1: the whole lane runs (no ids)" 'grep -q "^CALLS \[\"\"\]" <<<"$out" && ! grep -q "^COVERED" <<<"$out"'
  [ -z "${2:-}" ] || check "$1: the code printed is $2, never a name or a URL" 'grep -Eq "^COVER OFF: '"$2"'\. (private repo: no cover\. )?Nothing is lost: the local lane runs in full; rerun flow.py g1 qa" <<<"$out"'; }
wf() { git switch -q main; python3 -c "
import sys; p='.github/workflows/regression-pr.yml'; t=open(p).read(); a,b=sys.argv[1],sys.argv[2]
assert a in t, a
open(p,'w').write(t.replace(a,b,1))" "$1" "$2"; git commit -qam "variant"; git push -q origin main; git switch -q feat; }
unwf() { git switch -q main; git revert --no-edit HEAD >/dev/null; git push -q origin main; git switch -q feat; }
wf "run nightly --reuse --tier goal" "run nightly --reuse --tier goal --kind defect"; off "a shard narrowed by another argument" WF; unwf
wf '$R --budget $B --timeout 200' '$R --budget $B --timeout 200 --kind defect'; off "one shard call narrowed by another argument" WF; unwf
wf "      - run: python3 skills/workflow-regression/scripts/cutgate.py 's/shard-[0-7]/t.tsv' all.tsv .loop/regression-skips.tsv 8
" ""; off "no aggregate check of the shards" WF; unwf
wf "    timeout-minutes: 30
" "    timeout-minutes: 30
    continue-on-error: true
"; off "a shard job allowed to fail" WF; unwf
wf "shard: [0, 1, 2, 3, 4, 5, 6, 7, tree]" "shard: [0, 1, 2, 3, 4, 5, 6, 7]"; off "a matrix without the whole-tree shard" WF; unwf
# a skip or limit list that is there but cannot be read is an unknown; a list that is not there is empty
mkdir -p "$d/gitw"; printf '#!/bin/bash
[ "$1 $2" = "show origin/main:.loop/regression-limits.tsv" ] && exit 1
[ "$1" = ls-tree ] && [ -n "${GITW_MISSING:-}" ] && exit 0
exec %s "$@"
' "$(command -v git)" > "$d/gitw/git"; chmod +x "$d/gitw/git"
PATH="$d/gitw:$PATH" off "an unread limit list on the base" LIST
reset; out=$(GITW_MISSING=1 PATH="$d/gitw:$PATH" cov lane qa)
check "control: a limit list that is not on the base reads as empty, and the cover still holds" 'grep -q "^COVERED " <<<"$out" && ! grep -q "COVER OFF" <<<"$out"'

echo "== a refusal that is not about the lane passes through"
reset; cov lane qa >/dev/null
out=$(REF_CAPS=1 cov need qa); check "a refusal that is not about the lane (TEST_CAPS) passes through the cover unchanged" 'grep -q "^NEED \[\"over a cap\", \"fix\", \"TEST_CAPS\"\]" <<<"$out"'

echo "== the lane command, the certificates, the real lane, cut and unproven rows"
lane1() { (cd "$D" && LOOP_COVER_IDS=n,s python3 -B -c "import sys; sys.dont_write_bytecode=True; import lane; print($1)") 2>&1; }
check "LOOP_COVER_IDS alone narrows no lane command: lane_argv never reads it" 'o=$(lane1 "lane.lane_argv(), lane.lane_argv(5)"); [ "${o:0:1}" = "[" ] && ! grep -q -- "--ids" <<<"$o"'
cid() { (cd "$D" && LOOP_COVER_IDS=$1 python3 -B -c "import sys; sys.dont_write_bytecode=True; import lane; print('IDS=' + lane.cover_ids('$common/loop/runs', 'g1'))") 2>&1; }
reset; a=$(cid n,s); cov lane qa >/dev/null; b=$(cid n,s); c=$(cid s,n); e=$(cid n); f=$(cid a,b,c,n,s)
check "the launch honours LOOP_COVER_IDS only while the cover claim lists exactly those ids" '[ "$a" = IDS= ] && [ "$b" = IDS=n,s ] && [ "$c" = IDS=n,s ] && [ "$e" = IDS= ] && [ "$f" = IDS= ]'
NL=$(cat <<'PYEND'
import os, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import lanekit, role
runs = sys.argv[2]
for n in ("qa", "ship", "pr"):
    try:
        os.remove(lanekit.lane_base(runs, "g1", n) + ".ok")
    except OSError:
        pass
open(lanekit.lane_base(runs, "g1", "qa") + ".ok", "w").write((role.git_out("rev-parse", "HEAD") + " " + sys.argv[3]).strip())
got = role.need_lane(runs, "g1", "nope.txt", "qa")
print("NEED", got[2] if got else None)
PYEND
)
okneed() { python3 -B -c "$NL" "$D" "$common/loop/runs" "$1" 2>&1; }
reset; r1=$(okneed n,s); cov lane qa >/dev/null; r2=$(okneed n,s); r3=$(okneed n); r4=$(okneed ""); reset; r5=$(okneed "")
echo "$r1 | $r2 | $r3 | $r4 | $r5"
check "a lane .ok narrowed to ids is refused at record without a cover claim listing exactly those ids: LANE_MISSING" '[ "$r1" = "NEED LANE_MISSING" ] && [ "$r3" = "NEED LANE_MISSING" ]'
check "a narrowed lane .ok whose ids the cover claim lists exactly is accepted" '[ "$r2" = "NEED None" ]'
check "control: a full lane .ok (HEAD only, no ids) still passes, with or without a claim" '[ "$r4" = "NEED None" ] && [ "$r5" = "NEED None" ]'
w=$(cd "$D" && python3 -B -c "import sys; sys.dont_write_bytecode=True; import lane_run; print(lane_run.ok_text({'head': 'h', 'ids': 'n,s'}) + '|' + lane_run.ok_text({'head': 'h', 'ids': ''}))" 2>&1)
check "a passing lane's .ok holds HEAD then the ids of a narrowed lane, and HEAD alone for a full lane" '[ "$w" = "h n,s|h" ]'
# The real lane under a stub recorder: what the launch passes, and what a pass records.
cat > "$d/rec.sh" <<'A'
#!/bin/bash
echo "ARGV: $*"
[ -z "${TOY_LEFT:-}" ] || echo "BUDGET 1 min: ran 1 of 2 rows; LEFT 1 to the scheduled full suite: s"
exit 0
A
RL=$(cat <<'PYEND'
import json, os, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import lane, lanekit
runs, base = sys.argv[2], lanekit.lane_base(sys.argv[2], "g1", "qa")
status, line, _ = lane.lane(runs, "g1", "qa", {"test_record": ["bash", sys.argv[3]]}, json.load(open(".loop/config.json")), 60, os.environ.get("REDO") != "0")
print("STATUS", status); print(line)
print("ARGS", " ".join(l for l in open(base + ".txt").read().splitlines() if l.startswith("ARGV:")))
head = os.popen("git rev-parse HEAD").read().strip()
print("OK", open(base + ".ok").read().replace(head, "HEAD") if os.path.exists(base + ".ok") else "none")
PYEND
)
real() { python3 -B -c "$RL" "$D" "$common/loop/runs" "$d/rec.sh" 2>&1; }
reset; o1=$(LOOP_COVER_IDS=n,s real); cov lane qa >/dev/null; o2=$(LOOP_COVER_IDS=n,s real); o3=$(LOOP_COVER_IDS=n real)
o4=$(LOOP_COVER_IDS=n,s TOY_LEFT=1 real); reset; o5=$(TOY_LEFT=1 real)
printf '%s\n--\n' "$o1" "$o2" "$o3" "$o4" "$o5"
check "the real lane with LOOP_COVER_IDS and no claim launches without --ids and records HEAD alone" 'grep -q "^STATUS pass" <<<"$o1" && grep -q "^ARGS ARGV: " <<<"$o1" && ! grep -q -- "--ids" <<<"$o1" && grep -q "^OK HEAD$" <<<"$o1"'
check "the real lane with a claim listing exactly those ids launches --ids n,s and records HEAD then the ids" 'grep -q "^STATUS pass" <<<"$o2" && grep -q "^ARGS ARGV: .* --ids n,s$" <<<"$o2" && grep -q "^OK HEAD n,s$" <<<"$o2"'
check "the real lane with ids the claim does not list launches without --ids (the whole lane)" 'grep -q "^STATUS pass" <<<"$o3" && grep -q "^ARGS ARGV: " <<<"$o3" && ! grep -q -- "--ids" <<<"$o3" && grep -q "^OK HEAD$" <<<"$o3"'
check "a narrowed lane that leaves rows unrun records no pass: LANE_LEFT names the cut row and the budget, no .ok" 'grep -q "^STATUS fail" <<<"$o4" && grep -q "LANE_LEFT: the lane narrowed to n,s left s unrun" <<<"$o4" && grep -q "raise test_budget_minutes" <<<"$o4" && grep -q "^OK none$" <<<"$o4"'
check "control: a whole lane cut by the budget still passes as before" 'grep -q "^STATUS pass" <<<"$o5" && ! grep -q -- "--ids" <<<"$o5" && grep -q "^OK HEAD$" <<<"$o5"'
reset; cov lane qa >/dev/null; LOOP_COVER_IDS=n,s real >/dev/null; reset
st=$(python3 -B -c "import sys; sys.path.insert(0, '$D'); sys.dont_write_bytecode=True; import lane; print('STATE', lane.lane_status('$common/loop/runs', 'g1', 'qa')[0])" 2>&1); echo "$st"
check "the status of a narrowed pass whose claim is gone is not pass (lane-wait never answers it)" '[ "$st" != "STATE pass" ] && grep -q "^STATE " <<<"$st"'
o6=$(REDO=0 real)
check "a narrowed pass is not reused once its claim is gone: the whole lane runs again" 'grep -q "^STATUS pass" <<<"$o6" && grep -q "^ARGS ARGV: " <<<"$o6" && ! grep -q -- "--ids" <<<"$o6" && grep -q "^OK HEAD$" <<<"$o6"'
# a row a narrowed run left unrun (LEFT in the run record) stays local: it is never planned as reused
LR=$(cat <<'PYEND'
import os, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import lanes
root = os.getcwd(); path = lanes.record_path(root); old, _ = lanes.load(path, root)
lanes.save(path, root, old["command"], [{"id": "s", "state": "LEFT", "seconds": 0}], old["commit"], old["at"], False, old.get("merge_base"))
print("LEFT", lanes.load(path, root)[0]["rows"]["s"]["status"])
PYEND
)
reset; reg run land --reuse --tier goal --ids n,s >/dev/null 2>&1; o7=$(cov lane qa); o8=$(python3 -B -c "$LR" "$S" 2>&1); o9=$(cov lane qa)
echo "$o7" | head -1; echo "$o8"; echo "$o9" | head -1
check "a row left unrun by a narrowed run stays local, never planned as reused" 'grep -q "^LEFT LEFT$" <<<"$o8" && grep -Eq "^COVERED [0-9]+ rows by L1; running [0-9]+ locally: .*\bs\b" <<<"$o9"'
fresh; o10=$(reg run land --reuse --tier goal --ids s 2>&1); echo "$o10" | grep -E "^(SELECTED|REUSED|ROWS|RESULT)"
# a row that passes but has no seen-failing date stays local: it is never waived
git switch -q -c unp feat; printf 'u\tland\tbash dev/u.sh\tX-1\t\tu works.\tcriterion\t\n' >> .loop/regression.tsv; printf 'echo u >> "$TOY_LOG"\n' > dev/u.sh; git add -A; git commit -qm "An unproven row"
reset; reg run land --reuse --tier goal --ids u >/dev/null 2>&1; o11=$(cov lane qa); git switch -q feat; echo "$o11" | head -1
check "a row that passes but is unproven stays local, never waived" 'grep -Eq "^COVERED [0-9]+ rows by L1; running [0-9]+ locally: .*\bu\b" <<<"$o11"'
check "the narrowed run after a LEFT record runs that row again, never reuses it" 'grep -q "^s$" "$TOY_LOG" && grep -q "^SELECTED s: skipped last time" <<<"$o10" && ! grep -q "^REUSED" <<<"$o10"'
SH=$(cat <<'PYEND'
import json, os, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import cover, lanekit
runs, base = sys.argv[2], lanekit.lane_base(sys.argv[2], "g1", "qa")
data = cover.load(runs, "g1"); data["claim"]["local"] = ["n", "s", "t"]; cover.save(runs, "g1", data)
open(base + ".ok", "w").write(os.popen("git rev-parse HEAD").read().strip() + " n,s,t"); open(base + ".last", "w").write("{}")
cover.lane(lambda *a, **k: ("pass", "LANE stub", []), runs, "g1", "qa", {}, json.load(open(".loop/config.json")))
print("LEFT", os.path.exists(base + ".ok"), os.path.exists(base + ".last"))
PYEND
)
reset; cov lane qa >/dev/null; out=$(python3 -B -c "$SH" "$D" "$common/loop/runs" 2>&1)
check "local rows that shrank drop the earlier narrowed pass and its own record (no stuck refusal)" '[ "$out" = "LEFT False False" ]'

echo "== the late loss: the second bookkeeping commit"
# after a late loss, the second bookkeeping commit may touch only the tool's no-effect and bookkeeping files
LI='import os, sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True; import cover; print("LATE", cover.late_inputs(os.getcwd(), sys.argv[2]))'
git switch -q -c late feat; t0=$(git rev-parse HEAD); printf 'x\tPASS\n' >> .loop/regression-runs.tsv; git add -A; git commit -qm "records"; l1=$(python3 -B -c "$LI" "$D" "$t0" 2>&1)
mkdir -p docs/wiki; printf 'page\n' > docs/wiki/Tests.md; printf '# more\n' >> .loop/regression.tsv; git add -A; git commit -qm "pages and rows"; l2=$(python3 -B -c "$LI" "$D" "$t0" 2>&1); git switch -q feat
echo "$l1"; echo "$l2"
check "after a late loss, a bookkeeping commit that touches only the run records changes no tested input" '[ "$l1" = "LATE []" ]'
check "after a late loss, a bookkeeping commit that changes a page or the row table is named as changing tested inputs (LATE_INPUTS)" 'grep -q "docs/wiki/Tests.md" <<<"$l2" && grep -q "[.]loop/regression[.]tsv" <<<"$l2"\'
exit $((fails > 0))
