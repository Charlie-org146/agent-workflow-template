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
# DOC-27: a feature in the new form (sections, five requirements, metric and tests each, reference, milestone, Reviewed mark)
if python3 - "$here" <<'PY'
import contextlib, io, os, sys, tempfile
from types import SimpleNamespace as SimpleNamespaceX
sys.path.insert(0, os.path.join(sys.argv[1], "skills/workflow-docs/scripts"))
import sections as s
slug = "o/r"
GOOD = """- X-1: **Unreviewed** A feature <!-- reviewed abcd1234 -->
  - Milestone: [v1](https://github.com/o/r/milestone/3)
  - **Promise.** It works.
  - ### Problem
  - Something is wrong.
  - ### Requirements
  - Functional
  - 1.1 A rule
  - **Success metric 1.1.** Things broken.
  - Target **0**
  - Today **not measured**
  - Test cases
  - A broken thing fails the check.
  - Non-functional
  - None
  - ### Non-goals
  - It does nothing else.
  - ### Success metrics
  - \\# | Metric | Target | Today
  - 1.1 | Things broken. | 0 | not measured
  - ### Reference
  - adopted
  - [A source](https://example.org/a). Why it applies.
  - ### Revisions
  - r1 2026-11-22
"""
def run(text, reviews=None):
    d = tempfile.mkdtemp()
    out = []
    for f in s.blocks(text):
        out += s.feature("P", *f, slug, reviews or {})
    return out
def sub(a, b, text=GOOD):
    assert a in text, a
    return text.replace(a, b, 1)
fails = 0
def case(name, text, kind=None, want="", reviews=None):
    global fails
    got = run(text, reviews)
    hit = [x for x in got if (kind is None or x[0] == kind) and want in x[2]]
    ok = (not got) if kind is None and not want else bool(hit)
    print(("PASS" if ok else "FAIL") + ": DOC-27 " + name + ("" if ok else ": %s" % got))
    fails += not ok
case("a feature of the fixed shape passes", GOOD)
OLDFORM = sub("  - ### Revisions\n  - r1 2026-11-22\n", "", sub("  - ### Success metrics\n  - \\# | Metric | Target | Today\n  - 1.1 | Things broken. | 0 | not measured\n", "", GOOD))
for fid in ("DEL-19", "DEL-23"):
    sealed = sub("- X-1:", "- %s:" % fid, sub("**Unreviewed**", "**Reviewed 2026-11-21**", OLDFORM))
    case("%s, sealed with its sections missing, is reported as NOTE only (o721)" % fid, sealed, "NOTE", "the sections are")
    fails += any(x[0] == "FORMAT" for x in run(sealed))
    print(("FAIL" if fails else "PASS") + ": DOC-27 %s has no FORMAT finding" % fid)
