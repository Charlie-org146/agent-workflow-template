#!/bin/bash
# reads: skills/workflow-docs/scripts/sections.py skills/workflow-docs/references/sections.tsv
# Test DOC-25: each page kind has its fixed ## sections in order and README and Home match: a good page passes, and a
# missing, extra, renamed, out-of-order section or a README and Home that differ fails. usage: test-docs-sections.sh
set -u
here=$(cd "$(dirname "$0")/../.." && pwd)
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$here/skills/workflow-docs/scripts"
fails=0
# run KIND PAGE-TEXT: prints the check's findings, one per line
run() { python3 -c 'import sys, sections as s; [print(x[2]) for x in s.check("P", sys.argv[1], sys.argv[2])]' "$1" "$2"; }
sub() { python3 -c 'import sys; print(sys.argv[3].replace(sys.argv[1], sys.argv[2], 1), end="")' "$1" "$2" "$3"; }  # replace the first FROM in TEXT
want() { # NAME KIND TEXT PATTERN-OR-empty: a page that must pass (empty) or fail naming PATTERN
  local out; out=$(run "$2" "$3")
  if { [ -z "$4" ] && [ -z "$out" ]; } || { [ -n "$4" ] && echo "$out" | grep -q "DOC-25.*$4"; }; then echo "PASS: DOC-25 $1"; else echo "FAIL: DOC-25 $1: $out"; fails=1; fi
}
good=$'# t\n\n## System design\n\n## 1. One\n\n## 2. Two\n\n## Requirements by feature\n'
want "a README of the fixed sections passes" front "$good" ""
want "a missing System design section fails" front "$(sub $'## System design\n\n' "" "$good")" "System design"
want "an extra section fails" front "$good## Extra"$'\n' "no more sections"
want "a renamed section fails" front "$(sub 'System design' 'System diagram' "$good")" "System design"
want "an out-of-order section fails" front $'# t\n\n## 1. One\n\n## System design\n\n## 2. Two\n\n## Requirements by feature\n' "System design"
want "an adopted README with the template principles section before the principles passes" front-adopted "$(sub '## 1. One' $'## The template\'s principles\n\n## 1. One' "$good")" ""
want "an adopted README with that section after the principles fails" front-adopted "$(sub '## Requirements by feature' $'## The template\'s principles\n\n## Requirements by feature' "$good")" "template"
feat=$'# F\n\n## Problem\n\n## Requirements\n\n## Non-goals\n\n## Success metrics\n\n## Revisions\n\n## Tests\n'
want "a feature page of the fixed sections passes" feature "$feat" ""
want "a feature page with Non-goals missing fails" feature "$(sub $'## Non-goals\n\n' "" "$feat")" "Non-goals"
want "a feature page with an optional Runbook before Requirements passes" feature "$(sub '## Requirements' $'## Runbook\n\n## Requirements' "$feat")" ""
want "a How-to-use page without Links fails" howto $'# H\n\n## What it\'s for\n\n## How to reach or run it\n\n## URLs and deployments\n' "Links"
want "a Tests page with Other last passes" tests $'# T\n\n## Delivery\n\n## Health\n\n## Other\n' ""
# README and Home: the same sections, and the same sentence and table in a principle
r=$'# t\n\n## System design\n\n## 1. One\n\nSentence.\n\n![d](d.svg)\n\n| a | b |\n|---|---|\n| [X](https://github.com/o/r/wiki/X) | y |\n\n## Requirements by feature\n'
h=$'# t\n\n## System design\n\n## 1. One\n\nSentence.\n\n| a | b |\n|---|---|\n| [X](X) | y |\n\n## Requirements by feature\n'
same() { python3 -c 'import sys, sections as s; [print(x[2]) for x in s.same(sys.argv[1], sys.argv[2])]' "$1" "$2"; }
if [ -z "$(same "$r" "$h")" ]; then echo "PASS: DOC-25 a README and a Home with the same sections and principle text pass, links read alike and a diagram line ignored"; else echo "FAIL: DOC-25 same pages"; fails=1; fi
if same "$r" "$(sub '## Requirements by feature' $'## Settings\n\n## Requirements by feature' "$h")" | grep -q "same sections"; then echo "PASS: DOC-25 a Home with a section the README lacks fails"; else echo "FAIL: DOC-25 extra Home section"; fails=1; fi
if same "$r" "$(sub 'Sentence.' 'Another sentence.' "$h")" | grep -q "'1. One' is the same"; then echo "PASS: DOC-25 a principle sentence that differs between README and Home fails"; else echo "FAIL: DOC-25 sentence differs"; fails=1; fi
[ $fails = 0 ] && echo "ALL PASS" || { echo "FAILED"; exit 1; }
