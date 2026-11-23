#!/bin/bash
# reads: dev/package.py skills/workflow-delivery/scripts/goal.py skills/workflow-delivery/scripts/flow.py
# reads: skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/autorelease.py
# reads: skills/workflow-docs/scripts/steps_page.py skills/steps.py skills/workflow-setup/scripts/update.py
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
# DEL-19 end-to-end (v110-fast-steps-2): the path an ADOPTER gets, not the repo's own tree. A built pack is unpacked and its scripts run
# in a toy repo with fakegh: the pack carries shared/steps.py and update.py keeps it; "no done line" and "skip the review" are refused
# with their own text; a stop before any pull request, a refusal after it, a goal left unreleased, a merge-queue merge and a release cut
# by hand each record their steps (every step that ran has a start and an end) and causes, which the summary job's step previews, one
# fix per cause, grouped with repeats. Filing ships off in v1.1.0: nothing is written to GitHub. Red on a tree without the build.
# usage: test-steps-e2e.sh
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH GH_TOKEN GITHUB_TOKEN CLAUDE_CODE_HOST_SESSION_ID CLAUDE_CODE_SESSION_ID CLAUDE_SESSION_ID LOOP_POD_ID
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID GITHUB_ACTIONS GITHUB_REF
export LOOP_ROLE=worker
export HOME=$(mktemp -d); export USERPROFILE="$HOME"
export LOOP_PRIVATE_NAMES=/dev/null  # exactly as CI does (o675); the list is never read or printed here
toy_on_exit 'rm -rf "$HOME"'
d=$(mktemp -d); toy_on_exit 'rm -rf "$d"'
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }

echo "== a built pack is what an adopter installs"
pack="$d/pack"; mkdir -p "$pack"
python3 "$here/dev/package.py" --root "$here" --out "$d/pack.zip" >"$d/package.log" 2>&1 && ok "the pack builds" || bad "the pack does not build: $(grep -m3 FAIL "$d/package.log" | tr '\n' ' ')"
[ -f "$d/pack.zip" ] && python3 -c 'import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$d/pack.zip" "$pack"
[ -f "$pack/shared/steps.py" ] && ok "the pack carries shared/steps.py" || bad "the pack has no shared/steps.py (SHARED in dev/package.py)"
python3 - "$here/skills/workflow-setup/scripts" <<'PY' && ok "update.py keeps skills/steps.py when it reads a tree" || bad "update.py drops skills/steps.py from an update"
import sys; sys.path.insert(0, sys.argv[1]); import update
names = ["skills/steps.py", "skills/x/scripts/a.py", "VERSION"]
manifest, _ = update.from_tree(names, lambda n: b"1.0.0\n" if n == "VERSION" else b"x")
sys.exit(0 if "steps.py" in manifest["files"] else 1)
PY
PK="$pack/skills"
goal="python3 $PK/workflow-delivery/scripts/goal.py"
flow="python3 $PK/workflow-delivery/scripts/flow.py"
filer="python3 $PK/workflow-docs/scripts/steps_page.py"
[ -f "$PK/workflow-delivery/scripts/goal.py" ] || { bad "no goal.py in the pack"; echo "$fails FAILED"; exit 1; }
python3 "$PK/workflow-delivery/scripts/goal.py" --help >/dev/null 2>&1 && ok "goal.py runs alone from the pack (its steps import resolves)" || bad "goal.py --help fails from the pack"

# One toy repo with a bare origin and fakegh (the same stand-ins the release toy uses).
"$here/dev/toy/make.sh" "$d/t" >/dev/null || exit 1
export LOOP_FLOW="$d/t/flow.json"
export PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh" FAKE_GH_ORIGIN="$d/t/origin.git"
cd "$d/t/repo" || exit 1
python3 "$PK/workflow-setup/scripts/setup.py" --bare >"$d/setup.log" 2>&1 || bad "setup.py from the pack: $(tail -2 "$d/setup.log" | tr '\n' ' ')"
git switch -q main 2>/dev/null; git merge -q --no-edit workflow-setup 2>/dev/null
python3 - <<'PY'
import json
c = json.load(open(".loop/config.json")); c["auto_merge"] = True
json.dump(c, open(".loop/config.json", "w"), indent=2)
PY
git add -A; git commit -qm "Setup and auto_merge" 2>/dev/null; git tag v0.1.0

