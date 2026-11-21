#!/bin/bash
# reads: skills/workflow-monitoring/scripts/machines.py skills/workflow-release/scripts/merge.py
# reads: skills/workflow-release/scripts/autorelease.py dev/toy/fakegh/gh
# reads: skills/
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
# Merge batching (merge-queue slice C): merge.py SLUG SLUG [SLUG] --batch merges up to 3 done goals whose own CI is green as one
# draft pull request of their combined head, binds the GO to that exact head's CI, and releases once. Off unless "merge_batch" is true.
# Value: protects=a batch never lands a head its CI did not run on, never takes a safety-class, major, conflicting or stale goal, and
# the single-goal merge is untouched; fails_when=a red or moved batch merges, a stale GO passes, a safety member is batched, or
# merge.py SLUG behaves differently with batching off; why_new=merges went one goal at a time; seam=none;
# no_claim=GitHub's own merge and the release itself (autorelease.finish is stubbed here and covered by its own toys)
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION
export HOME=$(mktemp -d) PATH="$here/dev/toy/fakegh:$PATH"
export USERPROFILE="$HOME"
export GIT_AUTHOR_NAME=Toy GIT_AUTHOR_EMAIL=t@example.test GIT_COMMITTER_NAME=Toy GIT_COMMITTER_EMAIL=t@example.test
d=$(mktemp -d); toy_on_exit 'rm -rf "$d" "$HOME"'
export FAKE_GH_DIR="$d/gh"; mkdir -p "$FAKE_GH_DIR"
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; echo "    out: ${out:-}"; fi; }
git init -q --bare -b main "$d/origin.git"
n="$d/repo"; git clone -q "$d/origin.git" "$n" 2>/dev/null; cd "$n"
mkdir -p src .loop
for f in a b c d e f g; do printf '%s\n' "$f" > "src/$f.txt"; done
printf '{"auto_merge": true, "base": "main"}\n' > .loop/config.json
git add -A; git commit -qm base; git push -q origin main
branch() {  # SLUG FILE: a goal branch from main that edits FILE
  git switch -q -c "loop/$1" main; echo "$1" >> "src/$2.txt"; git commit -qam "goal $1"; git push -q origin "loop/$1"; git switch -q main; }
branch g1 a; branch g2 b; branch g3 a; branch g4 c; branch g5 d; branch g6 e; branch g7 f
common=$(cd "$(git rev-parse --git-common-dir)" && pwd); mkdir -p "$common/loop/runs"
M="$here/skills/workflow-release/scripts"
ok1='[{"name":"suite","status":"COMPLETED","conclusion":"SUCCESS"}]'
red1='[{"name":"suite","status":"COMPLETED","conclusion":"FAILURE"}]'
i=20
for s in g1 g2 g3 g4 g5 g6 g7; do  # a finished goal with its own pull request (#21...) and its own green CI
  i=$((i + 1)); h=$(git rev-parse "loop/$s")
  printf '{"slug": "%s", "status": "done", "pr": "https://example.test/pull/%d", "branch": "loop/%s", "pr_head": "%s", "goal": "goal %s", "release_bullets": ["Change %s"]}\n' \
    "$s" $i "$s" "$h" "$s" "$s" > "$common/loop/runs/$s.json"
  export "FAKE_GH_PR_HEAD_$i=$h" "FAKE_GH_ROLLUP_$i=$ok1"
