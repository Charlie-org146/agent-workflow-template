#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/release.py
"""release.py cut's criteria check: a known row is not a failure, a row skipped on this platform (exit 77) is not a
failure, and a row already recorded PASS is not run again; each has a control that still fails."""
import os
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-release", "scripts"))
import release  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def trouble(command, known="", runs=""):
    with tempfile.TemporaryDirectory() as top:
        os.makedirs(os.path.join(top, ".loop"))
        os.makedirs(os.path.join(top, "docs", "wiki"))
        files = {".loop/docs.tsv": "Page\tx.py\n", "docs/wiki/Page.md": "# Page\n\n## Requirements\n\n- ABC-1: a thing\n",
                 ".loop/regression.tsv": "row1\tland\t%s\tABC-1\n" % command, ".loop/regression-known.tsv": known,
                 ".loop/regression-runs.tsv": runs}
        for name, text in files.items():
            with open(os.path.join(top, name), "w", newline="\n") as handle:
                handle.write(text)
        return release.criteria_trouble(top, {})


check(trouble("exit 1") != [], "control: a failing row is a trouble")
check(trouble("exit 1", known="row1\tfails on this PC\n") == [], "a row in regression-known.tsv is not a failure")
check(trouble("exit 77") == [], "a row that exits 77 is skipped, not a failure")
check(trouble("exit 1", runs="row1\tPASS\t2026-11-15\t\t\n") == [], "a row already recorded PASS is not run again")
check(trouble("exit 1", runs="row1\tFAIL\t2026-11-15\t\t\n") != [], "control: a row recorded FAIL still runs and fails")
sys.exit(1 if failed else 0)
