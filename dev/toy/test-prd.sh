#!/bin/bash
# reads: skills/workflow-docs/scripts/criteria.py skills/workflow-docs/scripts/docs.py
# reads: skills/workflow-docs/scripts/prd.py skills/workflow-health/scripts/health.py
# reads: skills/workflow-monitoring/scripts/board_status.py
# reads: skills/workflow-monitoring/scripts/graph.py skills/workflow-monitoring/scripts/live_board.py
# reads: skills/workflow-health/scripts/judge.py
# reads: skills/workflow-monitoring/scripts/board_page.py skills/workflow-regression/scripts/regression.py
# reads: skills/workflow-release/scripts/release.py skills/workflow-setup/scripts/setup.py
# Test the PRD page format: section order, the owner's PRD review lock, Given/When/Then scenarios, the prd
# command, convert, the requirement readers, and that this repo stays green. usage: test-prd.sh [DIR]
set -u
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID  # run cells and rendered Tests never depend on the runner
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH  # a toy test never reaches a real session tool
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d)  # setup.py writes the private settings under HOME
export USERPROFILE="$HOME"
export LOOP_OWNER_WORDS='"review it" (the toy owner)'  # review --user with no terminal needs the owner's words
d=${1:-$(mktemp -d)}; rm -rf "$d"; mkdir -p "$d"
"$here/dev/toy/make.sh" "$d" || exit 1
export LOOP_FLOW="$d/flow.json" PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh"
unset GH_TOKEN GITHUB_TOKEN
docs="python3 $here/skills/workflow-docs/scripts/docs.py"
cri="python3 $here/skills/workflow-docs/scripts/criteria.py"
prd="python3 $here/skills/workflow-docs/scripts/prd.py"
reg="python3 $here/skills/workflow-regression/scripts/regression.py"
cd "$d/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
python3 -c "import json; c = json.load(open('.loop/config.json')); c['criteria'] = True; json.dump(c, open('.loop/config.json', 'w'), indent=2)"
mkdir -p "$FAKE_GH_DIR" docs/wiki skills/toy
printf '## Command map\n\n| Ask | Runs |\n|---|---|\n| `/toy median` | `python3 scripts/calc.py median` |\n| `/toy mean` | `python3 scripts/calc.py mean` |\n' > skills/toy/SKILL.md
printf 'Delivery\tcalc.py\nHome\tREADME.md\n' > .loop/docs.tsv
printf '<!-- workflow-docs -->\n# Toy\n\n## Features\n\n| Feature | What it does | How to use | Milestone |\n|---|---|---|---|\n| [Delivery](Delivery) | Sums up the numbers of the toy calculator. | [README](https://github.com/toy/repo#how-to-use-delivery) | https://example.test/milestone/1 |\n' > docs/wiki/Home.md
printf '\n## How to use\n\n### How to use Delivery\n\n| You say | What happens |\n|---|---|\n| "How do I use Delivery?" | Opens [How-to-use-Delivery](https://github.com/toy/repo/wiki/How-to-use-Delivery). |\n' >> README.md
repo=$PWD; mkdir -p docs/wiki; cat > docs/wiki/How-to-use-Delivery.md <<'HOWEOF'
<!-- workflow-docs -->
# How to use Delivery

## What it's for

The toy calculator prints the median of the numbers given.

### What's delivered

| Component | Kind | What it is | How a user uses it |
|---|---|---|---|
| `calc.py` | Command | Prints a median. | `python3 scripts/calc.py median LIST`. |

## How to reach or run it

- DEL-1: The calculator prints a median; run `calc.py median LIST` and read its one line.
- DEL-2: It answers within a second; run it on a short list.

### Command: calc.py
- **Command:** `python3 scripts/calc.py median LIST`
- **Dry run:** none
- **Reads:** the list given
- **Writes:** nothing
- **Exit codes:** 0 printed

## Links

- PRD page: [Delivery](Delivery)
HOWEOF
fails=0; day=$(date -u +%F)
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
P=docs/wiki/Delivery.md
USAGE=''  # Usage is gone (drop-usage): page "$USAGE" writes a page with no Usage section
REQS='### Functional

- DEL-1: **Unreviewed** The calculator prints a median.
  - The median of the numbers given is printed.
- DEL-2: **Unreviewed** It exits 0.
  - It exits 0 once it has printed.

### Non-functional

None'
page() { # page [USAGE]: a PRD page for Delivery, rendered
  local usage=""; [ -n "${1:-}" ] && usage="## Usage

$1

"
  cat > $P <<EOF
<!-- workflow-docs -->
# Delivery

$MS

Review: **Unreviewed**

How to use: [How-to-use-Delivery](How-to-use-Delivery)

## Problem

- I own the toy calculator and want my numbers summed up.

${usage}## Requirements

$REQS

## Non-goals

- No charts.

- No files.

## Success metrics

- The median is right for every list in the toy run.

## Tests

EOF
  $cri render >/dev/null
}
edit() { python3 - "$P" "$1" "$2" <<'PY'
import sys
p, a, b = sys.argv[1:]
t = open(p).read()
assert a in t, a
open(p, "w").write(t.replace(a, b, 1))
PY
}
check() { $docs check 2>&1; }
MS=""; page "$USAGE"
MS="Milestone: https://example.test/milestone/1"; page "$USAGE"; git add -A; git commit -qm "Toy PRD" >/dev/null

