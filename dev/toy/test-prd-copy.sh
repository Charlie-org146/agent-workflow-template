#!/bin/bash
# windows: ok
# reads: skills/
# reads: skills/workflow-docs/scripts/criteria.py skills/workflow-docs/scripts/docs.py
# reads: skills/workflow-docs/scripts/pageformat.py skills/workflow-docs/scripts/render.py
# reads: skills/workflow-docs/scripts/prdcopy.py skills/workflow-docs/scripts/prd.py skills/workflow-docs/scripts/counting.py skills/workflow-docs/scripts/audit.py
# reads: skills/workflow-docs/references/commands.md skills/workflow-health/scripts/judge.py
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/tests.py
# reads: skills/workflow-setup/scripts/setup.py skills/workflow-setup/scripts/settings.py
# Test the repo's copy of an external PRD (DOC-17): docs.py sync adopts a source's PRD into .loop/prd/PAGE.md in the repo's layout, a page with a
# source then passes the docs check, the audit and the rows with no reader and shows the PRD as a generated block, an addition on either side is a
# delta accepted with --accept, a change on both sides is a CONFLICT that overwrites nothing, and a page with no source is left alone.
# usage: test-prd-copy.sh [DIR]

set -u
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH  # a toy test never reaches a real session tool
unset GITHUB_SERVER_URL GITHUB_REPOSITORY GITHUB_RUN_ID
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d) USERPROFILE=$(mktemp -d)  # setup.py writes the private settings under HOME
export LOOP_OWNER_WORDS='"review it" (the toy owner)'  # review --user with no terminal needs the owner's words
d=${1:-$(mktemp -d)}; rm -rf "$d"; mkdir -p "$d"
"$here/dev/toy/make.sh" "$d" >/dev/null || exit 1
export LOOP_FLOW="$d/flow.json" PATH="$here/dev/toy/fakegh:$PATH" FAKE_GH_DIR="$d/gh" PYTHONDONTWRITEBYTECODE=1
unset GH_TOKEN GITHUB_TOKEN
docs="python3 $here/skills/workflow-docs/scripts/docs.py"
cri="python3 $here/skills/workflow-docs/scripts/criteria.py"
prd="python3 $here/skills/workflow-docs/scripts/prd.py"
reg="python3 $here/skills/workflow-regression/scripts/regression.py"
cd "$d/repo" || exit 1
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
python3 -c "import json; c = json.load(open('.loop/config.json')); c['criteria'] = True; c.pop('criteria_max', None); json.dump(c, open('.loop/config.json', 'w'), indent=2)"
mkdir -p "$FAKE_GH_DIR" docs/wiki skills/toy
printf '## Command map\n\n| Ask | Runs |\n|---|---|\n| `/toy median LIST` | `python3 scripts/calc.py median LIST` |\n' > skills/toy/SKILL.md
printf 'Delivery\tcalc.py\nHome\tREADME.md\n' > .loop/docs.tsv
fails=0; day=$(date -u +%F)
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
check() { $docs check 2>&1; }
H=docs/wiki/Home.md; P=docs/wiki/Delivery.md; T=docs/wiki/Tests.md
edit() { python3 - "$1" "$2" "$3" <<'PY'
import sys
p, a, b = sys.argv[1:]
t = open(p).read()
assert a in t, a
open(p, "w").write(t.replace(a, b, 1))
PY
}
cat > $H <<'EOF'
<!-- workflow-docs -->
# Toy

## Features

