#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/milestones.py skills/workflow-docs/scripts/pageformat.py skills/workflow-docs/scripts/deployments.py
"""DOC-19 (#4677): every How-to-use row names a Kind and the page carries that Kind's block; a feature page names no command its
How-to-use page leaves out; the README keeps links, not How-to-use tables."""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-docs", "scripts"))
import milestones  # noqa: E402
import pageformat as pf  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


NL = chr(10)
ROWS = ["| `a.py` | Command | Does a thing. | Run `a.py go`. |", "| `b.json` | API/file contract | The settings. | Edit it. |",
        "| `s` | Skill | The skill. | Say it. |", "| nightly | Scheduled routine | The round. | See its runbook. |"]
BLOCKS = [
    "### Command: a.py", "- **Command:** `python3 a.py go`", "- **Dry run:** none", "- **Reads:** its input", "- **Writes:** nothing", "- **Exit codes:** 0 done", "",
    "### API/file contract: b.json", "- **Path:** `b.json`", "- **Fields:** one field", "- **Example:** `{}` here", "- **Writer:** the owner", "- **Reader:** the tool", "",
    "### Skill: s", "- **Say:** \"do it\"", "- **Command:** `/s go`", "",
]
ROUTINE = ["### nightly", "- **Serves:** its requirement", ""]


def page(rows=ROWS, blocks=BLOCKS, runbooks=ROUTINE, header="| Component | Kind | What it is | How a user uses it |"):
    return NL.join(["<!-- workflow-docs -->", "# How to use X", "", "## What it's for", "", "It does a thing.", "", "### What's delivered", "", header,
                    "|---|---|---|---|"] + rows + ["", "## How to reach or run it", ""] + blocks + ["## Runbooks", ""] + runbooks)


def problems(text, on_page=()):
    return [d for _, _, d in milestones.kinds("How-to-use-X", text, on_page)]


check(problems(page()) == [], "a page whose rows each name a Kind and carry that Kind's block passes")
check(any("Kind ''" in d for d in problems(page(rows=[ROWS[0].replace("| Command |", "|  |")] + ROWS[1:]))), "negative control: a delivered row with no Kind is reported")
check(any("Widget" in d for d in problems(page(rows=[ROWS[0].replace("| Command |", "| Widget |")] + ROWS[1:]))), "negative control: an unknown Kind is reported")
check(any("'Dry run'" in d for d in problems(page(blocks=[b for b in BLOCKS if not b.startswith("- **Dry run:**")]))), "negative control: a Command block missing its dry-run form is reported")
check(any("no block" in d for d in problems(page(blocks=BLOCKS[7:]))), "negative control: a row with no block is reported")
check(any("has no row" in d for d in problems(page(rows=ROWS[1:]))), "negative control: a block with no row is reported")
check(any("address" in d for d in problems(page(blocks=[b.replace("none", "mail a" + "@" + "b.co") for b in BLOCKS]))), "negative control: an address in a block is reported")
check(any("header" in d for d in problems(page(header="| Component | What |"))), "negative control: a wrong table header is reported")
check(any("Skill" in d and "/command" in d for d in problems(page(blocks=[b.replace("`/s go`", "go") for b in BLOCKS]))), "negative control: a Skill whose Command is not a /command is reported")
check(problems(page(runbooks=[]), {"nightly"}) == [], "a Scheduled routine row whose runbook is on the feature page passes")
check(any("no block" in d for d in problems(page(runbooks=[]))), "negative control: a Scheduled routine row with no runbook anywhere is reported")

feature = NL.join(["# X", "", "- Run `docs.py check` and `goal.py new SLUG --goal G`.", "", "## Tests", "", "`never.py once`"])
check(milestones.unlisted(feature, "nothing") == ["docs.py check", "goal.py new"], "negative control: a command the feature page names and the How-to-use page lacks is reported")
check(milestones.unlisted(feature, "docs.py check and goal.py new") == [], "a command the How-to-use page lists passes; the Tests section is not read")

FEATS = ["Alpha", "Beta"]
LINKS = NL.join(["## How to use", ""] + ["- [How to use %s](https://github.com/o/r/wiki/How-to-use-%s)" % (f, f) for f in FEATS] + [""])
check(pf.frontdoor(LINKS, FEATS) == [], "a README that only links each How-to-use page passes")
check(any("How-to-use-Beta" in d[2] for d in pf.frontdoor(LINKS.replace("Beta)", "Elsewhere)"), FEATS)), "negative control: a README with no link to a page is reported")
table = NL.join(["### How to use Alpha", "", "| You say | What happens |", "|---|---|", '| "a" | one |', '| "b" | two |', ""])
check(any("table" in d[2] for d in pf.frontdoor(LINKS + table, FEATS)), "negative control: a README How to use table of two rows is reported")
one = NL.join(["### How to use Alpha", "", "| You say | What happens |", "|---|---|", '| "How do I use Alpha?" | Opens [How-to-use-Alpha](https://github.com/o/r/wiki/How-to-use-Alpha). |', ""])
check(pf.frontdoor(LINKS + one, FEATS) == [], "a one-row table whose row links the page passes")
sys.exit(1 if failed else 0)
