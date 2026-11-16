#!/usr/bin/env python3
"""The Documentation page does not call milestone sync left for later while DOC-17 syncs milestones (#4546).

usage: test-doc-nongoal-milestone.py [PAGE]   PAGE defaults to docs/wiki/Documentation.md next to this repo
"""
import os
import re
import sys

page = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "wiki", "Documentation.md")
text = open(page, encoding="utf-8").read().replace("\r\n", "\n")
req = re.search(r"^- DOC-17:.*?(?=^- [A-Z]+-\d+:|^## )", text, re.M | re.S)
non = re.search(r"^## Non-goals\n(.*?)^## ", text, re.M | re.S)
if not req or not non:
    print("FAIL: the page has no DOC-17 requirement or no Non-goals section")
    sys.exit(1)
if "milestone" not in req.group(0).lower():
    print("PASS: DOC-17 does not sync milestones, so no line can contradict it")
    sys.exit(0)
bad = [l for l in non.group(1).splitlines() if re.search(r"\bsyncing\b[^.]*\bmilestones?\b", l, re.I) and "later" in l.lower() and "DOC-17" not in l]
if bad:
    print("FAIL: DOC-17 syncs milestones but a Non-goals line leaves them for later: %s" % bad[0][:120])
    sys.exit(1)
print("PASS: DOC-17 syncs milestones and no Non-goals line leaves milestone sync for later")