done
heads=$(git rev-parse origin/main)
mk() { python3 - "$common/loop/runs/$1.json" "$2" "$3" <<'PY'  # SLUG KEY JSON: set one field of a run record
import json, sys
path = sys.argv[1]; state = json.load(open(path)); state[sys.argv[2]] = json.loads(sys.argv[3]); json.dump(state, open(path, "w"))
PY
}
# the driver: runs machines.batch in-process against the real git and the fake gh, with the release itself stubbed
drive() { python3 -B - "$here" "$n" "$common" "$@" <<'PY'
import contextlib, io, json, os, sys
here, top, common, slugs, go = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(","), sys.argv[5] or None
os.chdir(top)
sys.path[:0] = [os.path.join(here, "skills", d, "scripts") for d in ("workflow-release", "workflow-monitoring")]
import merge, machines
merge.release.auto_need = lambda t, s: (s["bump"] if s.get("bump") in ("minor", "major") else "patch", "toy")
calls = []
def finish(t, cfg, lead):
    calls.append(lead["slug"]); lead.update(release="cut", release_version="9.9.9", release_url="https://example.test/r/9", release_pushed="9.9.9")
    merge.release.save(lead); return True
merge.ar.finish = finish
cfg = {"base": "main", "merge_batch": True}
out, err = io.StringIO(), io.StringIO()
with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
    try:
        rc = machines.batch(top, common, cfg, slugs, go, merge)
    except SystemExit as stop:
        rc = stop.code if isinstance(stop.code, int) else 2
        print(stop.code if not isinstance(stop.code, int) else "")
print("RC=%s FINISH=%d" % (rc, len(calls)))
print(out.getvalue() + err.getvalue())
PY
}
calls() { cat "$FAKE_GH_DIR/calls.log" 2>/dev/null; }
rec() { python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2], ''))" "$common/loop/batches/$1.json" "$2"; }
bid() { python3 -c "import hashlib,sys; print(hashlib.sha1(','.join(sorted(sys.argv[1].split(','))).encode()).hexdigest()[:8])" "$1"; }

# 1. batching is off by default: through merge.py itself, nothing is merged and no draft is made
out=$(python3 "$M/merge.py" g1 g2 --batch 2>&1); rc=$?
check "batching off by default: g1 g2 --batch refuses naming merge_batch (exit 1) and opens nothing" '[ $rc != 0 ] && grep -q "merge_batch" <<<"$out" && ! calls | grep -q "pr create"'
out=$(python3 "$M/merge.py" g1 g2 2>&1); rc=$?
check "two goals without --batch refuse; nothing is merged" '[ $rc != 0 ] && grep -q "merge_batch" <<<"$out" && ! calls | grep -q "pr merge"'
printf '{"auto_merge": true, "base": "main", "merge_batch": true}\n' > .loop/config.json
out=$(python3 "$M/merge.py" g1 --batch 2>&1); rc=$?
check "a batch of one goal refuses: 2 or 3 goals" '[ $rc != 0 ] && grep -q "2 or 3 goals" <<<"$out"'
out=$(python3 "$M/merge.py" g1 g2 g3 g4 --batch 2>&1); rc=$?
check "a batch of four goals refuses: 2 or 3 goals" '[ $rc != 0 ] && grep -q "2 or 3 goals" <<<"$out"'
printf '{"auto_merge": true, "base": "main"}\n' > .loop/config.json

