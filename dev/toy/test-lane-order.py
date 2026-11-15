#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/tiers.py skills/workflow-regression/scripts/lanes.py
# reads: skills/workflow-regression/scripts/narrow.py skills/workflow-regression/scripts/slots.py
"""lane-order (#531): after a base merge, a goal's own new and changed rows run before the rows that only reach a changed
file, so the 15-minute budget never leaves the goal's new rows to the scheduled suite.

Checks the order tiers.plan sorts by: new row, then failure rerun, then reaches, then the root runners and the picks."""
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
sys.dont_write_bytecode = True
import tiers  # noqa: E402

why = {"r1": "reaches .loop/goals/x.md", "r2": "root runner", "r3": "new row", "r4": "reaches a.py", "r5": "failure rerun",
       "r6": "names an unmapped path", "r7": "new row", "r8": "skipped last time", "r9": "root runner (unmapped path)"}
todo = sorted(why, key=lambda rid: tiers.rank(why[rid]))  # plan() sorts by the same key; the sort is stable
kinds = [why[rid].split()[0] for rid in todo]
ok = (todo[:2] == ["r3", "r7"] and set(todo[2:4]) == {"r5", "r8"} and set(todo[4:6]) == {"r1", "r4"}
      and set(todo[6:]) == {"r2", "r6", "r9"} and todo.index("r1") < todo.index("r4"))
print(("PASS: " if ok else "FAIL: ") + "new rows first, then reruns, then reach rows, then the root runners and picks (%s)" % ", ".join(kinds))
sys.exit(0 if ok else 1)