case("negative control: any other feature with the same sections missing still fails", sub("**Unreviewed**", "**Reviewed 2026-11-21**", OLDFORM), "FORMAT", "the sections are")
case("a feature missing only its Revisions section still fails", sub("  - ### Revisions\n  - r1 2026-11-22\n", ""), "FORMAT", "the sections are")
case("an empty Problem fails", sub("  - Something is wrong.\n", ""), "FORMAT", "Problem is empty")
case("a feature with no milestone fails", sub("  - Milestone: [v1](https://github.com/o/r/milestone/3)\n", ""), "FORMAT", "Milestone")
case("a milestone link to another repo fails", sub("github.com/o/r/", "github.com/x/y/"), "FORMAT", "Milestone")
case("Non-goals before Requirements fails", sub("  - ### Requirements\n", "  - ### Non-goals\n  - none\n  - ### Requirements\n", sub("  - ### Non-goals\n  - It does nothing else.\n", "")), "FORMAT", "the sections are")
case("a sixth functional requirement fails", sub("  - Non-functional\n", "".join("  - 1.%d R\n  - **Success metric 1.%d.** M.\n  - Target **0**\n  - Today **1**\n  - Test cases\n  - c\n" % (i, i) for i in range(2, 7)) + "  - Non-functional\n"), "FORMAT", "more than five")
case("a requirement with no metric is reported, not failed, while Unreviewed", sub("  - **Success metric 1.1.** Things broken.\n", ""), "NOTE", "no target" if False else "success metrics")
case("a requirement with no metric fails once Reviewed", sub("**Unreviewed**", "**Reviewed 2026-11-22**", sub("  - **Success metric 1.1.** Things broken.\n", "")), "FORMAT", "success metrics", {"X-1": "o9"})
case("a requirement with no test case is reported", sub("  - A broken thing fails the check.\n", ""), "NOTE", "no test case")
case("a metric with no target is reported", sub("  - Target **0**\n", ""), "NOTE", "no target")
case("a table that differs from the inline metrics fails", sub("1.1 | Things broken. | 0", "1.1 | Other. | 0", GOOD), "FORMAT", "does not match")
case("a reference with no tag is reported", sub("  - adopted\n", ""), "NOTE", "Reference has no entry")
case("a reference with no link is reported", sub("[A source](https://example.org/a). Why", "A source. Why"), "NOTE", "no linked source")
RV = sub("**Unreviewed**", "**Reviewed 2026-11-22**")
case("a Reviewed mark dated on or after the rule with no .loop/reviews.tsv line fails", RV, "FORMAT", "no line in .loop/reviews.tsv")
case("the same mark with its line passes", RV, None, "", {"X-1": "o9"})
case("a Reviewed mark from before the rule with no line is reported, not failed", sub("**Unreviewed**", "**Reviewed 2026-11-21**"), "NOTE", "no line in .loop/reviews.tsv")
# DOC-27.5: the mark command's record check and the committed line
import json
d = tempfile.mkdtemp()
os.makedirs(os.path.join(d, "wiki")); os.makedirs(os.path.join(d, ".loop")); os.makedirs(os.path.join(d, "common"))
open(os.path.join(d, "wiki", "P.md"), "w").write(GOOD)
rows = [("o1", "operation", "X-1"), ("o2", "operation", "X-1,X-2"), ("o3", "operation-top", "X-1")]
open(os.path.join(d, "common", "owner-words.tsv"), "w").write("".join("%s\t2026-11-22T00:00:00Z\t%s\t%s\t%s\n" % (r, src, json.dumps("words"), ids) for r, src, ids in rows))
def mark(ids, rec):
    try:
        s.reviewed(d, os.path.join(d, "wiki"), "review", ids, rec, os.path.join(d, "common"), "2026-11-22")
        return ""
    except SystemExit as e:
        return str(e)
def want(name, ok):
    global fails
    print(("PASS" if ok else "FAIL") + ": DOC-27 " + name)
    fails += not ok
out = mark(["X-1"], "o2")
want("one record naming two IDs is refused for a new-form mark", "exactly X-1" in out and not os.path.exists(os.path.join(d, ".loop", "reviews.tsv")))
want("a relayed record (not the owner's source) is refused", "exactly X-1" in mark(["X-1"], "o3"))
want("typed words naming two IDs at once are refused", "exactly X-1" in mark(["X-1", "Z-9"], ""))
want("an unknown record is refused", "exactly X-1" in mark(["X-1"], "o99"))
want("an owner record naming exactly the ID passes and writes only ID, record and date", mark(["X-1"], "o1") == "" and open(os.path.join(d, ".loop", "reviews.tsv")).read() == "X-1\to1\t2026-11-22\n")
want("an old-form requirement needs no line", mark(["Y-1"], "o2") == "" and open(os.path.join(d, ".loop", "reviews.tsv")).read() == "X-1\to1\t2026-11-22\n")
case("a reference naming only a host, no specific source, is reported", sub("https://example.org/a", "https://example.org"), "NOTE", "no linked source")
pd = tempfile.mkdtemp()
def principles(a, b):
    open(os.path.join(pd, "Principles.md"), "w").write("## 1. One\n\n| [%s name](P) |\n\n## 2. Two\n\n| [%s name](P) |\n" % (a, b))