# 2. the single-goal path is the same with batching off: the previous merge.py and this one answer the same refusals
old="$d/oldskills"; mkdir -p "$old"; cp -R "$here/skills/." "$old/"
git -C "$here" show origin/main:skills/workflow-release/scripts/merge.py > "$old/workflow-release/scripts/merge.py"
head=$(git rev-parse loop/g1)
for variant in "--go-head deadbeefdeadbeef" "--go-head ${head:0:12}"; do
  a=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$head FAKE_GH_ROLLUP="$ok1" python3 "$M/merge.py" g1 $variant 2>&1; echo "rc=$?")
  printf '{"slug": "g1", "status": "done", "pr": "https://example.test/pull/21", "branch": "loop/g1", "pr_head": "%s", "goal": "goal g1", "release_bullets": ["Change g1"]}\n' "$head" > "$common/loop/runs/g1.json"
  b=$(FAKE_GH_PR_STATE=OPEN FAKE_GH_PR_HEAD=$head FAKE_GH_ROLLUP="$ok1" python3 "$old/workflow-release/scripts/merge.py" g1 $variant 2>&1; echo "rc=$?")
  a=${a//$here/@}; b=${b//$old/@}; out="new: $a / old: $b"
  check "merge.py g1 $variant answers byte for byte as before (batching off)" '[ "$a" = "$b" ]'
  printf '{"slug": "g1", "status": "done", "pr": "https://example.test/pull/21", "branch": "loop/g1", "pr_head": "%s", "goal": "goal g1", "release_bullets": ["Change g1"]}\n' "$head" > "$common/loop/runs/g1.json"
done

# 3. a batch of g1 g3 g2: g3 conflicts with g1 and goes alone; g4 (safety) and g7 (major) never batch
mk g4 safety true; mk g7 bump '"major"'; mk g5 bump '"minor"'
out=$(drive g4,g5 ""); check "a safety-class goal is never batched: ALONE, and one goal left is BATCH_NONE (exit 4); nothing pushed or opened" \
  'grep -q "^ALONE g4: safety class" <<<"$out" && grep -q "RC=4" <<<"$out" && grep -q "BATCH_NONE" <<<"$out" && ! calls | grep -q "pr create" && ! git ls-remote origin "refs/heads/batch/*" | grep -q .'
mk g4 safety false; mk g4 release '"ask"'
out=$(drive g4,g5 ""); check "a goal the owner marked (release ask) is never batched" 'grep -q "^ALONE g4: safety class" <<<"$out" && grep -q "BATCH_NONE" <<<"$out"'
mk g4 release '"merged"'; mk g4 release 'null'
out=$(drive g7,g5 ""); check "a major bump is removed from the batch: the owner cuts it" 'grep -q "^ALONE g7: major bump" <<<"$out" && grep -q "BATCH_NONE" <<<"$out"'
export FAKE_GH_ROLLUP_24="$red1"
out=$(drive g4,g5 ""); check "a member whose own CI is red goes alone (CI_RED) and is not batched" 'grep -q "^ALONE g4: .*CI_RED" <<<"$out" && grep -q "BATCH_NONE" <<<"$out"'
export FAKE_GH_ROLLUP_24="$ok1"
export FAKE_GH_PR_HEAD_25=0000000000000000000000000000000000000000
out=$(drive g4,g5 ""); check "a member whose head moved since its lane goes alone and is not batched" 'grep -q "^ALONE g5: its head moved" <<<"$out" && grep -q "BATCH_NONE" <<<"$out"'
export FAKE_GH_PR_HEAD_25=$(git rev-parse loop/g5)
out=$(drive g1,g3,g2 ""); b=$(bid g1,g2)
check "g3 conflicts with g1: it goes alone, g1 and g2 are batched on a draft PR of their combined head" \
  'grep -q "^ALONE g3: conflicts" <<<"$out" && grep -q "RC=0" <<<"$out" && [ "$(rec $(bid g1,g3,g2) phase)" = assembled ] && calls | grep -q "pr create --draft"'
b=$(bid g1,g3,g2); bh=$(rec "$b" head); pr=$(rec "$b" pr); pn=${pr##*/}
check "the batch head holds both goals and not the conflicting one, on origin as batch/<id>" \
  '[ "$(git rev-parse origin/main)" = "$heads" ] && git fetch -q origin "batch/$b" && [ "$(git rev-parse FETCH_HEAD)" = "$bh" ] && git show "$bh:src/a.txt" | grep -q g1 && git show "$bh:src/b.txt" | grep -q g2 && ! git show "$bh:src/a.txt" | grep -q g3'
check "the record names the kept goals in queue order" '[ "$(python3 -c "import json;print(*json.load(open(\"$common/loop/batches/$b.json\"))[\"slugs\"])")" = "g1 g2" ]'
export FAKE_GH_PR_HEAD_$pn=$bh FAKE_GH_ROLLUP_$pn="$ok1"
out=$(drive g1,g3,g2 ""); check "with the draft's CI green and no GO, the batch only reports green (no merge)" 'grep -q "RC=0" <<<"$out" && grep -q "is green" <<<"$out" && ! calls | grep -q "pr merge"'
out=$(drive g1,g3,g2 "deadbeefdeadbeef"); check "a GO for a stale sha refuses GO_HEAD (exit 4); nothing merged" 'grep -q "RC=4" <<<"$out" && grep -q "GO_HEAD" <<<"$out" && ! calls | grep -q "pr merge"'
export FAKE_GH_PR_HEAD_$pn=1111111111111111111111111111111111111111
out=$(drive g1,g3,g2 "${bh:0:12}"); check "a draft whose head moved after assembly refuses BATCH_MOVED (exit 4); nothing merged" 'grep -q "RC=4" <<<"$out" && grep -q "BATCH_MOVED" <<<"$out" && ! calls | grep -q "pr merge"'
export FAKE_GH_PR_HEAD_$pn=$bh FAKE_GH_ROLLUP_$pn="$red1"
out=$(drive g1,g3,g2 "${bh:0:12}"); check "a red batch is dissolved to singles: BATCH_RED (exit 5), the draft closed, nothing merged" \
  'grep -q "RC=5" <<<"$out" && grep -q "BATCH_RED" <<<"$out" && calls | grep -q "pr close $pr --delete-branch" && ! calls | grep -q "pr merge" && [ "$(rec $b phase)" = dissolved ]'
out=$(drive g1,g3,g2 "${bh:0:12}"); check "a dissolved batch stays dissolved: merge each goal alone, nothing merged" 'grep -q "RC=5" <<<"$out" && grep -q "dissolved" <<<"$out" && ! calls | grep -q "pr merge"'
check "after the red batch both goals are still open and unreleased (each merges alone through merge.py SLUG)" \
  '[ "$(python3 -c "import json;print(json.load(open(\"$common/loop/runs/g1.json\")).get(\"release\"))")" = None ]'

# 4. a green batch, a right GO: one merge of the draft, one release for the whole batch
out=$(drive g2,g5 ""); b2=$(bid g2,g5); bh2=$(rec "$b2" head); pr2=$(rec "$b2" pr); pn2=${pr2##*/}
check "a second batch g2 g5 is assembled" 'grep -q "RC=0" <<<"$out" && [ "$(rec $b2 phase)" = assembled ]'
export FAKE_GH_PR_HEAD_$pn2=$bh2 FAKE_GH_ROLLUP_$pn2="$ok1" FAKE_GH_MERGE_BRANCH="batch/$b2" FAKE_GH_ORIGIN="$d/origin.git"
out=$(drive g2,g5 "${bh2:0:12}")
check "a GO on the draft's green head merges the draft with the head bound, and releases once" \
  'grep -q "RC=0" <<<"$out" && grep -q "FINISH=1" <<<"$out" && calls | grep -q "pr ready $pr2" && calls | grep -q "pr merge $pr2 --merge --match-head-commit $bh2" && [ "$(rec $b2 phase)" = released ]'
check "the bump is the largest of the members (minor), carried by the goal that releases" '[ "$(python3 -c "import json;print(json.load(open(\"$common/loop/runs/g2.json\")).get(\"bump\"))")" = minor ]'
check "every member shows the one release and is marked merged" \
  'for s in g2 g5; do python3 -c "import json,sys; s=json.load(open(sys.argv[1])); sys.exit(0 if s.get(\"release_version\")==\"9.9.9\" and s.get(\"status\")==\"done\" else 1)" "$common/loop/runs/$s.json" || exit 1; done'
check "the release notes carry every member's change once" \
  'python3 -c "import json,sys; b=json.load(open(sys.argv[1]))[\"release_bullets\"]; sys.exit(0 if b==[\"Change g2\",\"Change g5\"] else 1)" "$common/loop/runs/g2.json"'
out=$(drive g2,g5 "${bh2:0:12}"); check "running the released batch again changes nothing: ALREADY merged, no second release" 'grep -q "RC=0" <<<"$out" && grep -q "FINISH=0" <<<"$out" && [ "$(calls | grep -c "pr merge $pr2")" = 1 ]'
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
