#!/bin/bash
# reads: skills/workflow-delivery/scripts/goal.py skills/workflow-health/scripts/health.py
# reads: skills/workflow-health/scripts/milestone.py skills/workflow-setup/scripts/setup.py
# reads: skills/workflow-health/scripts/
# Test that milestones are optional and free form (owner commands, none per feature, none on a pull request or an issue
# health files), the feature tag always on, and that setup asks for none, on a toy repo with a fake gh. usage: test-milestones.sh [DIR]
set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION  # a toy test never reaches a real session tool
export LOOP_ROLE=worker  # goal.py and flow.py run only in a worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d)  # setup.py writes the private settings under HOME
export USERPROFILE="$HOME"
d=${1:-$(mktemp -d)}; rm -rf "$d"; mkdir -p "$d"
"$here/dev/toy/make.sh" "$d" || exit 1
export LOOP_FLOW="$d/flow.json"
export PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh"
unset GH_TOKEN GITHUB_TOKEN
ms="python3 $here/skills/workflow-health/scripts/milestone.py"
health="python3 $here/skills/workflow-health/scripts/health.py"
goal="python3 $here/skills/workflow-delivery/scripts/goal.py"
cd "$d/repo" || exit 1
setup_out=$(python3 "$here/skills/workflow-setup/scripts/setup.py" --bare 2>&1)
git switch -q main; git merge -q --no-edit workflow-setup
printf 'Calc\tskills/x\nHome\tREADME.md\n' > .loop/docs.tsv
mkdir -p docs/wiki; printf '<!-- workflow-docs -->\n# Calc\n' > docs/wiki/Calc.md
git add -A; git commit -qm "Map the Calc page"; git push -q origin main
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
calls() { grep -c "$1" "$FAKE_GH_DIR/calls.log" 2>/dev/null || true; }
mkdir -p "$FAKE_GH_DIR"

echo "== setup asks for no milestone"
f0=$fails
! grep -qi "milestone" <<<"$setup_out" && ! git ls-files | xargs grep -li "milestone" 2>/dev/null | grep -q . && ok "setup's plan, NEXT line and files mention no milestone" || bad "setup mentions a milestone: $setup_out"
grep -q "^NEXT: review the branch, then merge it into main$" <<<"$setup_out" && ok "setup's NEXT line is only to review and merge" || bad "setup NEXT: $setup_out"
[ "$fails" = "$f0" ] && echo "PASS milestone-freeform:setup-no-milestone-step"

echo "== milestone.py: free form, named by the owner, created once"
f0=$fails
out=$($ms new v1.0); echo "$out"
[ "$out" = "WOULD create milestone v1.0 (dry run; add --live)" ] && [ ! -f "$FAKE_GH_DIR/milestones.json" ] && ok "without --live it only prints the WOULD line" || bad "dry run"
out=$($ms new v1.0 --live); echo "$out"
[ "$out" = "CREATED v1.0" ] && ok "new v1.0 --live creates it" || bad "created"
out=$($ms new v1.0 --live); echo "$out"
[ "$out" = "EXISTS v1.0" ] && [ "$(calls 'milestones -f title')" = 1 ] && ok "running it again creates nothing" || bad "idempotent"
[ "$($ms new backlog --live)" = "CREATED backlog" ] && [ "$($ms new Calc --live)" = "CREATED Calc" ] && ok "backlog and a page name are ordinary titles, nothing is refused as not a feature" || bad "ordinary titles"
out=$(FAKE_GH_NO_AUTH=1 $ms new v2.0 --live 2>&1); rc=$?
[ $rc = 1 ] && grep -q "^REFUSED: no GitHub token, nothing created. Fix: set GH_TOKEN or run gh auth login, or drop --live to preview.$" <<<"$out" && ! grep -q "title=v2.0" "$FAKE_GH_DIR/calls.log" && ok "--live with no token refuses with the fix and creates nothing" || bad "no token: $out"
for removed in "new --all" "features" "attach calc-goal"; do
  out=$($ms $removed 2>&1); rc=$?
  [ $rc = 1 ] && [ "$(wc -l <<<"$out" | tr -d ' ')" = 1 ] && grep -q "^REFUSED: .* was removed, milestones are free form. Fix: drop the call.$" <<<"$out" || bad "removed: $removed -> $out"