| Feature | What it does | How to use | Milestone |
|---|---|---|---|
| [Delivery](Delivery) | Prints the median of the numbers given. | [README](https://github.com/toy/repo#how-to-use-delivery) | https://github.com/toy/repo/milestone/1 |
EOF
cat >> README.md <<'EOF'

## How to use

### How to use Delivery

Say these to the agent:

| You say | What happens |
|---|---|
| "What is the median of 1 2 3?" | The calculator prints 2. |
EOF
cat > $P <<'EOF'
<!-- workflow-docs -->
# Delivery

Review: **Unreviewed**

## Problem

- I want the median of my numbers without working it out by hand.

## Requirements

### Functional

- DEL-1: **Unreviewed** The calculator prints a median.
  - The median of the numbers given is printed.

### Non-functional

- DEL-2: **Unreviewed** It answers quickly.
  - It prints within a second for a short list.

## Non-goals

- No charts.

## Success metrics

- The median is right for every list in the toy run.

## Tests

EOF
$reg add del-1a --level land --command "true" --goal DEL-1 --describe "Given 1 2 3, when the median is asked, then it prints 2." >/dev/null
$reg add del-2a --level land --command "true" --goal DEL-2 --describe "Given a short list, when it runs, then it answers in a second." >/dev/null
$reg run del-1a >/dev/null 2>&1; $reg run del-2a >/dev/null 2>&1
$cri render >/dev/null
git add -A; git commit -qm "Toy pages in the format" >/dev/null
reset() { git checkout -q -- .; git clean -qfd docs .loop >/dev/null; }
has() { check | grep -q "$1"; }


# --- offline-prd-copy (DOC-17): the copy in .loop/prd is the PRD every check reads ---
dw=$(cd "$d" && { pwd -W 2>/dev/null || pwd; })
cat > "$d/gh.py" <<'EOF'
import os, sys
open(os.environ["TOY_LOG"], "a").write("gh " + " ".join(sys.argv[1:]) + "\n")
if sys.argv[1:3] == ["issue", "create"]:
    print("https://example.test/issues/%d" % (sum(1 for x in open(os.environ["TOY_LOG"]) if x.startswith("gh issue create"))))
EOF
cat > "$d/writer.py" <<'EOF'
import os, sys
open(os.environ["TOY_LOG"], "a").write("writer " + " ".join(sys.argv[2:]) + " | " + sys.stdin.read() + "\n")
EOF
cat > "$d/reader.py" <<'EOF'
import sys
sys.stdout.write(open(sys.argv[1]).read())
EOF
export TOY_LOG="$d/calls.log"; : > "$TOY_LOG"
rd="python3 $dw/reader.py $dw/notion.md"
sync() { LOOP_PRD_READER="$rd" LOOP_GH="python3 $dw/gh.py" LOOP_PRD_WRITER="python3 $dw/writer.py" $docs sync "$@" 2>&1; }
nosync() { env -u LOOP_PRD_READER LOOP_GH="python3 $dw/gh.py" $docs sync "$@" 2>&1; }
COPY=.loop/prd/Delivery.md
cat > "$d/notion.md" <<'EOF'
Source: toy repo, <code>docs/wiki/Delivery.md</code> at v0 (2026-11-14), made up for the toy
Milestone: [x](y)
Review: <b>Unreviewed</b>

## Problem

I want the median of my numbers without working it out by hand.

## Runbook

### toy-run

- <b>Serves:</b> nobody

## Requirements

### Functional

- <b>DEL-1</b> Functional: <i>(Reviewed 2026-11-10)</i>
  - Functional: The calculator prints a <code>median</code>.
  - The median of the numbers given is printed.

### Non-functional

- <b>DEL-2</b> Non-functional: <i>(Unreviewed)</i>
  - Non-functional: It answers quickly.

## Non-goals

No charts.

## Success metrics

The median is right for every list in the toy run.

## Deployments

| Page | Link |

## New requirements (2026-11-13, Unreviewed, being built in goal toy)

- <b>DEL-3</b> Functional: It rejects an empty list. <i>(Unreviewed)</i>
  - A made-up sub-bullet.
EOF
cat > $P <<'EOF'
<!-- workflow-docs -->
# Delivery

PRD: mcp:notion:delivery-prd

## Tests

EOF
printf 'Delivery\tcalc.py\tmcp:notion:delivery-prd\nHome\tREADME.md\n' > .loop/docs.tsv
$reg add del-1a --level land --command "true" --goal DEL-1 --describe "Given 1 2 3, when the median is asked, then it prints 2." >/dev/null
$reg add del-3a --level land --command "true" --goal DEL-3 --describe "Given an empty list, when the median is asked, then it is rejected." >/dev/null
git add -A; git commit -qm "Link page and rows" >/dev/null

echo "== the source's layout is normalised into the copy"
out=$(sync)
grep -q "^SYNCED Delivery: 3 requirement" <<<"$out" && ok "the first sync adopts the source: 3 requirements" || bad "adopt: $out"
grep -qx -- '- DEL-1: \*\*Reviewed 2026-11-10\*\* Functional: The calculator prints a `median`.' $COPY && grep -qx -- "- DEL-2: \*\*Unreviewed\*\* Non-functional: It answers quickly." $COPY \
  && grep -qx -- "- DEL-3: \*\*Unreviewed\*\* Functional: It rejects an empty list." $COPY && grep -q "^  - The median of the numbers given is printed." $COPY \
  && ok "the copy holds each requirement in the repo's layout: the title from the first sub-bullet, the kind kept, the mark before or after, New requirements merged" || bad "normalise: $(cat $COPY)"
! grep -qE "<b>|<i>|<code>|^Source:|^Milestone:|^Review:|Serves|Page . Link" $COPY && grep -q 'prints a `median`' $COPY \
  && ok "Notion's html tags become markdown, and its Source, Milestone, Review, Runbook and Deployments lines stay out of the copy" || bad "notion shape: $(cat $COPY)"
grep -q "^## Non-goals" $COPY && grep -q "^No charts." $COPY && grep -q "^## Success metrics" $COPY && ok "the copy holds the four sections" || bad "sections: $(cat $COPY)"

echo "== a page with a copy passes with no reader, and shows the PRD as a generated block"
out=$(env -u LOOP_PRD_READER python3 "$here/skills/workflow-regression/scripts/tests.py" list 2>&1); grep -q "^FEATURE Delivery" <<<"$out" && ! grep -q "^FEATURE Other" <<<"$out" && ok "the rows' listing groups the page's rows under it from the copy, before any block, with no reader" || bad "tests list before the block: $out"
$cri render >/dev/null
grep -q "^<!-- prd:begin -->" $P && grep -q "^## Requirements" $P && grep -q "DEL-3: \*\*Unreviewed\*\* Functional: It rejects" $P && grep -q "^## Problem" $P && grep -q "^<!-- prd:end -->" $P \
  && ok "render writes Problem, Requirements, Non-goals and Success metrics as a block generated from the copy" || bad "block: $(cat $P)"
grep -q "DEL-1" $P && ok "the Tests table lists the copy's ids" || bad "tests table: $(cat $P)"
out=$(env -u LOOP_PRD_READER $docs check 2>&1); grep -q "^DOCS OK" <<<"$out" && ! grep -qE "^(UNREAD|LINK)" <<<"$out" && ok "an opted-in page with a copy passes the docs check with no reader: no UNREAD, no LINK" || bad "no reader: $out"
out=$(env -u LOOP_PRD_READER $docs audit --dry-run 2>&1); grep -qE "^(UNREAD|LINK)" <<<"$out" && bad "audit with no reader: $out" || ok "the audit with no reader reports no UNREAD or LINK"
out=$(env -u LOOP_PRD_READER python3 "$here/skills/workflow-regression/scripts/tests.py" list 2>&1); grep -q "DEL-1" <<<"$out" && ok "the rows' listing sees the copy's ids with no reader" || bad "tests list: $out"
edit $P "It rejects an empty list." "It rejects nothing."
out=$(env -u LOOP_PRD_READER $docs check 2>&1); grep -q "^STALE Delivery: its PRD block differs from .loop/prd/Delivery.md" <<<"$out" && ok "a hand-edited block is STALE, naming the copy" || bad "block edit: $out"
$cri render >/dev/null; grep -q "It rejects an empty list." $P && ok "render puts the copy's text back" || bad "re-render: $(cat $P)"
cp $P "$d/page-ok.md"
edit $P "## Non-goals" "## Notes"; out=$(env -u LOOP_PRD_READER $docs check 2>&1); grep -qE "^(SECTIONS|STALE) Delivery" <<<"$out" && ok "a changed block heading is not accepted" || bad "heading: $out"
cp "$d/page-ok.md" $P
git add -A; git commit -qm "Adopted" >/dev/null

echo "== a source that cannot be reached changes nothing"
before=$(cat $COPY)
out=$(nosync); rc=$?
grep -q "^not connected: Delivery (mcp:notion:delivery-prd)" <<<"$out" && [ "$rc" = 0 ] && [ "$(cat $COPY)" = "$before" ] && ok "with no reader sync prints not connected, exits 0 and leaves the copy as it was" || bad "no reader: $rc $out"

echo "== a requirement added on either side is a delta accepted with --accept"
printf '\n- <b>DEL-4</b> Functional: It prints a mean too. <i>(Unreviewed)</i>\n' >> "$d/notion.md"
out=$(sync); grep -q "^DELTA Delivery: DEL-4 the source changed" <<<"$out" && ok "a requirement added in the source is a DELTA naming the source" || bad "source add: $out"
grep -q "DEL-4" $COPY && bad "the delta changed the copy" || ok "the delta leaves the copy as it was"
out=$(sync --accept Delivery:DEL-4=source); grep -q "^ACCEPTED Delivery: DEL-4" <<<"$out" && grep -qx -- "- DEL-4: \*\*Unreviewed\*\* Functional: It prints a mean too." $COPY && grep -q "DEL-1: \*\*Reviewed" $COPY && ok "accepting the source writes that requirement into the copy and leaves the others" || bad "accept source: $out $(cat $COPY)"
python3 - "$COPY" <<'PY'
import sys
p = sys.argv[1]
t = open(p).read()
open(p, "w").write(t.replace("\n## Non-goals", "- DEL-5: **Unreviewed** It keeps the last list.\n\n## Non-goals", 1))
PY
out=$(sync); grep -q "^DELTA Delivery: DEL-5 the repo changed" <<<"$out" && ok "a requirement added in the repo's copy is a DELTA naming the repo" || bad "repo add: $out"
out=$(sync --accept Delivery:DEL-5=repo); grep -q "^ACCEPTED Delivery: DEL-5" <<<"$out" && grep -q "^writer replace DEL-5 | It keeps the last list." "$TOY_LOG" && ok "accepting the repo's text sends it to the source through the writer" || bad "accept repo: $out $(cat $TOY_LOG)"

echo "== a requirement changed on both sides is a CONFLICT, never overwritten"
python3 - "$COPY" "$d/notion.md" <<'PY'
import sys
for p, old, new in ((sys.argv[1], "It answers quickly.", "It answers in a second."), (sys.argv[2], "It answers quickly.", "It answers in two seconds.")):
    t = open(p).read()
    assert old in t, p
    open(p, "w").write(t.replace(old, new, 1))
PY
cp $COPY "$d/copy-before.md"; cp "$d/notion.md" "$d/notion-before.md"
out=$(sync); grep -q "^CONFLICT Delivery: DEL-2 both sides changed (repo: Non-functional: It answers in a second. | source: Non-functional: It answers in two seconds.)" <<<"$out" && ok "a requirement changed on both sides is a CONFLICT naming both texts" || bad "conflict: $out"
cmp -s $COPY "$d/copy-before.md" && cmp -s "$d/notion.md" "$d/notion-before.md" && ok "a conflict overwrites neither side" || bad "conflict overwrote"
grep -q "^gh issue create .*CONFLICT Delivery DEL-2" "$TOY_LOG" && ok "a conflict is posted once as an issue" || bad "conflict issue: $(cat $TOY_LOG)"
n=$(grep -c '^gh issue create' $TOY_LOG); out=$(sync); [ "$(grep -c '^gh issue create' $TOY_LOG)" = "$n" ] && grep -q "CONFLICT Delivery: DEL-2" <<<"$out" && ok "a second sync still reports it and posts nothing more" || bad "second: $out"

echo "== the source's review mark follows when the text agrees"
python3 - "$d/notion.md" <<'PY'
import sys
p = sys.argv[1]
t = open(p).read()
t = t.replace("It answers in two seconds.", "It answers in a second.").replace("It prints a mean too. <i>(Unreviewed)</i>", "It prints a mean too. <i>(Reviewed 2026-11-12)</i>")
open(p, "w").write(t)
PY
out=$(sync); grep -q "^MARKED Delivery: DEL-4" <<<"$out" && grep -qx -- "- DEL-4: \*\*Reviewed 2026-11-12\*\* Functional: It prints a mean too." $COPY && ok "the copy takes the source's Reviewed mark when the text is the same" || bad "mark: $out $(cat $COPY)"

echo "== a copy from before the repo's layout is left as it was"
printf -- '- LG-1: **Unreviewed** Old text.
' > "$d/legacy.md"
mkdir -p .loop/prd; printf '<!-- prd-sync: owned -->
<!-- source: x -->
- LG-1: Old text
' > .loop/prd/Legacy.md; cp .loop/prd/Legacy.md "$d/legacy-before.md"
printf 'Delivery	calc.py	mcp:notion:delivery-prd
Legacy	calc.py	url:%s/legacy.md
Home	README.md
' "$dw" > .loop/docs.tsv
out=$(sync); grep -q "^SKIPPED Legacy: its copy is from before the repo's layout" <<<"$out" && cmp -s .loop/prd/Legacy.md "$d/legacy-before.md" && ok "a copy from before the layout is skipped with the fix named, and left as it was" || bad "legacy: $out"

echo "== a page with no source is left alone"
out=$(env -u LOOP_PRD_READER $docs check 2>&1)
grep -q "^<!-- prd:begin -->" $H && bad "Home got a block" || ok "a page with no source gets no block and no read"
printf 'Delivery\tcalc.py\nHome\tREADME.md\n' > .loop/docs.tsv
out=$(sync); grep -q "^NO EXTERNAL PRDS" <<<"$out" && ok "sync with no source visits no page and raises no signal" || bad "no source: $out"
reset
echo
[ "$fails" -eq 0 ] && { echo "ALL PASS"; exit 0; } || { echo "$fails FAILED"; exit 1; }