writes() { grep -cE "pr create --draft|pr edit|pr ready|issue " "$FAKE_GH_DIR/calls.log" 2>/dev/null || true; }  # filing ships off: nothing but goal.py pr's own pull request may reach GitHub
preview() { (cd "$d/t/repo" && env -u LOOP_ROLE $filer file 2>&1); }  # the summary job's step: previews the causes the records hold, grouped by key
ran() { (cd "$d/t/repo" && python3 "$PK/workflow-docs/scripts/steps_page.py" show "$1" 2>/dev/null | awk -v n="$2" 'index($0, n) == 1 && $0 ~ / ran / && $0 !~ / start - / && $0 !~ / end - / {f=1} END {exit f ? 0 : 1}'); }
table() { (cd "$d/t/repo" && python3 "$PK/workflow-docs/scripts/steps_page.py" show "$1" 2>&1 | tr '\n' '|' | cut -c1-420); }
causes_of() { python3 -c 'import json, sys; print(len(json.load(open(sys.argv[1])).get("causes") or []))' "$(cd "$d/t/repo" && git rev-parse --git-common-dir)/loop/runs/$1.json" 2>/dev/null || echo 0; }
flowdone() {  # every step of a goal's flow, through the pack's flow.py, with the stand-in flow
  local slug=$1 runs; runs="$(cd "$(git rev-parse --git-common-dir)" && pwd)/loop/runs"
  for step in idea plan review qa ship; do
    for _ in $(seq 20); do
      out=$($flow "$slug" $step --wait 10) || return 1
      grep -q "^NEXT:" <<<"$out" && break
    done
    $goal record "$slug" $step --file "$runs/$slug.$step.txt" >/dev/null || return 1
  done
}
newgoal() {  # a goal with one commit, its verify steps and its flow done, then its pull request
  git switch -q main 2>/dev/null; git merge -q --no-edit "loop/$2" 2>/dev/null
  $goal new "$1" --here --goal "Goal $1" --done "calc has $1" >"$d/new.log" 2>&1 || { bad "goal new $1: $(tail -2 "$d/new.log" | tr '\n' ' ')"; return 1; }
  printf 'def g_%s():\n    return 1\n' "$1" > "g_$1.py"; git add "g_$1.py"; git commit -qm "$1"
  python3 - "$1" <<'PY'
import sys
p = ".loop/goals/%s.md" % sys.argv[1]; t = open(p).read().replace("## Verify by hand\n", "## Verify by hand\n\n1. Open calc.py.\n   Expect: it has the function.\n", 1); open(p, "w").write(t)
PY
  git commit -qam "Verify steps for $1"
  flowdone "$1" && ok "$1's flow ran" || bad "$1's flow"
  $goal pr "$1" >"$d/pr-$1.log" 2>&1 || bad "goal pr $1: $(tail -3 "$d/pr-$1.log" | tr '\n' ' ')"
}

echo "== DEL-19's own page tests, through the pack's entry points"
$goal new nodone --here --goal "A goal with no done line" >"$d/nodone.log" 2>&1 && bad "a goal with no done line was frozen" || { grep -q "no done lines" "$d/nodone.log" && ok "freezing a goal with no done line is refused (no done lines)" || bad "no-done refusal text missing: $(tail -1 "$d/nodone.log")"; }
git switch -q main 2>/dev/null
$goal new skipr --here --goal "A goal that skips its review" --done "calc has skipr" >/dev/null 2>&1 || bad "goal new skipr"
printf 'def g_skipr():\n    return 1\n' > g_skipr.py; git add g_skipr.py; git commit -qm skipr
$goal pr skipr >"$d/skipr.log" 2>&1 && bad "a goal that skipped its review opened its pull request" || { grep -q "the flow hasn.t finished" "$d/skipr.log" && ok "a goal that skips its review cannot open its pull request (the flow hasn't finished)" || bad "skip-review refusal text missing: $(tail -1 "$d/skipr.log")"; }
git switch -q main 2>/dev/null

echo "== a goal that stops before any pull request: its cause is recorded and previewed once, and nothing is written to GitHub"
$goal new prea --here --goal "Goal prea" --done "calc has prea" >"$d/new.log" 2>&1 || bad "goal new prea: $(tail -2 "$d/new.log" | tr '\n' ' ')"
printf 'def g_prea():\n    return 1\n' > g_prea.py; git add g_prea.py; git commit -qm "prea"
$goal finding prea "step build refused: no root cause" >"$d/find0.log" 2>&1
[ "$(causes_of prea)" -ge 1 ] && ok "the stop recorded a structured cause" || bad "prea: no cause in its record: $(tail -2 "$d/find0.log" | tr '\n' ' ')"
out=$(preview); [ "$(grep -c "^preview: .*prea" <<<"$out")" = 1 ] && ok "the cause is previewed exactly once, with its fix" || bad "prea previewed $(grep -c "prea" <<<"$out") times: $(head -2 <<<"$out" | tr '\n' ' ')"
[ "$(writes)" = 0 ] && ok "no pull request was drafted or edited and no issue was made" || bad "a stop wrote to GitHub: $(grep -E "pr create --draft|pr edit|issue " "$FAKE_GH_DIR/calls.log" | head -2 | tr '\n' ' ')"
git switch -q main 2>/dev/null