echo "== 1. the sections, in order, and nothing else"
check | grep -q "DOCS OK" && ok "a PRD page passes" || bad "PRD page: $(check)"
edit "## Non-goals" "## Scope"; check | grep -q "^SECTIONS Delivery: have Problem, Requirements, Scope" && ok "an unknown section fails" || bad "unknown section"
page "$USAGE"; python3 - "$P" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
a, b = t.index("## Non-goals"), t.index("## Success metrics"); c = t.index("## Tests")
open(p, "w").write(t[:a] + t[b:c] + t[a:b] + t[c:])
PY
check | grep -q "^SECTIONS Delivery: .*want Problem, Requirements, Non-goals, Success metrics, Tests" && ok "swapped sections fail" || bad "swapped"
page "$USAGE"; edit "## Problem" "A stray line.

## Problem"; check | grep -q "^SECTIONS Delivery: has text between the Review line and the first section: A stray line.*Fix:" && ok "stray text before the first section fails" || bad "stray text"
page "$USAGE"; edit "- No files." "- No files.

\`\`\`
## Example heading in a fence
\`\`\`"; check | grep -q "DOCS OK" && ok "a fenced heading is not a section" || bad "fenced heading: $(check)"
page "$USAGE"; edit "## Non-goals

- No charts.

- No files.

" "## Non-goals

"; check | grep -q "^NONGOALS Delivery: .*Fix:" && ok "empty Non-goals fail" || bad "nongoals"
page "$USAGE"; edit "- The median is right for every list in the toy run." "- One.

- Two.

- Three.
- Four."; check | grep -q "^METRICS Delivery: Success metrics has 4 lines, want 1 to 3. Fix:" && ok "more than three Success metrics lines fail" || bad "metrics"
page "$USAGE"; edit "Review: **Unreviewed**" "Review: maybe"; check | grep -q "^REVIEW Delivery: a malformed Review line.*Fix:" && ok "a malformed Review line fails" || bad "review malformed"
page "$USAGE"; edit "Review: **Unreviewed**

" ""; check | grep -q "^REVIEW Delivery: has no Review line. Fix:" && ok "a missing Review line fails" || bad "review missing"

echo "== 2. the owner's PRD review locks Problem, Requirements, Non-goals and Success metrics"
page "$USAGE"; git commit -qam "Clean" >/dev/null || true
$cri review Delivery 2>&1 | grep -q "only the owner" && ok "a PRD review needs --user" || bad "review --user"
$cri review Delivery --user --date 2026-11-08 | grep -q "^REVIEWED PAGE Delivery" && grep -q "^Review: \*\*Reviewed 2026-11-08\*\* <!-- prd P=[0-9a-f]\{8\} R=[0-9a-f]\{8\} N=[0-9a-f]\{8\} M=[0-9a-f]\{8\} U=[0-9a-f]\{8\} -->$" $P && ok "review PAGE --user --date stamps the PRD line with five fingerprints" || bad "review page"
check | grep -q "DOCS OK" && ok "a reviewed PRD passes" || bad "reviewed: $(check)"
git commit -qam "Reviewed PRD" >/dev/null
for pair in "own the toy calculator|own the big calculator|Problem" "prints a median.|prints a mode.|Requirements" "- No charts.|- No graphs.|Non-goals" "for every list|for most lists|Success metrics"; do
  IFS='|' read -r a b name <<<"$pair"
  edit "$a" "$b"; out=$(check)
  grep -q "^LOCKED Delivery: the reviewed PRD changed in $name (reviewed lock" <<<"$out" && grep -q "Fix: git log -p -- docs/wiki/Delivery.md .*unreview Delivery --user (and /workflow-docs unreview ID --user" <<<"$out" && ok "a change to $name is LOCKED with both un-review fixes" || bad "lock $name: $out"
  git checkout -q -- $P
done
python3 - "$P" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
t = t.replace("- No files.\n\n", "", 1).replace("## Success metrics\n\n", "## Success metrics\n\n- No files.\n\n", 1)
open(p, "w").write(t)
PY
check | grep -q "^LOCKED Delivery: the reviewed PRD changed in Non-goals, Success metrics" && ok "a line moved from Non-goals to Success metrics is LOCKED naming both" || bad "moved line"
git checkout -q -- $P; edit "own the toy" "own the old"; edit "- No charts." "- No plots."
check | grep -q "^LOCKED Delivery: the reviewed PRD changed in Problem, Non-goals (reviewed lock P=.* N=.*, now P=.* N=" && ok "two sections changed at once are both named, with both locks" || bad "two sections"
git checkout -q -- $P; edit "- I own the toy calculator and want my numbers summed up." "- I own the toy calculator
and want   my numbers summed up."
check | grep -q "LOCKED" && bad "a reflow-only edit is LOCKED" || ok "a reflow-only edit is not LOCKED"
git checkout -q -- $P; edit "- DEL-2: **Unreviewed** It exits 0." "- DEL-2: **Unreviewed** It exits 0.
- DEL-3: **Unreviewed** It is quick."; check | grep -q "^LOCKED Delivery: the reviewed PRD changed in Requirements" && ok "adding a requirement is LOCKED" || bad "add requirement"
git checkout -q -- $P; edit "- DEL-2: **Unreviewed** It exits 0.
" ""; check | grep -q "^LOCKED Delivery: the reviewed PRD changed in Requirements" && ok "removing a requirement is LOCKED" || bad "remove requirement"
git checkout -q -- $P
$cri review DEL-1 --user --date 2026-11-08 >/dev/null; check | grep -q "LOCKED" && bad "reviewing a requirement tripped the PRD lock" || ok "reviewing a requirement after the PRD review doesn't trip the lock"
$cri unreview DEL-1 --user >/dev/null; check | grep -q "LOCKED" && bad "unreviewing a requirement tripped the PRD lock" || ok "unreviewing a requirement doesn't trip the lock either"
git checkout -q -- $P; before=$(grep "^Review:" $P)
$cri unreview Delivery --user | grep -q "^UNREVIEWED PAGE Delivery" && grep -q "^Review: \*\*Unreviewed\*\*$" $P && ok "unreview PAGE clears the PRD review" || bad "unreview page"
edit "- No charts." "- No graphs."; check | grep -q "LOCKED" && bad "an unreviewed PRD is locked" || ok "after unreview the PRD may change"
$cri review Delivery --user >/dev/null; after=$(grep "^Review:" $P)
[ "$before" != "$after" ] && grep -q "Reviewed $day" <<<"$after" && ! check | grep -q "LOCKED" && ok "review again gives new fingerprints and no lock" || bad "re-review"
git checkout -q -- $P

echo "== 3. review and unreview check every argument first"
cp $P "$d/before.md"
$cri review DEL-9 Delivery --user 2>&1 | grep -q "REFUSED: no requirement DEL-9 .*Nothing was changed. Fix:" && cmp -s $P "$d/before.md" && ok "a bad ID with a good page changes nothing" || bad "bad id + page"
$cri review DEL-1 Nosuch --user 2>&1 | grep -q "REFUSED: Nosuch is not a feature page.*Nothing was changed. Fix:" && cmp -s $P "$d/before.md" && ok "a good ID with a bad page changes nothing" || bad "id + bad page"
$cri review Delivery --user --date 2026-13-45x 2>&1 | grep -q "REFUSED: --date 2026-13-45x is not a YYYY-MM-DD date.*Fix:" && ok "a bad --date is refused" || bad "bad date"
$cri review Delivery --user --date 2999-01-01 2>&1 | grep -q "REFUSED: --date 2999-01-01 .*on or before today" && cmp -s $P "$d/before.md" && ok "a future --date is refused" || bad "future date"
$cri unreview Home --user 2>&1 | grep -q "REFUSED: Home is not a feature page" && ok "Home is not a feature page" || bad "home"
! $cri review DEL-1 delivery --user >/dev/null 2>&1 && cmp -s $P "$d/before.md" && ok "a page name must match the page's own case; nothing changes" || bad "page case"
! $cri unreview ../../README --user >/dev/null 2>&1 && ok "a page name outside the wiki is refused" || bad "page path"

echo "== 4. Usage is gone: a Usage section is USAGE, never CHANGED, and the review lock ignores it"
edit "## Requirements" "## Usage

- \`/toy median 1 2 3\` — Prints the median (\`2\`). Refuses nothing.

## Requirements"
out=$(check); rc=$?
grep -q "^USAGE Delivery: has a Usage section" <<<"$out" && ! grep -q "^CHANGED\|^LOCKED" <<<"$out" && [ "$rc" = 1 ] && ok "a Usage section added after the review is USAGE, not CHANGED or LOCKED, and the check exits 1" || bad "usage added: $out"
out=$($docs audit --dry-run 2>&1); grep -q "^USAGE Delivery" <<<"$out" && ok "audit names the USAGE page" || bad "audit usage: $out"
git checkout -q -- $P

echo "== 5. a PRD review makes every requirement with no passing test UNTESTED, and fixes never touch the page"
$docs audit --dry-run | grep -q "^UNTESTED DEL-2: no test" && ok "a PRD review with Unreviewed requirements lists UNTESTED for one with no row" || bad "untested via PRD review"
page "$USAGE"; $cri review Delivery --user >/dev/null; git commit -qam "Reviewed again" >/dev/null
cp $P "$d/page.before"; echo "# change" >> calc.py; git commit -qam "Code" >/dev/null
(cd "$here/skills/workflow-release/scripts" && python3 -c "import release; release.docs_trouble('$repo', 'main', True)") >/dev/null 2>&1
cmp -s $P "$d/page.before" && ! check | grep -q "^CHANGED\|^LOCKED" && ok "the release step's mechanical fixes never change a reviewed page" || bad "fixes touched the page"
git checkout -q -- .; git reset -q --hard HEAD~1  # drop the code commit, so the page is not stale

echo "== 6. Tests are Given/When/Then scenarios with the test, its result and date"
$reg add del-1a --level land --command "true" --goal DEL-1 --describe "Given 1 2 3, when the median is asked, then it prints 2." >/dev/null
$reg add del-2a --level land --command "true" --goal DEL-2 --describe "It exits 0." >/dev/null
$reg add bug-1 --level land --command "true" --goal DEL-1 --describe "Empty input crashes." >/dev/null
python3 - <<'PY'
p = ".loop/regression.tsv"; rows = [r.split("\t") for r in open(p).read().split("\n")]
for r in rows:
    if r[0] == "bug-1":
        r[6:8] = ["defect", "https://example.test/issues/7"]
open(p, "w").write("\n".join("\t".join(r) for r in rows))
PY
$reg run del-1a >/dev/null || true; $cri render >/dev/null
grep -qxF "| [del-1a](Tests#t-del-1a) | requirement | DEL-1 | Given 1 2 3, when the median is asked, then it prints 2. | PASS $day |" $P && ok "a row renders as a scenario in the Tests table, with its test link, result and date" || bad "scenario line"
grep -qxF "| [del-2a](Tests#t-del-2a) | requirement | DEL-2 | It exits 0. (not yet Given/When/Then) | not run |" $P && grep -qxF "| - | requirement | DEL-2 | no passing test | not enforced |" $P && ok "a plain description renders flagged, and a requirement with no passing row is not enforced" || bad "flagged"
grep -qxF "| [bug-1](Tests#t-bug-1) | defect | [#7](https://example.test/issues/7) state unknown | Empty input crashes. (not yet Given/When/Then) | not run |" $P && ok "defect tests render in the same scenario form, in the same table" || bad "defect scenario"
out=$($docs audit --dry-run)
grep -q "^REWRITE regression: SCENARIO row del-2a: 'It exits 0.' is not 'Given ..., when ..., then ...'. Fix:" <<<"$out" && grep -q "SCENARIO row bug-1" <<<"$out" && ! grep -q "SCENARIO row del-1a" <<<"$out" && ok "audit lists each plain row, defect rows too, as SCENARIO" || bad "scenario audit: $out"
check | grep -q "SCENARIO" && bad "SCENARIO failed the docs check" || ok "SCENARIO is not a docs check failure"
rm -f .loop/regression.tsv .loop/regression-runs.tsv; git checkout -q -- .

echo "== 7. the requirement readers find the same IDs under either heading, outside fences"
mkdir -p "$d/r/docs/wiki" "$d/r/.loop"; cp .loop/config.json "$d/r/.loop/"
printf 'Alpha\tcalc.py\nBeta\tcalc.py\n' > "$d/r/.loop/docs.tsv"
printf '<!-- workflow-docs -->\n# Alpha\n\nReview: **Unreviewed**\n\nHow to use: [How-to-use-Delivery](How-to-use-Delivery)\n\n## Problem\n\nAn example:\n\n```\n## Requirements\n- ZZZ-9: **Unreviewed** Not real.\n```\n\n## Requirements\n\n- ALP-1: **Unreviewed** One.\n- ALP-2: **Unreviewed** Two.\n\n## Non-goals\n\n- None.\n\n## Success metrics\n\n- Works.\n\n## Tests\n\n' > "$d/r/docs/wiki/Alpha.md"
printf '<!-- workflow-docs -->\n# Beta\n\n## Summary\n\nOld page.\n\n## Criteria\n\n- BET-1: **Unreviewed** Old one.\n\n## Tests\n\n' > "$d/r/docs/wiki/Beta.md"
ids=$(cd "$d/r" && python3 - "$here" <<'PY'
import sys, os
here = sys.argv[1]
for sub in ("workflow-release", "workflow-regression", "workflow-health", "workflow-docs"):
    sys.path.insert(0, os.path.join(here, "skills", sub, "scripts"))
import release, regression, judge, criteria
root, out = os.getcwd(), []
release.doc_rows = lambda top: ["Alpha", "Beta"]
release.run = lambda *a, **k: type("R", (), {"returncode": 0})()
out.append(sorted(x.split()[0] for x in release.criteria_trouble(root, {})))
out.append(sorted(regression.criteria_ids(root)))
out.append(sorted(i for p in ("Alpha", "Beta") for i, _ in judge.criteria(root, p)))
seen = {}
for page in ("Alpha", "Beta"):
    text = open("docs/wiki/%s.md" % page).read()
    parts = dict(criteria.sections(text))
    out.append(sorted(m.group(1) for _, m in criteria.criteria_of(parts.get("Requirements") or parts.get("Criteria")) if m))
print(out[0] == out[1] == out[2] == sorted(out[3] + out[4]) == ["ALP-1", "ALP-2", "BET-1"], out)
PY
)
grep -q "^True" <<<"$ids" && ok "release, regression, judge and the page parser read the same IDs under both headings, ignoring a fenced heading" || bad "readers: $ids"
(cd "$d/r" && git init -q && python3 -c "
import sys; sys.path.insert(0, '$here/skills/workflow-docs/scripts')
import docs; print([c for c in docs.counts('.') if 'Alpha' in c[1]])") | grep -q '^\[\]$' && ok "the docs counts reader reads Requirements, not the fenced example" || bad "counts reader"

echo "== 8. sync and the release see requirements on a PRD page"
out=$($reg sync 2>&1 || true); grep -q "^GAP DEL-1" <<<"$out" && grep -q "^GAP DEL-2" <<<"$out" && ok "regression sync reports a requirement with no row" || bad "sync: $out"
(cd "$here/skills/workflow-release/scripts" && python3 -c "import release; print(release.criteria_trouble('$repo', {}))") | grep -q "DEL-1 (no regression row)" && ok "the release's requirement check refuses an unmet requirement" || bad "release refuses"

echo "== 9. prd new drafts an Unreviewed PRD from a one-line idea"
$prd new DEL-4 "x" --paths calc.py 2>&1 | grep -q "REFUSED: DEL-4 looks like a requirement ID.*Fix: .*prd.py new Billing" && ok "an ID-shaped name is refused with an example" || bad "id name"
$prd new Billing "charge cards" 2>&1 | grep -q "REFUSED: no --paths.*Fix: .*--paths" && [ ! -f docs/wiki/Billing.md ] && ok "a missing --paths is refused" || bad "no paths"
$prd new Delivery "x" --paths calc.py 2>&1 | grep -q "REFUSED: docs/wiki/Delivery.md already exists" && ok "an existing page is refused" || bad "existing"
out=$($prd new Delight "Owners want a smile when the sum is right." --paths calc.py); echo "$out"
grep -q "^DRAFTED docs/wiki/Delight.md: Review \*\*Unreviewed\*\*, requirement DELI-1" <<<"$out" && grep -q "^NEXT replace the placeholder lines" <<<"$out" && grep -q "regression row in this same pull request" <<<"$out" && ok "prd new drafts the page, takes a free prefix (DEL is used) and prints the next steps" || bad "new output"
grep -q "^Review: \*\*Unreviewed\*\*$" docs/wiki/Delight.md && grep -q "^- DELI-1: \*\*Unreviewed\*\* Owners want a smile" docs/wiki/Delight.md && ! grep -q "^Milestone:" docs/wiki/Delight.md && ok "the draft is Unreviewed, with no Milestone line" || bad "draft shape"
out=$(check); grep -q "^UNMAPPED" <<<"$out" && bad "the draft is unmapped" || ok "the draft is mapped in docs.tsv"
grep -q "^UNWRITTEN Delight" <<<"$out" && ! grep -q "^SECTIONS Delight" <<<"$out" && ok "the draft is UNWRITTEN until its placeholders are replaced" || bad "unwritten: $out"
python3 -c "
p = 'docs/wiki/Delight.md'; t = open(p).read(); open(p, 'w').write(t.replace('# Delight\n', '# Delight\n\nMilestone: https://example.test/m/1\n', 1))"
grep -v '^$' docs/wiki/Delight.md | sed -n '2,4p' | tr '\n' '~' | grep -q "^# Delight~Milestone: https://example.test/m/1~Review: \*\*Unreviewed\*\*~$" && ! check | grep -q "^REVIEW Delight" && ok "an optional Milestone line goes under the title and keeps Review next" || bad "milestone order"
$prd new Qq "x" --paths calc.py --prefix DEL 2>&1 | grep -q "REFUSED: --prefix DEL must be 2 to 5 capital letters not already in use" && ok "a used --prefix is refused" || bad "prefix"
git checkout -q -- .; rm -f docs/wiki/Delight.md

echo "== 10. convert turns old pages into PRD pages"
printf '<!-- workflow-docs -->\n# Delivery\n\nMilestone: https://example.test/m/2\n\n## Summary\n\nThe toy calculator, an old page.\n\n## Criteria\n\n%s\n\n## Tests\n\n' "$REQS" > $P
cp $P "$d/old.md"; out=$($prd convert); grep -q "^Delivery converted (dry run)" <<<"$out" && cmp -s $P "$d/old.md" && ok "convert without --write changes nothing" || bad "dry convert"
$prd convert --write | grep -q "^Delivery converted$" && ok "convert --write converts an old page" || bad "convert"
grep -v '^$' $P | sed -n '3,5p' | tr '\n' '~' | grep -q "^Milestone: https://example.test/m/2~Review: \*\*Unreviewed\*\*~## Problem~$" && grep -q "^- DEL-1: \*\*Unreviewed\*\* The calculator prints a median.$" $P && ok "Summary becomes Problem, Criteria Requirements, lines and stamps kept, Review under Milestone" || bad "converted shape"
$prd convert --write | grep -q "^Delivery skipped$" && ok "converting twice changes nothing" || bad "twice"
$cri render >/dev/null; out=$(check)
grep -q "^UNWRITTEN Delivery" <<<"$out" && ! grep -q "^SECTIONS" <<<"$out" && ok "a converted page is UNWRITTEN until its placeholder drafts are replaced" || bad "convert unwritten: $out"
sed -i.bak 's/^- Write this page from what is really in the repo\./- A real draft line./' $P; rm $P.bak
! check | grep -v "^FORMAT" | grep -q . && ok "with real drafts the converted page passes all but the format checks, which want a rewrite" || bad "drafted: $(check)"
printf '<!-- workflow-docs -->\n# Delivery\n\nReview: **Unreviewed**\n\nHow to use: [How-to-use-Delivery](How-to-use-Delivery)\n\n## Problem\n\nHalf done.\n\n## Criteria\n\n%s\n\n## Non-goals\n\n- None.\n\n## Tests\n\n' "$REQS" > $P
$prd convert --write | grep -q "^Delivery completed$" && grep -q "^## Requirements$" $P && grep -q "^## Success metrics$" $P && [ "$(grep -c '^Review:' $P)" = 1 ] && ok "a half-converted page is completed" || bad "completed"
printf '<!-- workflow-docs -->\n# Delivery\n\nReview: **Unreviewed**\n\nHow to use: [How-to-use-Delivery](How-to-use-Delivery)\n\n## Problem\n\nHalf done.\n\n## Requirements\n\n%s\n\n## Success metrics\n\n- m\n\n## Tests\n\n' "$REQS" > $P
$prd convert --write >/dev/null; grep '^## ' $P | tr '\n' '~' | grep -q "^## Problem~## Requirements~## Non-goals~## Success metrics~## Tests~$" && ok "a missing Non-goals goes before Success metrics" || bad "non-goals order: $(grep '^## ' $P | tr '\n' ' ')"
printf '## Summary\n\nNo title.\n\n## Criteria\n\n%s\n\n## Tests\n\n' "$REQS" > $P
$prd convert --write >/dev/null; grep -q "^## Problem$" $P && grep -q "^No title.$" $P && [ "$(grep -c '^Review:' $P)" = 1 ] && ok "a page with no title keeps its first heading" || bad "no title: $(head -5 $P | tr '\n' ' ')"
printf '<!-- workflow-docs -->\n# Delivery\n\n## Overview\n\nOdd.\n\n## Tests\n\n' > $P
out=$($prd convert --write); rc=$?
grep -q "^Delivery refused: sections are Overview, Tests" <<<"$out" && [ "$rc" = 1 ] && grep -q "Fix:" <<<"$out" && ok "an unrecognized page is refused with what is missing" || bad "refused: $out"
git checkout -q -- .

echo "== 11. revisions: migrate, revise, retire and the REVISION and IDS checks"
git checkout -q -- .; git switch -q main 2>/dev/null; MS="Milestone: https://example.test/milestone/1"
REQS='### Functional

- DEL-1: **Unreviewed** The calculator prints a median.
  - The median of the numbers given is printed.
- DEL-2: **Unreviewed** It exits 0.
  - It exits 0 once it has printed.
- DEL-3: **Unreviewed** It is quick.
  - It answers within a second.
- DEL-4: **Unreviewed** It is quiet.
  - It prints nothing else.
- DEL-5: **Unreviewed** It is small.
  - It fits one file.

### Non-functional

None'
printf -- '- DEL-3: Quick; run calc.py on a short list.\n- DEL-4: Quiet; read its one line.\n- DEL-5: Small; it is one file.\n' > "$d/items"; python3 - "$d/items" <<'PY'
import sys
p = 'docs/wiki/How-to-use-Delivery.md'; t = open(p).read()
open(p, 'w').write(t.replace('- DEL-2: It answers within a second; run it on a short list.\n', '- DEL-2: It answers within a second; run it on a short list.\n' + open(sys.argv[1]).read(), 1))
PY
page "$USAGE"; git add -A; git commit -qm "five requirements" >/dev/null; git push -q origin main 2>/dev/null
C=$(cd "$(git rev-parse --git-common-dir)" && pwd); mkdir -p "$C/loop"
printf 'o1\t2026-11-17T00:00:00Z\toperation\t"revise it"\tprd-t,Delivery,DEL-1,DEL-2\no2\t2026-11-17T00:00:00Z\toperation\t"other"\tDelivery,DEL-4\n' > "$C/loop/owner-words.tsv"
rv="$cri"; R="--owner-record o1 --goal prd-t"
! check | grep -qE "REVISION|IDS" && check | grep -q "DOCS OK" && ok "a page with no Revisions section is not failed for it" || bad "a page with no Revisions section is not failed for it"
$rv migrate --page Delivery $R | grep -q "^MIGRATED docs/wiki/Delivery.md$" && check | grep -q "DOCS OK" && [ "$(grep -c '^| r1 |' $P)" = 5 ] && grep -q "migration r1; date from the run day" $P && ok "migrate gives each requirement r1 and the check passes" || bad "migrate gives each requirement r1 and the check passes"
cp $P "$d/migrated.md"; $rv migrate --page Delivery $R | grep -q "^MIGRATE OK$"; cmp -s $P "$d/migrated.md" && ok "a second migrate changes nothing" || bad "a second migrate changes nothing"
$rv review DEL-1 --user >/dev/null; sed -i.bak 's/^Review: .*/Review: **Unreviewed**/' $P; rm -f $P.bak; git add -A; git commit -qm "base with DEL-1 reviewed" >/dev/null; git push -q origin main 2>/dev/null
before=$(grep -c "Reviewed" $P)
out=$($rv revise DEL-1 --text "The calculator prints a median | and <br> a \\ mean." --why "the owner reworded it" $R 2>&1)
grep -q "^REVISED DEL-1 r1->r2 (now Unreviewed, awaits review)$" <<<"$out" && grep -q "^- DEL-1: \*\*Unreviewed\*\* The calculator prints a median | and <br> a \\\\ mean\.$" $P && ! grep -q "reviewed [0-9a-f]\{8\} -->.*mean" $P && [ "$(grep -c "^- DEL-[2-5]: \*\*Unreviewed" $P)" = 4 ] && check | grep -q "DOCS OK" && ok "revise touches only that requirement, writes no Reviewed stamp and the check stays green" || bad "revise touches only that requirement, writes no Reviewed stamp and the check stays green"
[ "$(grep -n "^| r2 | " $P | head -1 | cut -d: -f1)" -lt "$(grep -n "^| r1 | " $P | sed -n 1p | cut -d: -f1)" ] && grep -qF '| r2 | '"$day"' | The calculator prints a median \| and \<br> a \\ mean. <br> The median of the numbers given is printed. | the owner reworded it | o1: "revise it" |' $P && ok "the Revisions table shows the newest revision first with date, reason and owner record" || bad "the Revisions table shows the newest revision first with date, reason and owner record"
ok "text with a pipe, a literal <br> and a backslash round-trips through a revision (the check above is green)"
[ "$(sed -n '/^### DEL-1$/,/^### DEL-2$/p' $P | grep -c '^| r[0-9]')" = 2 ] && sed -n '/^### DEL-1$/,/^### DEL-2$/p' $P | grep -qF "| r1 | $day | The calculator prints a median. <br> The median of the numbers given is printed. |" && ok "the earlier text stays as r1 beside r2" || bad "the earlier text stays as r1 beside r2"
cp $P "$d/revised.md"; edit "It exits 0." "It exits one."; check | grep -q "^REVISION Delivery: \[REV-ROW\] DEL-2: r1 differs from its line" && ok "a line that differs from its newest row fails REVISION" || bad "a line that differs from its newest row fails REVISION"; cp "$d/revised.md" $P
python3 - "$P" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
row = [x for x in t.split("\n") if x.startswith("| r2 |")][0]
open(p, "w").write(t.replace(row, row + "\n" + row, 1))
PY
check | grep -q "^REVISION Delivery: \[REV-ROW\] DEL-1 rows are not r3..r1 newest first (two heads?)" && ok "a duplicated r-number fails as two heads" || bad "a duplicated r-number fails as two heads"; cp "$d/revised.md" $P
git add -A; git commit -qm "revised" >/dev/null; git push -q origin main 2>/dev/null
python3 - "$P" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(t.replace("| r1 | ", "| r1 | 1999-01-01 ", 1).replace("1999-01-01 " + "20", "20", 0))
PY
sed -i.bak 's/^| r1 | \(.*\) | migration r1/| r1 | \1 | edited r1/' $P; rm -f $P.bak
check | grep -q "^REVISION Delivery: \[REV-ROW\] DEL-[0-9]: r1 changed since the base (append-only). Fix: add r[0-9]" && ok "a revision row changed since the base fails as append-only" || bad "a revision row changed since the base fails as append-only"; git checkout -q -- $P
! $rv revise DEL-1 --text "The calculator prints a median | and <br> a \\ mean." --why x $R 2>&1 | grep -qv "^\[REV-NOOP\] DEL-1 already reads so. No changes written.$" && ok "a revise that changes nothing is refused as REV-NOOP" || bad "a revise that changes nothing is refused as REV-NOOP"
$rv revise DEL-2 --text "It exits 0 now." --why x --owner-record o2 --goal prd-t 2>&1 | grep -q "^\[REV-RECORD\] need an owner record naming prd-t and DEL-2 or Delivery. No changes written.$" && git diff --quiet && ok "an owner record that does not name the goal and the ID or page is refused" || bad "an owner record that does not name the goal and the ID or page is refused"
$rv retire DEL-3 --as retired --why "no longer wanted" $R | grep -q "^RETIRED DEL-3 as Retired$"
$rv retire DEL-4 --as merged:DEL-1 --why "same as DEL-1" $R | grep -q "^RETIRED DEL-4 as merged into DEL-1$"
$rv retire DEL-5 --as moved:DEL-1 --why "lives with DEL-1" $R | grep -q "^RETIRED DEL-5 as moved to DEL-1$"
$cri render >/dev/null; sed -i.bak '/^- DEL-[345]: /d' docs/wiki/How-to-use-Delivery.md; rm -f docs/wiki/How-to-use-Delivery.md.bak
grep -q "^- DEL-3: Retired$" $P && grep -q "^- DEL-4: merged into DEL-1$" $P && grep -q "^- DEL-5: moved to DEL-1$" $P && ! grep -q "^- DEL-[345]: \*\*" $P && grep -q "^### DEL-5$" $P && check | grep -q "DOCS OK" && ok "retire writes Retired, merged into and moved to entries, keeps the revision rows and the check passes" || bad "retire writes Retired, merged into and moved to entries, keeps the revision rows and the check passes"
$rv retire DEL-3 --as retired --why again $R 2>&1 | grep -q "^\[REV-ROW\] no live requirement DEL-3" && ok "a Retired ID cannot be revised or retired again" || bad "a Retired ID cannot be revised or retired again"
cp $P "$d/before.md"; $rv retire DEL-2 --as merged:DEL-9 --why x $R 2>&1 | grep -q "^\[IDS-MISSING\]" && cmp -s $P "$d/before.md" && ok "a merged or moved target that is no live requirement is refused" || bad "a merged or moved target that is no live requirement is refused"
cp $P "$d/retired.md"; sed -i.bak 's/^- DEL-3: Retired$/- DEL-3: moved to DEL-9/' $P; rm -f $P.bak
check | grep -q "^IDS Delivery: \[IDS-MISSING\] DEL-3: moved to DEL-9 is no requirement" && ok "a Retired entry pointing at a missing requirement fails" || bad "a Retired entry pointing at a missing requirement fails"; cp "$d/retired.md" $P
python3 - "$P" <<'PY'
import re, sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(re.sub(r"- DEL-2: .*\n  - It exits 0 once it has printed\.\n", "", t))
PY
check | grep -q "^IDS Delivery: \[IDS-MISSING\] DEL-2 is gone" && ok "an ID deleted from a migrated page fails IDS-MISSING" || bad "an ID deleted from a migrated page fails IDS-MISSING"; cp "$d/retired.md" $P
git add -A; git commit -qm "retired" >/dev/null; git push -q origin main 2>/dev/null
sed -i.bak 's/^- DEL-3: Retired$/- DEL-3: Retired\n- DEL-1: Retired/' $P; rm -f $P.bak
check | grep -q "^IDS Delivery: \[IDS-REUSE\] DEL-1 is live and Retired" && ok "an ID that is live and Retired fails IDS-REUSE" || bad "an ID that is live and Retired fails IDS-REUSE"; git checkout -q -- $P
sed -i.bak 's/^- DEL-3: Retired$//' $P; rm -f $P.bak
check | grep -q "^IDS Delivery: \[IDS-MISSING\] DEL-3 is gone" && ok "a Retired entry deleted since the base fails (an ID cannot disappear)" || bad "a Retired entry deleted since the base fails (an ID cannot disappear)"; git checkout -q -- $P
python3 - "$P" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read()
head, rest = t.split("\n## Revisions\n", 1)
open(p, "w").write(head + "\n" + rest.split("\n## ", 1)[1].join(["## ", ""]) if False else head + "\n## " + rest.split("\n## ", 1)[1])
PY
check | grep -q "^REVISION Delivery: \[REV-GONE\] Revisions section removed" && ok "removing the Revisions section fails REV-GONE" || bad "removing the Revisions section fails REV-GONE"; git checkout -q -- $P
$rv review Delivery --user >/dev/null; $rv migrate --page Delivery $R >/dev/null; check | grep -q "LOCKED" && bad "migrate trips the page lock: $(check)" || ok "the Revisions section stays out of the page fingerprint"
git checkout -q -- .; $rv review Delivery --user >/dev/null; $rv review DEL-1 --user >/dev/null; $rv migrate --page Delivery $R >/dev/null; git add -A; git commit -qm "page reviewed" >/dev/null; git push -q origin main 2>/dev/null
$rv revise DEL-1 --text "The calculator prints the median." --why "reworded" $R >/dev/null; check | grep -q "LOCKED" && bad "a revise on a Reviewed page keeps the page lock quiet: $(check | head -3)" || ok "a revise on a Reviewed page keeps the page lock quiet (a revision row explains it)"
git checkout -q -- .; edit "- No charts." "- No pies."; check | grep -q "^LOCKED Delivery: the reviewed PRD changed in Non-goals" && ok "an unrelated edit of a Reviewed page is still LOCKED" || bad "an unrelated edit of a Reviewed page is still LOCKED"
git checkout -q -- .

[ "$fails" = 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
