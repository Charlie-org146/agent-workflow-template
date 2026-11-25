#!/bin/bash
# reads: skills/workflow-delivery/scripts/cover.py skills/workflow-delivery/scripts/goal_steps.py skills/workflow-delivery/scripts/lane.py
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/lanes.py skills/workflow-regression/scripts/row_reach.py
# reads: skills/workflow-regression/scripts/narrow.py skills/workflow-regression/scripts/completion.py skills/workflow-release/scripts/merge.py
# reads: dev/toy/fakegh/gh dev/toy/fakegh/fake.py dev/toy/make.sh dev/toy/reap.sh
# Proves the pr side and the regression-skill side of the L1 cover (SKP-1.1, o939, o963): `regression.py run --ids` runs exactly its rows
# as one lane (memory wait, slot, no tracked write, the record kept); the reach finder moved to row_reach.py unchanged and every module
# still imports alone and in the cycle orders; the runner fingerprint covers row_reach.py and completion.py; the PR body refresh
# refuses with BODY_STALE; a covered goal cannot join a batch merge. Parts: ids, moves, merge, all. No model is called.
# usage: test-cover-pr.sh [ids|moves|merge|all]
set -u
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID LOOP_SESSION_TOOL LOOP_OPERATION_SESSION GH_TOKEN GITHUB_TOKEN LOOP_COVER_IDS
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) PYTHONDONTWRITEBYTECODE=1 GIT_AUTHOR_NAME=T GIT_AUTHOR_EMAIL=t@example.com GIT_COMMITTER_NAME=T GIT_COMMITTER_EMAIL=t@example.com
export USERPROFILE="$HOME"
d=$(mktemp -d)
toy_on_exit 'rm -rf "$d" "$HOME"'
part=${1:-all}
BASE=d1c3f0117  # the merge of make-room-b: the last commit that held the moved code where it was
S="$here/skills/workflow-regression/scripts"; D="$here/skills/workflow-delivery/scripts"; R="$here/skills/workflow-release/scripts"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }
imp() { (cd "$1" && python3 -B -c "$2" 2>&1 | tail -1); }