echo "== a refusal after the pull request is previewed once and grouped, and the release summary reaches the merged goal"
newgoal postb main
FAKE_GH_PR_STATE=OPEN FAKE_GH_MERGE_FAIL=1 python3 "$PK/workflow-release/scripts/merge.py" postb >/dev/null 2>&1
[ "$(causes_of postb)" -ge 1 ] && ok "the refused merge recorded a cause" || bad "postb: no cause recorded after the refusal"
out=$(preview); grep -q "merge:failed (1 goal: postb)" <<<"$out" && ok "the refusal is previewed once for its goal" || bad "postb's preview: $(head -3 <<<"$out" | tr '\n' ' ')"
FAKE_GH_PR_STATE=OPEN FAKE_GH_MERGE_BRANCH=loop/postb python3 "$PK/workflow-release/scripts/merge.py" postb >"$d/mergeb.log" 2>&1
ran postb "merge" && ran postb "after the merge" && ran postb "release" && ok "postb's merge, after the merge and release each have a start and an end" || bad "postb: a step has no start and end: $(table postb)"
grep -qF "### Steps" "$FAKE_GH_DIR/notes.log" 2>/dev/null && ok "the release note carries the per-step summary" || bad "the release note has no Steps summary: $(tail -2 "$d/mergeb.log" | tr '\n' ' ')"

echo "== a goal left unreleased: its merge row ends"
git switch -q main 2>/dev/null; newgoal leavd main
python3 "$PK/workflow-release/scripts/release.py" leave leavd >"$d/leave.log" 2>&1 || bad "release.py leave leavd: $(tail -2 "$d/leave.log" | tr '\n' ' ')"
ran leavd "merge" && ok "a goal left unreleased has its merge row ended" || bad "leavd: the merge row is not ended: $(table leavd)"

echo "== a release cut by hand carries the per-step summary"
git switch -q main 2>/dev/null; newgoal cutg main
python3 "$PK/workflow-release/scripts/release.py" cut cutg --user >"$d/cut.log" 2>&1; grep -qF "### Steps" "$FAKE_GH_DIR/notes.log" 2>/dev/null && ok "the manual cut's draft notes carry the Steps block" || bad "the manual cut has no Steps summary: $(tail -2 "$d/cut.log" | tr '\n' ' ')"

echo "== a merge-queue merge: its steps start and end, and a repeated cause is previewed grouped under one key"
python3 - <<'PY'
import json
c = json.load(open(".loop/config.json")); c["merge_queue"] = True
json.dump(c, open(".loop/config.json", "w"), indent=2)
PY
git add -A; git commit -qm "merge_queue on" 2>/dev/null
git switch -q main 2>/dev/null; newgoal queuec main
FAKE_GH_PR_STATE=OPEN FAKE_GH_MERGE_FAIL=1 python3 "$PK/workflow-release/scripts/merge.py" queuec >/dev/null 2>&1  # the queue first refuses once: that is the cause
FAKE_GH_QUEUE=1 FAKE_GH_PR_STATE=OPEN FAKE_GH_MERGE_BRANCH=loop/queuec python3 "$PK/workflow-release/scripts/merge.py" queuec >"$d/mergec.log" 2>&1
ran queuec "merge" && ran queuec "after the merge" && ran queuec "release" && ok "queuec's merge, after the merge and release each have a start and an end (merge queue)" || bad "queuec: a step has no start and end: $(table queuec)"
out=$(preview); [ "$(grep -c "merge:failed" <<<"$out")" = 1 ] && grep -q "merge:failed (2 goals: postb, queuec)" <<<"$out" && ok "a repeated cause is previewed once, grouped with its repeats" || bad "the grouping: $(grep "merge:failed" <<<"$out" | tr '\n' ' ')"
[ "$(writes)" = 0 ] && ok "no pull request was edited and no issue was made at any point" || bad "something was written to GitHub"

[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