done
ok "the removed new --all, features and attach each refuse in one line, never a traceback"
out=$(bash -c "$ms new --all --live || echo '::warning::an old workflow step'" 2>&1); rc=$?
[ $rc = 0 ] && grep -q "REFUSED" <<<"$out" && ok "an older workflow's step (milestone.py new --all --live || echo warning) still exits 0" || bad "stale step"
[ "$fails" = "$f0" ] && echo "PASS milestone-freeform:milestones-once"

echo "== v1.0 works as before: an issue on it, grouped by feature, never made a feature by the milestone"
f0=$fails
gh issue create --title "Plan a thing" --label health --body "x" >/dev/null
out=$($ms move 1 v1.0); echo "$out"
grep -q "^WOULD move issue 1 to milestone v1.0 (dry run; add --live)$" <<<"$out" && ok "move without --live only prints" || bad "move dry"
out=$($ms move 1 v1.0 --live); echo "$out"
[ "$out" = "MOVED issue 1 to milestone v1.0" ] && [ "$(python3 -c "import json,os;print(json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json'))[0]['milestone']['title'])")" = v1.0 ] && ok "move puts the issue on the milestone" || bad "move"
out=$($ms move 1 v9 --live 2>&1); rc=$?
[ $rc = 1 ] && grep -q "^REFUSED: no milestone v9 (issue 1 unchanged). Fix: milestone.py new v9 --live$" <<<"$out" && ok "an unknown title refuses, the issue unchanged" || bad "move unknown: $out"
out=$($ms move 1 none --live); [ "$out" = "MOVED issue 1 to no milestone" ] && [ "$(python3 -c "import json,os;print(json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json'))[0]['milestone'])")" = None ] && ok "move to none clears it" || bad "move none"
$ms move 1 v1.0 --live >/dev/null
got=$(python3 - "$here" <<'PY'
import os, sys
sys.path.insert(0, os.path.join(sys.argv[1], "skills", "workflow-health", "scripts"))
import issues as I
pages = {"Calc": ["skills/x"]}
print(I.feature_group({"labels": [], "milestone": "v1.0"}, pages), I.feature_group({"labels": [], "milestone": "Backlog"}, pages),
      I.feature_group({"labels": [], "milestone": None}, pages), I.feature_group({"labels": [], "milestone": "Calc"}, pages),
      I.feature_group({"labels": ["feature:calc"], "milestone": "v1.0"}, pages), I.feature_group({"labels": ["feature:" + "x" * 42], "milestone": None}, {"x" * 50: [], "x" * 49: []}))
PY
)
[ "$got" = "No feature No feature No feature Calc Calc No feature" ] && ok "an issue on v1.0, on Backlog or on none is No feature; a page-named milestone or a feature label groups as that page; two pages sharing a label are No feature" || bad "grouping: $got"
python3 -c "
import sys; sys.path.insert(0, '$here/skills/workflow-health/scripts'); import issues as I
f = lambda n: I.feature_label('p' * n)
assert len(f(42)) == 50 and len(f(43)) == 50 and f(42) == f(43), (len(f(42)), len(f(43)))
assert I.feature_label('A,b\nc\x00d') == 'feature:Abcd'" && ok "a feature label cuts the page name at 42 characters (the whole label at most 50) and drops commas and control characters" || bad "label length"
out=$($health triage); echo "$out"
grep -q "^== No feature: 1 ==" <<<"$out" && ok "triage lists the issue on v1.0 under No feature, with no complaint about a milestone" || bad "triage: $out"
[ "$fails" = "$f0" ] && echo "PASS milestone-freeform:milestone-v1-free-form"

echo "== goal.py pr puts the pull request in no milestone"
f0=$fails
$goal new calc-goal --here --goal "Change calc" --done "calc changes" --touches "calc.py" >/dev/null
echo "# change" >> calc.py; git commit -qam "Change calc"
python3 - <<'PYEND'
p = ".loop/goals/calc-goal.md"
t = open(p).read().replace("## Verify by hand\n", "## Verify by hand\n\n1. Open calc.py.\n   Expect: the change.\n", 1)
open(p, "w").write(t)
PYEND
git commit -qam "Verify steps"
: > "$FAKE_GH_DIR/calls.log"
bash "$here/dev/toy/flow-done.sh" calc-goal; out=$($goal pr calc-goal 2>&1); echo "$out"
grep -q "^PR https://example.test/pull/1$" <<<"$out" && ok "goal.py pr opens the pull request" || bad "pr: $out"
! grep -qi "milestone" "$FAKE_GH_DIR/calls.log" && ! grep -q "^pr edit" "$FAKE_GH_DIR/calls.log" && [ ! -f "$FAKE_GH_DIR/pr-milestone-1" ] && ! grep -qi "milestone" <<<"$out" \
  && ok "no milestone is read, made or set for the pull request" || bad "pr milestone: $(cat "$FAKE_GH_DIR/calls.log")"
[ "$fails" = "$f0" ] && echo "PASS milestone-freeform:pr-no-milestone"

echo "== health file: one tagged issue per finding, a WARN a backlog item on its Backlog milestone"
rm -f "$FAKE_GH_DIR/issues.json"; f0=$fails; git switch -q main
printf '<!-- workflow-docs -->\n# Calc\n\nThe calculator adds and prints the sum of the numbers given on the line.\n' > docs/wiki/Calc.md
printf '<!-- workflow-docs -->\n# Home\n\nThe toy repo holds one feature, the calculator, and this page says so.\n' > docs/wiki/Home.md
mkdir -p skills/x/scripts; printf '# calc\n' > skills/x/scripts/calc.py; git add -A; git commit -qm "Pages and code"
echo 'X = 1' >> skills/x/scripts/calc.py  # Calc's page goes stale: a Docs WARN (principle 5 retired the size rule, o988)
git commit -qam "Change calc"
out=$($health preview --group docs); echo "$out"
grep -q "^WOULD open issue 'health: docs Calc stale' \[health:docs, feature:Calc\] as backlog on Backlog: Calc$" <<<"$out" && [ ! -f "$FAKE_GH_DIR/issues.json" ] \
  && ok "preview: only WOULD lines, nothing written" || bad "run dry"
: > "$FAKE_GH_DIR/calls.log"; out=$($health file --group docs); echo "$out"
[ -s "$FAKE_GH_DIR/calls.log" ] || bad "FAIL milestone-freeform:health-file: calls.log absent, real gh may have run. Fix: put dev/toy/fakegh first on PATH"
python3 - <<'PYEND' && ok "file: one backlog issue on Backlog: Calc, labelled, with the hidden marker" || bad "issue created"
import json, os, re
issues = json.load(open(os.environ["FAKE_GH_DIR"] + "/issues.json"))
assert len(issues) == 1 and issues[0]["milestone"]["title"] == "Backlog: Calc", issues
assert "backlog" in [l["name"] for l in issues[0]["labels"]], issues[0]["labels"]
assert re.search(r"<!-- loop-health docs:Calc:stale evidence=[0-9a-f]{8} placed= -->", issues[0]["body"])
PYEND
grep -q -e "--label health --label health:docs --label backlog --label feature:Calc --milestone Backlog: Calc --body" "$FAKE_GH_DIR/calls.log" && grep -q -e "^api repos/{owner}/{repo}/milestones -f title=Backlog: Calc$" "$FAKE_GH_DIR/calls.log" && ok "labelled health, health:docs, backlog and its feature, on Backlog: Calc made first: the feature label even while feature_labels is off" || bad "label: $(cat "$FAKE_GH_DIR/calls.log")"
out=$($health file --group docs); echo "$out"
grep -q "^SAME #1" <<<"$out" && [ "$(python3 -c "import json,os;print(len(json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json'))))")" = 1 ] && ok "a repeat opens no second issue" || bad "duplicate"
echo 'Y = 2' >> skills/x/scripts/calc.py; git commit -qam "Bigger"
out=$($health file --group docs); echo "$out"
grep -q "^DONE update #1" <<<"$out" && ok "a changed finding updates its issue" || bad "update"
python3 - <<'PYEND'
import json, os, re
p = os.environ["FAKE_GH_DIR"] + "/issues.json"; issues = json.load(open(p))
issues[0]["body"] = re.sub(r"<!-- loop-health \S+ evidence=\w+ placed=\S* -->", "<!-- loop-health docs:Calc:stale -->", issues[0]["body"])
json.dump(issues, open(p, "w"))
PYEND
out=$($health file --group docs); echo "$out"
python3 - <<'PYEND' && grep -q "^DONE update #1 docs:Calc:stale" <<<"$out" && ! grep -q "^DONE \(open\|close\)" <<<"$out" && ok "an old-form marker (no evidence) is moved to the new form, not closed or duplicated" || bad "marker migrate"
import json, os
issues = json.load(open(os.environ["FAKE_GH_DIR"] + "/issues.json"))
assert len(issues) == 1 and issues[0]["state"] == "OPEN" and "docs:Calc:stale evidence=" in issues[0]["body"], issues
PYEND

echo "== an issue the owner put on a milestone stays there"
$ms new Sprint --live >/dev/null; $ms move 1 Sprint --live | grep -q "^MOVED issue 1 to milestone Sprint" && ok "the owner moves the issue to a milestone of their own" || bad "move"
echo 'Z = 3' >> skills/x/scripts/calc.py; git commit -qam "Bigger again"
: > "$FAKE_GH_DIR/calls.log"; out=$($health file --group docs); echo "$out"
python3 - <<'PYEND' && ! grep -q "milestone" "$FAKE_GH_DIR/calls.log" && ok "a later run updates the issue where the owner put it, touches no milestone, and opens no other" || bad "moved"
import json, os
issues = json.load(open(os.environ["FAKE_GH_DIR"] + "/issues.json"))
assert len(issues) == 1 and issues[0]["milestone"]["title"] == "Sprint", issues
PYEND

echo "== the feature tag: always on, whatever feature_labels says"
grep -q '"name": "feature:Calc"' "$FAKE_GH_DIR/issues.json" && ok "with the switch off the issue carries its feature tag" || bad "tag off"
python3 -c "import json; c = json.load(open('.loop/config.json')); c['feature_labels'] = True; json.dump(c, open('.loop/config.json', 'w'), indent=2)"
out=$($health preview --group docs); echo "$out"
! grep -q "^WOULD update #1" <<<"$out" && ok "turning the switch on changes nothing: the tag is already there" || bad "tag on: $out"
python3 - <<'PYEND'
import json, os
p = os.environ["FAKE_GH_DIR"] + "/issues.json"; issues = json.load(open(p))
for i in issues:
    i["labels"] = [l for l in i["labels"] if not l["name"].startswith("feature:")]
json.dump(issues, open(p, "w"))
PYEND
: > "$FAKE_GH_DIR/calls.log"; out=$($health file --group docs); echo "$out"
grep -q "^label create feature:Calc --description Filed by health.py file --force" "$FAKE_GH_DIR/calls.log" && grep -q -- "--add-label feature:Calc" "$FAKE_GH_DIR/calls.log" \
  && grep -q '"name": "feature:Calc"' "$FAKE_GH_DIR/issues.json" && ok "the label is made first, and a repeat run adds it to the old issue" || bad "backfill: $(cat "$FAKE_GH_DIR/calls.log")"
python3 -c "import json; c = json.load(open('.loop/config.json')); c['feature_labels'] = False; json.dump(c, open('.loop/config.json', 'w'), indent=2)"
: > "$FAKE_GH_DIR/calls.log"; out=$($health file --group docs); echo "$out"
grep -q "^label create feature:Calc" "$FAKE_GH_DIR/calls.log" && grep -q '"name": "feature:Calc"' "$FAKE_GH_DIR/issues.json" && ok "with the switch off again the feature label is still made and kept" || bad "off again"


echo "== fixed closes, returning reopens"
echo 'The page now covers the change.' >> docs/wiki/Calc.md; git commit -qam "Fix the page"
out=$($health file --group docs); echo "$out"
grep -q "^DONE close #1 docs:Calc:stale" <<<"$out" && grep -q '"state": "CLOSED"' "$FAKE_GH_DIR/issues.json" && ok "a fixed finding closes its issue" || bad "close"
echo 'W = 4' >> skills/x/scripts/calc.py; git commit -qam "Back again"
out=$($health file --group docs); echo "$out"
grep -q "^DONE reopen #1" <<<"$out" && grep -q '"state": "OPEN"' "$FAKE_GH_DIR/issues.json" && [ "$(python3 -c "import json,os;print(len(json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json'))))")" = 1 ] \
  && ok "a returning finding reopens the same issue" || bad "reopen"
grep -Eq "^(release |pr merge|api .*-X)|draft=false" "$FAKE_GH_DIR/calls.log" && bad "publish or merge call" || ok "no release or merge call"

[ "$fails" = "$f0" ] && echo "PASS milestone-freeform:health-file-no-milestone"

echo "== a group run or an unread rule closes nothing it did not check"
printf '# Findings\n\n- f0: open\n- f1: open\n- f2: open\n- f3: open\n- f4: open\n- f5: open\n' > .loop/findings.md; git add -A; git commit -qm "Six open findings"  # a hygiene issue to guard
out=$($health file --group criteria,hygiene,performance); echo "$out" | grep -c "^DONE" 
open_other=$(python3 -c "import json,os;print(sorted(i['number'] for i in json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json')) if i['state']=='OPEN' and 'docs:' not in i['body']))")
[ "$open_other" != "[]" ] && ok "other families have open issues: $open_other" || bad "no other issues to guard"
echo 'And the page covers it again.' >> docs/wiki/Calc.md; git commit -qam "Fix the page again"
$health file --group docs >/dev/null
still=$(python3 -c "import json,os;print(sorted(i['number'] for i in json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json')) if i['state']=='OPEN' and 'docs:' not in i['body']))")
[ "$still" = "$open_other" ] && grep -q '"number": 1, .*"state": "CLOSED"' "$FAKE_GH_DIR/issues.json" && ok "file --group docs closed only the docs issue" || bad "family close: $still"
lone=$(mktemp -d); cp "$here/skills/workflow-health/scripts/health.py" "$lone/"
n=$(wc -l < "$FAKE_GH_DIR/calls.log")
python3 "$lone/health.py" file --group criteria,docs >/dev/null 2>&1; rc=$?
[ $rc = 2 ] && [ "$(wc -l < "$FAKE_GH_DIR/calls.log")" = "$n" ] && ok "a lone health.py has no file command and calls no gh" || bad "lone file"
nofile=$(mktemp -d); cp -R "$here/skills/workflow-health/scripts/." "$nofile/"; rm -f "$nofile/file.py"
out=$(python3 "$nofile/health.py" file --group criteria,docs 2>&1); rc=$?
grep -q "^REFUSED\[file\]: file.py is not installed" <<<"$out" && [ $rc = 2 ] && [ "$(wc -l < "$FAKE_GH_DIR/calls.log")" = "$n" ] && ok "health.py without file.py refuses to file, writes nothing" || bad "no file.py"
# Value: protects=a group whose rule cannot read its data closes none of its issues on file; fails_when=plan() stops
#   taking unread groups out of the ones that ran; why_new=the lone health.py above now refuses before plan(), so it no
#   longer reaches the guard; seam=none; no_claim=real GitHub issue state (fake gh; toy repo)
lone="$lone/skills/workflow-health"; mkdir -p "$lone"; cp -R "$here/skills/workflow-health/scripts" "$lone/"  # no sibling skills: criteria and docs cannot read
python3 "$lone/scripts/health.py" file --group criteria,docs >/dev/null 2>&1
still=$(python3 -c "import json,os;print(sorted(i['number'] for i in json.load(open(os.environ['FAKE_GH_DIR']+'/issues.json')) if i['state']=='OPEN' and 'docs:' not in i['body'] and i['number'] in $open_other))")
[ "$still" = "$open_other" ] && ok "a rule that could not read closes none of its issues" || bad "unread close: $still"

echo "repo: $d/repo"
[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
