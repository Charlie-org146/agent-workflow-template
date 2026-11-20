#!/bin/bash
# reads: skills/workflow-docs/scripts/sections.py
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
good=$'# t\n\n## What this is\n\n## System design\n\n## 1. One\n\n## 2. Two\n\n## Requirements by feature\n'
want "a README of the fixed sections passes" front "$good" ""
want "a missing System design section fails" front "$(sub $'## System design\n\n' "" "$good")" "System design"
want "an extra section fails" front "$good## Extra"$'\n' "no more sections"
want "a renamed section fails" front "$(sub 'System design' 'System diagram' "$good")" "System design"
want "an out-of-order section fails" front $'# t\n\n## What this is\n\n## 1. One\n\n## System design\n\n## 2. Two\n\n## Requirements by feature\n' "System design"
want "an adopted README with the template principles section before the principles passes" front-adopted "$(sub '## 1. One' $'## The template\'s principles\n\n## 1. One' "$good")" ""
want "an adopted README with that section after the principles fails" front-adopted "$(sub '## Requirements by feature' $'## The template\'s principles\n\n## Requirements by feature' "$good")" "template"
feat=$'# F\n\n## Problem\n\n## Requirements\n\n## Non-goals\n\n## Success metrics\n\n## Revisions\n\n## Tests\n'
want "a feature page of the fixed sections passes" feature "$feat" ""
want "a feature page with Non-goals missing fails" feature "$(sub $'## Non-goals\n\n' "" "$feat")" "Non-goals"
want "a feature page with an optional Runbook before Requirements passes" feature "$(sub '## Requirements' $'## Runbook\n\n## Requirements' "$feat")" ""
want "a feature page with an optional Deployments before Revisions passes" feature "$(sub '## Revisions' $'## Deployments\n\n## Revisions' "$feat")" ""
want "a feature page with Deployments after Revisions fails" feature "$(sub '## Tests' $'## Deployments\n\n## Tests' "$feat")" "Deployments"
want "a feature page with Deployments before Success metrics fails" feature "$(sub '## Success metrics' $'## Deployments\n\n## Success metrics' "$feat")" "Deployments"
want "a How-to-use page without Links fails" howto $'# H\n\n## What it\'s for\n\n## How to reach or run it\n\n## URLs and deployments\n' "Links"
want "a Tests page with Other last passes" tests $'# T\n\n## Delivery\n\n## Health\n\n## Other\n' ""
prin=$'# P\n\n## 1. One\n\n## 2. Two\n'
want "a Principles page of one section per principle passes" principles "$prin" ""
want "a Principles page with a section that is not a principle fails" principles "$prin"$'\n## Extra\n' "no more sections"
want "a Tests page with Other not last fails" tests $'# T\n\n## Other\n\n## Health\n' "got Other"
# DOC-25 bullet 2: a Part 1 row with no figure fails, even one still marked v2.0 planned
fig() { # FLOW-CELL: the docs check on a one-principle README whose one row has that Flow cell
  python3 -c '
import sys, pageformat as pf
listing = "## The principles\n\n| 1 | Docs | The sentence. | a |\n"
row = "| [X-1 A](u)%s | s | f | Docs | 0%% | |" % sys.argv[1]
page = "# t\n\n[wiki](https://x/wiki/Home)\n\n## 1. Docs\n\nThe sentence.\n\n| Requirement | Summary | Follows | Feature | Adoption | Confidence |\n|---|---|---|---|---|---|\n" + row + "\n\n## Requirements by feature\n"
print("\n".join(x[2] for x in pf.frontdoor("README", page, listing, {"flows/X-1.svg"}) if "Flow link" in x[2]))' "$1"
}
if fig "" | grep -q "DOC-23 a Flow link"; then echo "PASS: DOC-25 a planned row with no figure fails the docs check"; else echo "FAIL: DOC-25 row with no figure"; fails=1; fi
if [ -z "$(fig " ([X-1 flow](docs/wiki/flows/X-1.svg))")" ]; then echo "PASS: DOC-25 a planned row that links its figure passes"; else echo "FAIL: DOC-25 row with a figure"; fails=1; fi
# README and Home: the same sections, and the same sentence and table in a principle
r=$'# t\n\n## What this is\n\n## System design\n\n## 1. One\n\nSentence.\n\n![d](d.svg)\n\n| a | b |\n|---|---|\n| [X](https://github.com/o/r/wiki/X) | y |\n\n## Requirements by feature\n'
h=$'# t\n\n## What this is\n\n## System design\n\n## 1. One\n\nSentence.\n\n| a | b |\n|---|---|\n| [X](X) | y |\n\n## Requirements by feature\n'
same() { python3 -c 'import sys, sections as s; [print(x[2]) for x in s.same(sys.argv[1], sys.argv[2])]' "$1" "$2"; }
if [ -z "$(same "$r" "$h")" ]; then echo "PASS: DOC-25 a README and a Home with the same sections and principle text pass, links read alike and a diagram line ignored"; else echo "FAIL: DOC-25 same pages"; fails=1; fi
if same "$r" "$(sub '## Requirements by feature' $'## Settings\n\n## Requirements by feature' "$h")" | grep -q "same sections"; then echo "PASS: DOC-25 a Home with a section the README lacks fails"; else echo "FAIL: DOC-25 extra Home section"; fails=1; fi
if same "$r" "$(sub 'Sentence.' 'Another sentence.' "$h")" | grep -q "'1. One' is the same"; then echo "PASS: DOC-25 a principle sentence that differs between README and Home fails"; else echo "FAIL: DOC-25 sentence differs"; fails=1; fi
# the render: Adoption from the Follows tags (adopted 1, adapted or own 0), the figure link inside the Requirement cell, What this is from DEL-19
mig() { python3 -c '
import sys, sections as s
page = "# t\n\n## System design\n\n## 1. One\n\nSentence.\n\n| Requirement | Summary | Follows | Feature | " + sys.argv[1] + " |\n|---|---|---|---|---|---|\n| [X-1 A](u) | s | a: adopted; b: adapted | Docs | v1.0 | [f](flows/X-1.svg) |\n| [X-2 B](u) | s | c: own | Docs | v1.0 | [f](flows/X-2.svg) |\n"
print(s.fresh(page, ".", lambda p: "- DEL-19: **Reviewed** t\n  - It is a loop. [DEL-19]\n  - Done. [DEL-2]\n"))' "$1"; }
out=$(mig "Version | Flow")
if echo "$out" | grep -qF "| [X-1 A](u) ([f](flows/X-1.svg)) | s | a: adopted; b: adapted | Docs | 50% |  |" && echo "$out" | grep -qF "| Adoption | Confidence |"; then echo "PASS: DOC-25 the render moves the figure link into the Requirement cell and computes Adoption from the Follows tags"; else echo "FAIL: DOC-25 migrate: $out"; fails=1; fi
if echo "$out" | grep -qF "Adoption: 25% (the average" && echo "$out" | grep -qF "It is a loop. Done."; then echo "PASS: DOC-25 the render averages Adoption per principle and writes What this is from DEL-19"; else echo "FAIL: DOC-25 average: $out"; fails=1; fi
if [ "$(mig "Adoption | Confidence" | grep -c "^| \[X-")" = 2 ]; then echo "PASS: DOC-25 a table already in the new columns, with a blank Confidence, is kept"; else echo "FAIL: DOC-25 new columns kept"; fails=1; fi
# an adopted repo: no DEL-19 leaves What this is as written; with DEL-19 it renders from it (negative control); no Follows tag anywhere is
# "not measured", never 0% (negative control: tagged rows keep their percentages and an empty Confidence stays empty)
adopted() { # DEL19-TEXT TABLE-ROW-FOLLOWS: fresh() on a front page with a hand-written What this is and one principle row with that Follows cell
  python3 -c '
import sys, sections as s
page = "# t\n\n## What this is\n\nMy own words.\n\n## System design\n\n## 1. One\n\nSentence.\n\n| Requirement | Summary | Follows | Feature | Adoption | Confidence |\n|---|---|---|---|---|---|\n| [X-1 A](u) | s | " + sys.argv[2] + " | Docs | 0% | |\n"
print(s.fresh(page, ".", lambda p: sys.argv[1]), end="")' "$1" "$2"; }
out=$(adopted "" "")
if echo "$out" | grep -qF "My own words." && echo "$out" | grep -qF "| Docs | not measured: no references recorded yet | not measured: no data yet |" && echo "$out" | grep -qF "Adoption: not measured: no references recorded yet." && ! echo "$out" | grep -q "0%"; then echo "PASS: DOC-25 a repo with no DEL-19 keeps What this is, and rows with no Follows tag read not measured, never 0%"; else echo "FAIL: DOC-25 adopted repo: $out"; fails=1; fi
out=$(adopted $'- DEL-19: **Reviewed** t\n  - Generated. [DEL-19]\n' "a: adopted; b: own")
if echo "$out" | grep -qF "Generated." && ! echo "$out" | grep -qF "My own words." && echo "$out" | grep -qF "| Docs | 50% |  |" && echo "$out" | grep -qF "Adoption: 50% (the average"; then echo "PASS: DOC-25 negative control: with DEL-19 and Follows tags What this is renders from DEL-19 and the percentages stay"; else echo "FAIL: DOC-25 template render: $out"; fails=1; fi
# What this is: fresh() rewrites only the generated first paragraph; owner paragraphs after it stay byte for byte
keep() { # TEXT: sections.fresh on a front page whose Delivery page has DEL-19 "Gen."
  python3 -c '
import sys, sections as s
print(s.fresh(sys.argv[1], "d", lambda _: "- DEL-19: x\n  - Gen. [DEL-19]\n"), end="")' "$1"; }
own=$'# t\n\n## What this is\n\nOld generated.\n\nOwner one.\n\nOwner two, kept.\n\n## System design\n\n## 1. One\n'
out=$(keep "$own")
if [ "$out" = "$(sub 'Old generated.' 'Gen.' "$own")" ]; then echo "PASS: DOC-25 a What this is with owner paragraphs after the generated one keeps them byte for byte"; else echo "FAIL: DOC-25 owner paragraphs kept: $out"; fails=1; fi
gen=$'# t\n\n## What this is\n\nGen.\n\n## System design\n\n## 1. One\n'
if [ "$(keep "$gen")" = "${gen%$'\n'}" ]; then echo "PASS: DOC-25 a What this is of only the generated paragraph is unchanged"; else echo "FAIL: DOC-25 generated only: $(keep "$gen")"; fails=1; fi
if [ "$(keep "$(sub 'Gen.' 'Stale.' "$gen")")" = "${gen%$'\n'}" ]; then echo "PASS: DOC-25 a stale generated paragraph is rewritten"; else echo "FAIL: DOC-25 stale paragraph not rewritten"; fails=1; fi
if python3 -c '
import sys, counting
o = counting.origins(sys.argv[1])
sys.exit(not ("https://rework.withgoogle.com" in o and "https://www.gitguardian.com" in o and "https://example.invalid" not in o))' "$here"; then echo "PASS: DOC-19 public_origins holds the two new hosts and still refuses an unlisted one"; else echo "FAIL: DOC-19 public_origins"; fails=1; fi
[ $fails = 0 ] && echo "ALL PASS" || { echo "FAILED"; exit 1; }
