#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/milestones.py skills/workflow-docs/scripts/pageformat.py skills/workflow-docs/scripts/deployments.py
"""DOC-19 (#4698, #4784, #4677): a How-to-use page's System diagram matches its What's delivered table; wiki pages and skill docs hold
no history link, other host, other-repo reference or machine path; Home carries the whole-system diagram; a feature page names no skill
or schedule its How-to-use page leaves out."""
import os
import sys
import tempfile

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
FENCE = chr(96) * 3
ROWS = ["| `a.py` | Command | Does a thing. | Run it. |", "| `s` | Skill | The skill. | Say it. |"]
BOXES = ["[Skill: s | the agent session] --calls--> [Command: a.py | the repo checkout]", "", "Legend: a box is a part and where it runs."]


def page(rows=ROWS, boxes=BOXES, diagram=True):
    lines = ["# How to use X", "", "## What it's for", "", "### What's delivered", "", "| Component | Kind | What it is | How a user uses it |", "|---|---|---|---|"] + rows + [""]
    if diagram:
        lines += ["### System diagram", "", FENCE + "text"] + boxes + [FENCE, ""]
    return NL.join(lines + ["## How to reach or run it", ""])


def says(found, text):
    return any(text in d for _, _, d in found)


check(milestones.diagram("X", page()) == [], "a System diagram with a box for each delivered row, where it runs and a legend passes")
check(says(milestones.diagram("X", page(diagram=False)), "no System diagram"), "negative control: a How-to-use page with no System diagram is reported")
check(says(milestones.diagram("X", page(boxes=BOXES[:1][0:0] + ["[Skill: s | the agent session]", "Legend: x"])), "Command: a.py"), "negative control: a delivered row with no box is reported, naming the part")
check(says(milestones.diagram("X", page(boxes=BOXES[:1] + ["[Command: ghost.py | the PC]"] + BOXES[1:])), "Command: ghost.py"), "negative control: a box the table lacks is reported, naming the part")
check(says(milestones.diagram("X", page(boxes=BOXES[:2])), "Legend"), "negative control: a diagram with no legend is reported")
check(says(milestones.diagram("X", page(boxes=["[Skill: s]", "[Command: a.py]", "Legend: x"])), "Skill: s"), "negative control: a box that says no where the part runs is not a box and is reported")

REPO = "me/proj"
own = "See https://github.com/me/proj/milestone/3 and https://github.com/me/proj/wiki/Home."
check(milestones.stands_alone("P", own, REPO) == [], "this repo's own milestone and wiki links stand")
check(says(milestones.stands_alone("P", "Fixed in https://github.com/me/proj/issues/12.", REPO), "issues/12"), "negative control: an issue link is reported")
check(says(milestones.stands_alone("P", "Run https://github.com/me/proj/actions/runs/9 .", REPO), "actions/runs/9"), "negative control: a CI link is reported")
check(says(milestones.stands_alone("P", "See https://example.org/doc .", REPO), "example.org"), "negative control: another host is reported")
check(says(milestones.stands_alone("P", "Like https://github.com/other/thing/milestone/1", REPO), "other/thing"), "negative control: another repo's milestone is reported")
check(says(milestones.stands_alone("P", "Follows other/thing#44 closely.", REPO), "other/thing#44"), "negative control: an owner/repo#N reference is reported")
check(says(milestones.stands_alone("P", "Edit C:" + chr(92) + "Users" + chr(92) + "me" + chr(92) + "x.", REPO), "Users"), "negative control: a machine path is reported")
check(says(milestones.stands_alone("P", "Open /home/me/x for it.", REPO), "/home/"), "negative control: a home path is reported")
check(milestones.stands_alone("P", NL.join(["## Tests", "https://github.com/me/proj/issues/1", "## Deployments", "https://example.org/live", "## Other", "plain"]), REPO) == [],
      "the generated Tests section and a Deployments table are not read")
check(says(milestones.stands_alone("P", NL.join(["## Tests", "x", "## Requirements", "https://example.org/a"]), REPO), "example.org"), "negative control: a link after the Tests section is read again")

HOME = NL.join(["# r", "", "<!-- diagram:begin -->", "## System diagram", FENCE + "text", "operation session, worker, step, staging, production, machine, routine, guard", "Legend: x", FENCE, "<!-- diagram:end -->", ""])
check(milestones.home_diagram(HOME) == [], "a Home diagram naming each part of the loop passes")
check(says(milestones.home_diagram("# r"), "no system diagram"), "negative control: a Home with no diagram is reported")
check(says(milestones.home_diagram(HOME.replace("staging, ", "")), "staging"), "negative control: a Home diagram without staging is reported, naming it")
check(pf.unblocked(HOME).strip() == "# r", "Home's DOC-4 table check does not read the diagram block")

FEATURE = NL.join(["# X", "", "- Say `/workflow-docs check` on a schedule `17 */4 * * *`.", "", "## Tests", "", "`/workflow-nope`"])
check(milestones.unlisted(FEATURE, "nothing") == ["/workflow-docs", "17 */4 * * *"], "negative control: a skill and a schedule the feature page names and the How-to-use page lacks are reported")
check(milestones.unlisted(FEATURE, "/workflow-docs and 17 */4 * * *") == [], "a skill and a schedule the How-to-use page lists pass; the Tests section is not read")

with tempfile.TemporaryDirectory() as root:
    os.makedirs(os.path.join(root, "docs", "wiki"))
    os.makedirs(os.path.join(root, "skills", "workflow-x", "scripts"))
    os.makedirs(os.path.join(root, "skills", "workflow-x", "references"))
    write = lambda rel, text: open(os.path.join(root, *rel.split("/")), "w", encoding="utf-8", newline="").write(text)
    write("docs/wiki/Home.md", HOME)
    write("docs/wiki/Tests.md", "https://example.org/generated")
    write("skills/workflow-x/SKILL.md", "Fine.")
    write("skills/workflow-x/references/commands.md", "See https://example.org/x .")
    found = milestones.alone(root, "docs/wiki", REPO)
    check([p for _, p, _ in found] == ["skills/workflow-x/references/commands.md"], "alone reads wiki pages and skill docs, never the Tests page: " + repr(found))
sys.exit(1 if failed else 0)