principles("X-1", "Y-1")
want("a feature listed under exactly one principle passes", s.principled(pd, "X-1") == [])
principles("X-1", "X-1")
want("a feature listed under two principles fails", "2 principles" in str(s.principled(pd, "X-1")))
principles("Y-1", "Y-2")
want("a feature listed under no principle fails", "0 principles" in str(s.principled(pd, "X-1")))
# DOC-27.1 and 27.3: whole-page shape, a text change with no new revision row, a typed score against health's latest run
import milestones, deployments, counting  # noqa: E402
check_ = lambda name, ok: want(name, bool(ok))
check_("a change outside Revisions with Revisions untouched is a change with no new row", milestones.unrowed("## Problem\ntext\n## Revisions\nr1\n", "## Problem\nnew\n## Revisions\nr1\n"))
check_("a change with a new Revisions row is fine", not milestones.unrowed("## Problem\ntext\n## Revisions\nr1\n", "## Problem\nnew\n## Revisions\nr1\nr2\n"))
check_("an unchanged page is fine", not milestones.unrowed("## Problem\ntext\n## Revisions\nr1\n", "## Problem\ntext\n## Revisions\nr1\n"))
import subprocess as sp
rt = tempfile.mkdtemp()
g = lambda *a: sp.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(a), cwd=rt, capture_output=True, text=True)
g("init", "-q", "-b", "main")
os.makedirs(os.path.join(rt, "docs", "wiki")); os.makedirs(os.path.join(rt, ".loop"))
open(os.path.join(rt, ".loop", "config.json"), "w").write('{"criteria": true, "base": "main"}\n')
PAGE = "<!-- workflow-docs -->\n# P\n\n## Problem\n\nx\n\n## Requirements\n\n## Non-goals\n\n## Success metrics\n\n## Reference\n\n## Revisions\n\n| r1 |\n\n## Tests\n"
open(os.path.join(rt, "docs", "wiki", "P.md"), "w").write(PAGE)
g("add", "-A"); g("commit", "-qm", "base"); g("update-ref", "refs/remotes/origin/main", "HEAD")
counting.repo_slug = lambda r: "o/r"
check_("a whole page of the seven sections passes", milestones.new_form(rt) == [])
open(os.path.join(rt, "docs", "wiki", "P.md"), "w").write(PAGE.replace("## Non-goals\n\n", ""))
check_("a whole page missing a section fails", any("sections are not" in x[2] for x in milestones.new_form(rt)))
open(os.path.join(rt, "docs", "wiki", "P.md"), "w").write(PAGE.replace("x\n", "changed\n"))
check_("a page whose text changed with no new revision row fails", any("no new revision row" in x[2] for x in milestones.new_form(rt)))
open(os.path.join(rt, "docs", "wiki", "P.md"), "w").write(PAGE.replace("x\n", "changed\n").replace("| r1 |\n", "| r1 |\n| r2 |\n"))
check_("the same change with a new revision row passes", milestones.new_form(rt) == [])
FEATP = "- X-1: **Unreviewed** A feature\n  - ### Problem\n  - old\n  - ### Revisions\n  - r1\n"
open(os.path.join(rt, "docs", "wiki", "Q.md"), "w").write(FEATP)
g("add", "-A"); g("commit", "-qm", "q"); g("update-ref", "refs/remotes/origin/main", "HEAD")
open(os.path.join(rt, "docs", "wiki", "Q.md"), "w").write(FEATP.replace("old", "new"))
check_("a feature whose text changed with no new revision row fails", any("Q:X-1" in x[1] and "no new revision row" in x[2] for x in milestones.new_form(rt)))
open(os.path.join(rt, "docs", "wiki", "Q.md"), "w").write(FEATP.replace("old", "new").replace("  - r1\n", "  - r1\n  - r2\n"))
check_("a feature changed with a new revision row passes", not [x for x in milestones.new_form(rt) if x[1].startswith("Q")])
import sections  # noqa: E402
ROW = "| [XX-1 A](u) | s | f | Docs | 50%% | %s |\n"
open(os.path.join(rt, "README.md"), "w").write("|a|\n" + ROW % "100% (1 of 1)")
tests = [["t1", "land", "c", "XX-1"]]
open(os.path.join(rt, ".loop", "regression.tsv"), "w").write("id\tlevel\tcommand\tgoal\n" + "\t".join(tests[0]) + "\n")
sections.latest_full = lambda slug, ids: {"t1": "PASS"}
check_("a typed score equal to health's latest run passes", milestones.new_form(rt, True) == [])
open(os.path.join(rt, "README.md"), "w").write("|a|\n" + ROW % "100% (2 of 2)")
check_("a typed score that differs from health's latest run fails the strict check", any("differs from health's latest run" in x[2] for x in milestones.new_form(rt, True)))
check_("the same typed score is not compared when not strict", not any("health" in x[2] for x in milestones.new_form(rt, False)))
sections.latest_full = lambda slug, ids: None
check_("a typed score with no health run says there is no run to compare, and fails", any("no health run to compare" in x[2] for x in milestones.new_form(rt, True)))
open(os.path.join(rt, "README.md"), "w").write("|a|\n" + ROW % "not measured: no data yet")
check_("a score that is not a typed number needs no run", not any("health" in x[2] for x in milestones.new_form(rt, True)))
# DOC-27.4: the page rebuild, reported as NOTE findings; docs.py check --strict fails them
sys.path.insert(0, os.path.join(sys.argv[1], "skills", "workflow-release", "scripts"))
import brief as brief27  # noqa: E402
rb = tempfile.mkdtemp()
os.makedirs(os.path.join(rb, "docs", "wiki", "flows")); os.makedirs(os.path.join(rb, ".loop"))
HEADER = "| " + " | ".join(brief27.COLS27) + " |\n|---|---|---|---|---|---|---|---|---|\n"
FRONT = "3 of 5 reviewed\n\n" + HEADER
def front(readme=FRONT, home=FRONT, extra=None, figs=()):
    for f in os.listdir(os.path.join(rb, "docs", "wiki")):
        if os.path.isfile(os.path.join(rb, "docs", "wiki", f)):
            os.remove(os.path.join(rb, "docs", "wiki", f))
    open(os.path.join(rb, "README.md"), "w").write(readme)
    for name, text in {"Home": home, "Principles": HEADER, "Tests": "t", "Roadmap": "r", "Topic": "topic ![](flows/X-1.svg)\n", **(extra or {})}.items():
        open(os.path.join(rb, "docs", "wiki", name + ".md"), "w").write(text)
    open(os.path.join(rb, ".loop", "docs.tsv"), "w").write("Topic\tskills\n")
    for f in ("X-1.svg",) + tuple(figs):
        open(os.path.join(rb, "docs", "wiki", "flows", f), "w").write("<svg/>")
