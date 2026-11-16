#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/role.py
"""pr-body-cap (#4531): the PR body's "Rows and why they ran" list is capped, so a change that selects every row can open its PR.

Builds a fake pr lane log in a temp git repo and calls role.lane_part: 1,000 selected rows are cut to a short list ending in the
count of the rest; a few very long rows are cut by characters; 5 rows are all listed with no "more" line. gh refuses a body over
65,536 characters, so every capped part is checked far under it."""
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
sys.dont_write_bytecode = True

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def part(tmp, rows):
    """lane_part's text for a pr lane log holding these SELECTED rows."""
    runs = os.path.join(tmp, ".git", "loop", "runs")
    os.makedirs(runs, exist_ok=True)
    with open(os.path.join(runs, "g.pr-lane.last"), "w") as handle:
        json.dump({"line": "LANE pr AFFECTED %d/%d in 5s" % (len(rows), len(rows))}, handle)
    with open(os.path.join(runs, "g.pr-lane.txt"), "w") as handle:
        handle.write("\n".join("SELECTED row%d: %s" % (n, text) for n, text in enumerate(rows)) + "\n")
    import role
    return role.lane_part("g")


with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(["git", "init", "-q", tmp], check=True)
    here = os.getcwd()
    os.chdir(tmp)
    try:
        big = part(tmp, ["changed a file the row reads"] * 1000)
        shown = big.count("SELECTED row")
        check(0 < shown < 1000, "1,000 selected rows list only %d" % shown)
        check("... %d more" % (1000 - shown) in big, "the list ends with the exact count of the rest (%d more)" % (1000 - shown))
        check(len(big) < 65536 // 2, "the part is far under gh's 65,536-character limit (%d)" % len(big))
        wide = part(tmp, ["x" * 600] * 200)
        shown = wide.count("SELECTED row")
        check(0 < shown < 200 and "... %d more" % (200 - shown) in wide, "200 very long rows are cut by characters too (%d listed)" % shown)
        check(len(wide) < 65536 // 2, "the long-row part is far under the limit (%d)" % len(wide))
        small = part(tmp, ["a", "b", "c", "d", "e"])
        check(small.count("SELECTED row") == 5 and "more" not in small.replace("SELECTED", ""), "5 selected rows are all listed, with no more line")
    finally:
        os.chdir(here)

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
