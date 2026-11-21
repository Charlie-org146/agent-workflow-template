#!/bin/bash
# reads: skills/workflow-release/scripts/wiki.py skills/workflow-docs/scripts/entry.py skills/workflow-docs/scripts/audit.py
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH
# #5317: wiki.py prepare --commit commits the START.md, CLAUDE.md and AGENTS.md that entry.write regenerates, so the head
# merge.py audits is not stale. No remote is used. usage: test-wiki-start.sh [DIR]
set -e
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d)
export USERPROFILE="$HOME"
d=${1:-$(mktemp -d)}; rm -rf "$d"; mkdir -p "$d"
"$here/dev/toy/make.sh" "$d"
docs="python3 $here/skills/workflow-docs/scripts/docs.py"
entry="python3 $here/skills/workflow-docs/scripts/entry.py"
wiki="python3 $here/skills/workflow-release/scripts/wiki.py"
cd "$d/repo"
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
last() { git show --name-only --format= HEAD | sort | tr '\n' ' '; }

$docs add Calc --paths calc.py >/dev/null
printf '<!-- workflow-docs -->\n# Calc\n\n## Problem\n\nPeople need a toy calculator.\n\n## Requirements\n\n- CAL-1: **Unreviewed** it adds\n' > docs/wiki/Calc.md
$entry write >/dev/null; git add -A; git commit -qm "Add the Calc page"
git switch -q -c loop/s
echo "== negative control: nothing generated changed"
before=$(git rev-parse HEAD)
$wiki prepare s --commit >/dev/null 2>&1 || true
[ "$(git rev-parse HEAD)" = "$before" ] && [ -z "$(git status --porcelain)" ] && ok "nothing changed: no extra commit and nothing staged" || bad "an extra commit or change with nothing stale ($(git log --format=%s $before..HEAD | tr '\n' ';'))"

echo "== a page edit moves what START.md is built from"
sed -i.bak 's/People need a toy calculator\./People need a toy calculator that also has s./' docs/wiki/Calc.md; rm -f docs/wiki/Calc.md.bak
$wiki prepare s --commit >/dev/null 2>&1 || true
[ -z "$(git status --porcelain)" ] && ok "prepare --commit leaves nothing uncommitted" || bad "left uncommitted: $(git status --porcelain | tr '\n' ' ')"
git show --name-only --format= HEAD~0 | grep -q "^.loop/START.md$" || git log --name-only --format= "$before..HEAD" | grep -q "^.loop/START.md$" \
  && ok "START.md is in the commits" || bad "START.md is in no commit"
$entry check 2>&1 | grep -q "ENTRY_STALE" && bad "START.md is stale at HEAD" || ok "START.md is current at HEAD"
for f in CLAUDE.md AGENTS.md; do
  [ -z "$(git status --porcelain -- $f)" ] && ok "$f is not left dirty" || bad "$f left dirty"
done

echo "== a tracked CLAUDE.md whose generated block went stale is committed too"
printf '# Toy\n\n<!-- workflow-loop -->\n## Workflow loop\n\n- stale line\n<!-- /workflow-loop -->\n' > CLAUDE.md
git add -A; git commit -qm "A CLAUDE.md with a stale generated block"
before=$(git rev-parse HEAD)
$wiki prepare s --commit >/dev/null 2>&1 || true
[ -z "$(git status --porcelain)" ] && ok "a stale CLAUDE.md block leaves nothing uncommitted" || bad "left uncommitted: $(git status --porcelain | tr '\n' ' ')"
git log --name-only --format= "$before..HEAD" | grep -qx "CLAUDE.md" && ok "CLAUDE.md is in a commit" || bad "CLAUDE.md is in no commit"
[ "$(git log -1 --format=%s)" = "Regenerate CLAUDE.md for s" ] && ok "the message names the file committed" || bad "message: $(git log -1 --format=%s)"

echo "== only what entry.write changed is committed: a hand edit and a deletion stay out"
printf '# Toy\n\n<!-- workflow-loop -->\n## Workflow loop\n\n- stale line\n<!-- /workflow-loop -->\n' > AGENTS.md
git add -A; git commit -qm "Track AGENTS.md with a stale block"
echo "my own note" >> CLAUDE.md
rm AGENTS.md
before=$(git rev-parse HEAD)
out=$($wiki prepare s --commit 2>&1 || true)
git log --name-only --format= "$before..HEAD" | grep -qx "CLAUDE.md" && bad "a hand edit to CLAUDE.md was committed" || ok "a hand edit to CLAUDE.md is not committed"
git log --name-only --format= "$before..HEAD" | grep -qx "AGENTS.md" && bad "a deleted AGENTS.md was committed" || ok "a deleted tracked AGENTS.md is not committed"
grep -q "WARNING: CLAUDE.md had edits" <<<"$out" && grep -q "WARNING: AGENTS.md had edits" <<<"$out" && ok "each file left alone is named in a warning" || bad "no warning naming both files: $out"
git status --porcelain | grep -q "CLAUDE.md" && git status --porcelain | grep -q "AGENTS.md" && ok "both stay as the owner left them" || bad "a file was touched"
exit $((fails > 0))
