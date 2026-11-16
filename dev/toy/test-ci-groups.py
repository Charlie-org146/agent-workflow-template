#!/usr/bin/env python3
# windows: ok
# reads: .loop/goals/ci-fail-causes.groups.md
"""ci-fail-causes (#4516): every failing row of the full run is in exactly one cause group, and each group names its outcome
(an issue link, a fix, or known with a reason). Controls: a row in two groups and a group with no outcome are caught."""
import os
import re
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
failed = []


def check(ok, said):
    print(("PASS: " if ok else "FAIL: ") + said)
    if not ok:
        failed.append(said)


def problems(text):
    seen, out = {}, []
    for part in re.split(r"(?m)^## ", text)[1:]:
        head = part.split("\n", 1)[0]
        if not re.search(r"Outcome: (filed, https://\S+|fixed\b|known: \S)", part):
            out.append("no outcome: " + head)
        rows = re.findall(r"`([^`]+)`", part.split("Rows: ", 1)[-1]) if "Rows: " in part else []
        for row in rows:
            if row in seen:
                out.append("%s in %s and %s" % (row, seen[row], head))
            seen[row] = head
    return out


text = open(os.path.join(root, ".loop", "goals", "ci-fail-causes.groups.md"), encoding="utf-8").read()
check(problems(text) == [], "every group has an outcome and no row is in two groups")
check(problems("## G1\n\nOutcome: filed, https://x/1\n\nRows: `a`, `b`\n\n## G2\n\nOutcome: filed, https://x/2\n\nRows: `b`\n") != [], "control: a row in two groups is caught")
check(problems("## G1\n\nShared error: x\n\nRows: `a`\n") != [], "control: a group with no outcome is caught")
sys.exit(1 if failed else 0)
