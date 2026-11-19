#!/bin/bash
# reads: skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/counting.py
unset LOOP_SESSION_TOOL LOOP_OPERATION_SESSION LOOP_BATCH  # a toy test never reaches a real session tool
# Test wiki images (DOC-19): publish copies each image a page embeds by bare file name to the wiki's top level, where GitHub
# serves it (the wiki repo held only pages, so the bare paths 404ed, e.g. in Safari); check fails an image path publish can't
# deliver (a folder, ../, a missing file), naming the page, the path and the fix. usage: test-wiki-images.sh [DIR]
set -e
export LOOP_ROLE=worker
here=$(cd "$(dirname "$0")/../.." && pwd)
. "$here/dev/toy/reap.sh"
export HOME=$(mktemp -d); export USERPROFILE="$HOME"
d=${1:-$(mktemp -d)}; rm -rf "$d"; mkdir -p "$d"
"$here/dev/toy/make.sh" "$d" >/dev/null
export LOOP_FLOW="$d/flow.json"
docs="python3 $here/skills/workflow-docs/scripts/docs.py"
cd "$d/repo"
python3 "$here/skills/workflow-setup/scripts/setup.py" --bare >/dev/null
git switch -q main; git merge -q --no-edit workflow-setup; git push -q origin main
fails=0
ok() { echo "PASS: $1"; }
bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
wikifile() { git --git-dir="$d/origin.wiki.git" show "main:$1" 2>/dev/null; }
$docs add Diagram --paths calc.py >/dev/null
mkdir -p docs/wiki
printf '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>\n' > docs/wiki/diagram.svg
page() { printf '<!-- workflow-docs -->\n# Diagram\n\nThe toy calculator in one picture, run with python3 calc.py to use it.\n\n![the toy](%s)\n' "$1" > docs/wiki/Diagram.md; git add -A; git commit -qm "page $1"; }

echo "== a bare file name beside the page passes and is published"
page diagram.svg
out=$($docs check 2>&1 || true)
grep -q "^IMAGE" <<<"$out" && bad "a bare file name beside the page was flagged: $out" || ok "a bare file name beside the page passes the check"
$docs publish >/dev/null 2>&1 || true
wikifile diagram.svg | grep -q "<svg" && ok "publish copies the image to the wiki's top level" || bad "the wiki has no diagram.svg"
$docs publish 2>&1 | grep -q "NO CHANGE" && ok "a second publish changes nothing" || bad "second publish"

echo "== negative control: a path publish cannot deliver is refused, naming page, path and fix"
for p in img/diagram.svg ../diagram.svg missing.svg; do
  page "$p"
  out=$($docs check 2>&1 || true)
  grep -q "^IMAGE Diagram: $p is not a file in docs/wiki next to the page.*Fix: keep the image in docs/wiki and embed its bare file name" <<<"$out" && ok "check fails $p" || bad "check let $p pass: $out"
done
page "https://example.org/x.svg"
$docs check 2>&1 | grep -q "^IMAGE" && bad "an absolute URL was flagged as a wiki file" || ok "an absolute URL is left to the links check"
page missing.svg
$docs publish >/dev/null 2>&1 && bad "publish accepted a bad image path" || ok "publish refuses a bad image path"
echo
[ "$fails" -eq 0 ] && { echo "ALL PASS"; exit 0; } || { echo "$fails FAILED"; exit 1; }