if [ "$part" = all ] || [ "$part" = ids ]; then
echo "== run --ids: exactly its rows, as one lane"
"$here/dev/toy/make.sh" "$d" >/dev/null || exit 1
export LOOP_FLOW="$d/flow.json" PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh" TOY_LOG="$d/ran.log" LOOP_LANES_DIR="$d/lanes"
reg() { python3 "$S/regression.py" "$@"; }
cd "$d/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
mkdir -p dev src
for r in a b; do printf 'ok\n' > "src/$r.txt"; printf 'echo %s >> "$TOY_LOG"; grep -q ok src/%s.txt\n' "$r" "$r" > "dev/$r.sh"; done
printf '# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n' > .loop/regression.tsv
for r in a b; do printf '%s\tland\tbash dev/%s.sh\tX-1\t2026-01-01\t%s works.\tcriterion\t\n' "$r" "$r" "$r" >> .loop/regression.tsv; done
python3 -c "
import json; c=json.load(open('.loop/config.json')); c['min_free_memory_gb']=0; json.dump(c,open('.loop/config.json','w'))"
git add -A; git commit -qm "Rows"
common=$(cd "$(git rev-parse --git-common-dir)" && pwd)
: > "$TOY_LOG"; reg run land --reuse --tier goal >/dev/null 2>&1
printf 'ok 2\n' > src/a.txt; printf 'ok 2\n' > src/b.txt; git add -A; git commit -qm "Change both"
: > "$TOY_LOG"; before=$(git status --porcelain); out=$(reg run land --reuse --tier goal --ids a 2>&1); echo "$out" | tail -3
check "an ids lane runs only the rows it names" '[ "$(sort "$TOY_LOG" | tr "\n" " ")" = "a " ]'
check "an ids lane writes no tracked file" '[ "$(git status --porcelain)" = "$before" ]'
check "an ids lane keeps the branch lane record's other rows" 'python3 -c "
import json,glob
d=json.load(open(glob.glob(\"$common/loop/tests/main-*.json\")[0])); raise SystemExit(0 if sorted(d[\"rows\"])==[\"a\",\"b\"] else 1)"'
out=$(reg run land --reuse --ids zz 2>&1); check "an unknown id is refused, naming it" 'grep -q "^REFUSED: no row called zz\." <<<"$out"'
python3 -c "
import json; c=json.load(open('.loop/config.json')); c['min_free_memory_gb']=99999; json.dump(c,open('.loop/config.json','w'))"
git add -A; git commit -qm "Floor"; printf 'ok 3\n' > src/a.txt; git add -A; git commit -qm "Change a"
: > "$TOY_LOG"; out=$(LOOP_MEMORY_WAIT_SECONDS=2 reg run land --reuse --tier goal --ids a 2>&1); rc=$?; echo "$out" | tail -2
check "an ids lane takes the memory wait before any row runs (exit 6, nothing ran)" '[ $rc = 6 ] && grep -q "^MEMORY_WAIT: waited" <<<"$out" && [ ! -s "$TOY_LOG" ]'
python3 -c "
import json; c=json.load(open('.loop/config.json')); c['min_free_memory_gb']=0; json.dump(c,open('.loop/config.json','w'))"
out=$(LOOP_LANES_DIR=/dev/null/lanes reg run land --reuse --tier goal --ids a 2>&1 </dev/null)
check "an ids lane asks for a lane slot (the pool is tried before the rows run)" 'grep -q "LANE_SLOTS_UNAVAILABLE" <<<"$out"'
out=$(reg run a 2>&1 </dev/null); check "a plain row run, the comparison for the ids lane" '! grep -q "LANE_SLOTS" <<<"$out" && [ -n "$(git status --porcelain -- .loop/regression-runs.tsv)" ]'
cd "$here"
fi

if [ "$part" = all ] || [ "$part" = moves ]; then
echo "== the moves are whole functions, byte for byte, and every module imports"
check "row_reach.py, lanes.py and regression.py are under the caps (2,500 and 20,480 bytes)" '[ $(wc -c < "$S/row_reach.py") -lt 2500 ] && [ $(wc -c < "$S/lanes.py") -lt 20480 ] && [ $(wc -c < "$S/regression.py") -lt 20480 ]'
check "narrow.py is not edited (it keeps the bytes the base commit gave it)" '[ "$(git -C "$here" show $BASE:skills/workflow-regression/scripts/narrow.py | wc -c)" = "$(wc -c < "$S/narrow.py")" ]'
python3 -B - "$here" "$BASE" <<'PY' > "$d/moves.out" 2>&1
import ast, subprocess, sys
here, base = sys.argv[1], sys.argv[2]
def src(rev, rel):
    return subprocess.run(["git", "-C", here, "show", "%s:%s" % (base, rel)] if rev else ["cat", here + "/" + rel], capture_output=True, text=True).stdout
def nodes(text):
    out = {}
    for n in ast.parse(text).body:
        if isinstance(n, ast.FunctionDef): out[n.name] = ast.dump(n)
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name): out[n.targets[0].id] = ast.dump(n)
    return out
old_l, old_r = nodes(src(1, "skills/workflow-regression/scripts/lanes.py")), nodes(src(1, "skills/workflow-regression/scripts/regression.py"))
new_rr = nodes(src(0, "skills/workflow-regression/scripts/row_reach.py")); new_l = nodes(src(0, "skills/workflow-regression/scripts/lanes.py"))
bad = [k for k in ("PATH", "BARE", "ROOT", "SKILL_NAME", "HERE_FORMS", "CD_SKILLS", "widen", "references") if old_l.get(k) != new_rr.get(k)]
print("MOVED_RR_BAD", bad or "none")
print("MOVED_MERGED", "same" if old_r.get("merged") == new_l.get("merged") else "differs")
PY
cat "$d/moves.out"
check "references, its six regexes and widen are byte for byte what lanes.py held (same syntax tree)" 'grep -q "^MOVED_RR_BAD none" "$d/moves.out"'
check "merged is byte for byte what regression.py held, now in lanes.py" 'grep -q "^MOVED_MERGED same" "$d/moves.out"'
out=$(imp "$S" "import regression, lanes, row_reach; print(regression.merged is lanes.merged, lanes.references is row_reach.references, lanes.HERE_FORMS is row_reach.HERE_FORMS)")
check "the old names still resolve: regression.merged, lanes.references and lanes.HERE_FORMS (narrow.py reads it)" '[ "$out" = "True True True" ]'
ok_all=1; for m in "$S:regression" "$S:lanes" "$S:row_reach" "$S:narrow" "$S:completion" "$S:lanes_cli" "$D:lane" "$D:role" "$D:goal" "$D:flow" "$D:cover" "$R:merge"; do
  mod=${m#*:}; dir=${m%%:*}; cp -R "$dir" "$d/lone-$mod"; o=$(imp "$d/lone-$mod" "import $mod; print('ok')")
  [ "$o" = ok ] || { ok_all=0; echo "    $mod: $o"; }; rm -rf "$d/lone-$mod"; done
check "each entry point imports alone in a lone copy of its folder (12 isolated imports, one process each)" '[ $ok_all = 1 ]'
ok_all=1; for order in "lanes row_reach narrow" "narrow lanes" "row_reach lanes narrow" "completion lanes" "lane cover role" "role cover lane"; do
  mods=${order// /, }; dir=$S; case "$order" in "lane "*|"role "*) dir=$D;; esac
  o=$(imp "$dir" "import $mods; print('ok')"); [ "$o" = ok ] || { ok_all=0; echo "    $order: $o"; }; done
check "the cycle orders import (lanes, row_reach, narrow in each order; completion then lanes; lane, cover, role in each order)" '[ $ok_all = 1 ]'
cp -R "$S" "$d/fp"; a=$(imp "$d/fp" "import lanes; print(lanes.runner())"); printf '\n# x\n' >> "$d/fp/row_reach.py"; b=$(imp "$d/fp" "import lanes; print(lanes.runner())")
cp "$S/row_reach.py" "$d/fp/row_reach.py"; printf '\n# y\n' >> "$d/fp/completion.py"; c=$(imp "$d/fp" "import lanes; print(lanes.runner())")
check "changing only row_reach.py, or only completion.py, changes the runner fingerprint (cached plans and records are invalid)" '[ "$a" != "$b" ] && [ "$a" != "$c" ] && [ "$b" != "$c" ]'
o=$(cd "$d" && cp -R "$D" lonecover && cd lonecover && python3 -B cover.py --help 2>&1 | head -1); check "cover.py --help runs in a lone copy of its folder" 'grep -q "^usage: cover.py" <<<"$o"'
fi

if [ "$part" = all ] || [ "$part" = merge ]; then
echo "== a covered goal cannot join a batch; the PR body refresh refuses with BODY_STALE"
mkdir -p "$d/m/.loop" "$d/m/.git/loop/runs"; cd "$d/m" && git init -q -b main && git commit -q --allow-empty -m x
printf '{"auto_merge": true, "merge_batch": true, "base": "main"}' > .loop/config.json
printf '{"claim": {"name": "L1"}}' > .git/loop/runs/g1.cover.json
out=$(python3 "$R/merge.py" --batch g1 g2 2>&1 </dev/null); echo "$out" | head -2
check "a goal that ran with a cover is refused in a batch: COVER_NOBATCH names it and says merge it alone" 'grep -q "^REFUSED: g1 ran with a cover and cannot join a batch; merge it alone: merge.py SLUG (COVER_NOBATCH)\." <<<"$out"'
rm -f .git/loop/runs/g1.cover.json; out=$(python3 "$R/merge.py" --batch g1 g2 2>&1 </dev/null); check "a batch with no covered goal is not refused for a cover" '! grep -q "COVER_NOBATCH" <<<"$out"'
mkdir -p "$d/bin"; printf '#!/bin/bash\ncase "$1 $2" in\n  "pr view") echo "${FAKE_HEAD:-}";;\n  "pr edit") [ -f "$FAKE_DIR/fail" ] && { echo "edit refused" >&2; exit 1; }; echo edit >> "$FAKE_DIR/edits";;\nesac\n' > "$d/bin/gh"; chmod +x "$d/bin/gh"
H=$(cat <<'PYEND'
import json, os, sys
sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True
import cover
class G:
    class guards:
        @staticmethod
        def refuse_no_try(state, why, fix, code, save): print("REFUSED %s: %s | %s" % (code, why, fix)); raise SystemExit(5)
    state_path = staticmethod(lambda slug: os.environ["FAKE_DIR"] + "/" + slug)
    write = staticmethod(lambda p, t: open(p, "w").write(t))
    save = staticmethod(lambda *a: None)
state = {"slug": "g1", "branch": "feat", "pr_body_pushed": json.loads(sys.argv[2]) if sys.argv[2] != "none" else None}
cover.refresh(G, state, {"state": "OPEN", "url": "https://example.test/pull/1"}, "new body")
print("PUSHED", bool(state["pr_body_pushed"]))
PYEND
)
mkdir -p "$d/fake"; git -C "$d/m" checkout -q -b feat; git -C "$d/m" commit -q --allow-empty -m y; head=$(git -C "$d/m" rev-parse HEAD)
rb() { (cd "$d/m" && PATH="$d/bin:$PATH" FAKE_DIR="$d/fake" FAKE_HEAD="$head" python3 -B -c "$H" "$D" "$1" 2>&1); }
rm -f "$d/fake/fail" "$d/fake/edits"; out=$(rb '"old"'); check "an open PR whose body text changed is edited once and the new text is recorded" '[ "$(wc -l < "$d/fake/edits" | tr -d " ")" = 1 ] && grep -q "^PUSHED True" <<<"$out"'
: > "$d/fake/fail"; rm -f "$d/fake/edits"; out=$(rb '"old"'); echo "$out" | head -2
check "a failed edit refuses with BODY_STALE, the PR number in its words and goal.py pr as the fix" 'grep -q "^REFUSED BODY_STALE: the PR is open and its body is stale (PR https://example.test/pull/1) | goal.py pr g1 reruns the pr step: it re-syncs, may rerun the lane and push, then retries the edit" <<<"$out"'
rm -f "$d/fake/fail" "$d/fake/edits"; head=0000000000000000000000000000000000000000; out=$(rb '"old"')
check "a PR head that moved is not edited (no merge, lane or push: the body waits for the next pr run)" '[ ! -e "$d/fake/edits" ] && grep -q "the PR head moved" <<<"$out"'
fi
exit $((fails > 0))