notes = lambda: brief27.rebuild(rb, "docs/wiki")
front()
want("DOC-27.4 a structure with the nine columns, the reviewed line, no How-to page and every figure shown has nothing to report", notes() == [])
front(readme=FRONT.replace("| Review |", "| Mine |"))
want("DOC-27.4 a principle table that lost its Review column is reported", any("principle table columns" in x[2] and x[1] == "README" for x in notes()))
front(home=FRONT.replace("| Today | Reference |", "| Reference | Today |"))
want("DOC-27.4 a principle table with two columns swapped is reported", any("principle table columns" in x[2] and x[1] == "Home" for x in notes()))
front(readme="x\n\n" + HEADER)
want("DOC-27.4 a front page with no 'N of M reviewed' line is reported", any("N of M reviewed" in x[2] for x in notes()))
front(extra={"How-to-use-Topic": "h"})
want("DOC-27.4 a How-to-use page is reported with its count", any("1 How-to-use pages to remove" in x[2] for x in notes()))
front(extra={"Stray": "s"})
want("DOC-27.4 a wiki page of no listed kind is reported", any("pages of no listed kind (Stray)" in x[2] for x in notes()))
front(figs=("old.svg", "older.svg"))
want("DOC-27.4 figure files no page shows are reported, counted", any("2 figure files no page shows" in x[2] for x in notes()))
want("DOC-27.4 every item is a NOTE, so the default check reports it and does not fail", all(x[0] == "NOTE" for x in notes()))
# --strict turns every NOTE into a failure; without it a NOTE alone passes
import docs  # noqa: E402
docs.top = lambda: rb
docs.read_map = lambda r: {"Topic": ["skills"]}
docs.problems = lambda r, b: []
docs.counts = lambda r: []
docs.entry.problems = lambda r: []
docs.entry.perm_check = lambda r: []
docs.contract = lambda r, s=False: [("NOTE", "Topic", "DOC-27 27.4: 1 How-to-use pages to remove (x)")]
mk = lambda strict: SimpleNamespaceX(base="", own=None, strict=strict)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    plain = docs.cmd_check(mk(False))
    hard = docs.cmd_check(mk(True))
want("DOC-27.4 docs.py check reports a rebuild NOTE and passes, and --strict fails on the same NOTE", plain == 0 and hard == 1)
sys.exit(1 if fails else 0)
PY
then :; else fails=1; fi
[ $fails = 0 ] && echo "ALL PASS" || { echo "FAILED"; exit 1; }
