#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/deployments.py skills/workflow-docs/scripts/prd.py
"""DOC-18: docs check reports a feature with no How-to-use page, one off the skeleton and an unlinked one; a How-to-use page
with no docs.tsv row is mapped to its feature (#4542); one whose feature has no page is an orphan."""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-docs", "scripts"))
import deployments  # noqa: E402
import docs  # noqa: E402
import prd  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


GOOD = """<!-- workflow-docs -->
# How to use A

## What it's for

It does a thing for its users, in one plain sentence here.

## How to reach or run it

Say "run it" to the agent.

## Links

- PRD page: [A](A)
"""
PAGE = "<!-- workflow-docs -->\n# A\n\nHow to use: [How-to-use-A](How-to-use-A)\n\n## Problem\n- I want a thing that works for me every day without fuss or delay.\n"


def put(root, name, text):
    with open(os.path.join(root, "docs", "wiki", name + ".md"), "w") as handle:
        handle.write(text)


with tempfile.TemporaryDirectory() as tmp:
    root = os.path.join(tmp, "repo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    os.makedirs(os.path.join(root, ".loop"))
    os.makedirs(os.path.join(root, "docs", "wiki"))
    with open(os.path.join(root, ".loop", "config.json"), "w") as handle:
        handle.write("{}")
    with open(os.path.join(root, ".loop", "docs.tsv"), "w") as handle:
        handle.write("A\tsrc\n")
    folder = docs.wiki_dir(root)
    put(root, "A", PAGE)
    rows = docs.read_map(root)
    check([x[0] for x in deployments.howto(root, folder, ["A"])] == ["HOWTO"] and "no How-to-use page" in deployments.howto(root, folder, ["A"])[0][2],
          "negative control: a feature page with no How-to-use page is reported")
    put(root, "How-to-use-A", GOOD)
    check(deployments.howto(root, folder, ["A"]) == [], "a feature with a How-to-use page on the skeleton, linked from its page, passes")
    check(deployments.mapped(root, rows, folder).get("How-to-use-A") == ["src"], "a How-to-use page with no docs.tsv row is mapped to its feature's paths")
    check("How-to-use-A" not in rows, "the docs.tsv map itself is not changed by the mapping")
    check(not any(k == "UNMAPPED" and p == "How-to-use-A" for k, p, _ in docs.problems(root, None)), "docs check does not report that page unmapped")
    put(root, "How-to-use-Ghost", GOOD)
    orphan = [d for k, p, d in docs.problems(root, None) if k == "UNMAPPED" and p == "How-to-use-Ghost"]
    check(bool(orphan) and "orphan" in orphan[0], "negative control: a How-to-use page whose feature has no page is an orphan")
    put(root, "How-to-use-A", GOOD.replace("# How to use A", "# Using A"))
    check(any("title" in d for _, _, d in deployments.howto(root, folder, ["A"])), "negative control: a wrong title is reported")
    put(root, "How-to-use-A", GOOD.replace("## Links", "## Misc"))
    check(any("sections" in d for _, _, d in deployments.howto(root, folder, ["A"])), "negative control: a section off the skeleton is reported")
    put(root, "How-to-use-A", GOOD.replace("## How to reach or run it", "## Links2").replace("## Links2", "## Links") + "\n## What it's for\n")
    check(any("sections" in d for _, _, d in deployments.howto(root, folder, ["A"])), "negative control: sections out of order are reported")
    put(root, "How-to-use-A", GOOD)
    put(root, "A", PAGE.replace("How to use: [How-to-use-A](How-to-use-A)\n\n", ""))
    check(any("doesn't link" in d for _, _, d in deployments.howto(root, folder, ["A"])), "negative control: a feature page that does not link its How-to-use page is reported")
    # case 1 (REVIEW rule): exactly one link line is allowed in the page head
    rule, link = {"milestone": "Milestone", "review": "Review"}, "How to use: [How-to-use-A](How-to-use-A)"
    head = lambda *lines: chr(10).join(["<!-- workflow-docs -->", "# A", ""] + [x for line in lines for x in (line, "")] + ["## Problem"])
    base = ["Milestone: https://x/1", "Review: **Unreviewed**"]
    check(prd.review_of(head(link, *base), rule)[1] is None, "the link line between the title and the Milestone line is allowed")
    check(prd.review_of(head(*base, link), rule)[1] is None, "the link line after the Review line is allowed")
    check(prd.review_of(head(base[0], link, base[1]), rule)[1] is None, "the link line between the Milestone and Review lines is allowed")
    check(prd.review_of(head("Notes: other", *base), rule)[1] is not None, "negative control: a different extra line between the title and Milestone is refused")
    check(prd.review_of(head(*base, "Notes: other"), rule)[1] is not None, "negative control: a different extra line after the Review line is refused")
    check(prd.review_of(head(link, link, *base), rule)[1] is not None, "negative control: a second link line is refused")
    check(prd.review_of(head("How to use: [A](B)", *base), rule)[1] is not None, "negative control: a link line to another page is refused")

    # case 2 (DOC-16): a routine's runbook may sit on the feature's How-to-use page instead of its PRD
    with open(os.path.join(root, ".loop", "routines.tsv"), "w") as handle:
        handle.write("r" + chr(9) + "A" + chr(10))
    put(root, "How-to-use-A", GOOD + chr(10) + "## Runbooks" + chr(10) + chr(10) + "### r" + chr(10) + chr(10) + "- **Runs:** daily" + chr(10))
    book = deployments.howto_book(root, folder, "A", "Runbook")
    check(deployments.owed(root, {"A": book}, "Runbook") == [], "a routine whose runbook is on the How-to-use page is not owed")
    check(any("'### r' runbook" in x[2] for x in deployments.owed(root, {"A": []}, "Runbook")), "negative control: a routine with a runbook on neither page is owed")
    put(root, "How-to-use-A", GOOD)
    check(deployments.howto_book(root, folder, "A", "Runbook") == [], "a How-to-use page with no Runbooks section gives no runbook")
sys.exit(1 if failed else 0)
