#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/release.py
"""release.py cut's criteria check: a known row is not a failure, a row skipped on this platform (exit 77) is not a
failure, and a row already recorded PASS is not run again; each has a control that still fails."""
import json
import os
import subprocess
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


def trouble(command, known="", passed=None):
    with tempfile.TemporaryDirectory() as top:
        os.makedirs(os.path.join(top, ".loop"))
        os.makedirs(os.path.join(top, "docs", "wiki"))
        files = {".loop/docs.tsv": "Page\tx.py\n", "docs/wiki/Page.md": "# Page\n\n## Requirements\n\n- ABC-1: a thing\n",
                 ".loop/regression.tsv": "row1\tland\t%s\tABC-1\n" % command, ".loop/regression-known.tsv": known}
        for name, text in files.items():
            with open(os.path.join(top, name), "w", newline="\n") as handle:
                handle.write(text)
        if passed is not None:  # a PASS counts only from a lane record (git common dir loop/tests) on the current commit
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.test"]
            subprocess.run(git + ["init", "-q"], cwd=top, check=True)
            subprocess.run(git + ["add", "-A"], cwd=top, check=True)
            subprocess.run(git + ["commit", "-q", "-m", "x"], cwd=top, check=True)
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=top, check=True, capture_output=True, text=True).stdout.strip()
            os.makedirs(os.path.join(top, ".git", "loop", "tests"))
            with open(os.path.join(top, ".git", "loop", "tests", "lane.json"), "w") as handle:
                json.dump({"rows": {"row1": {"status": passed, "commit": head}}}, handle)
        unmet, _left = release.criteria_trouble(top, {})  # (unmet, left): only unmet requirements are a trouble
        return unmet


check(trouble("exit 1") != [], "control: a failing row is a trouble")
check(trouble("exit 1", known="row1\tfails on this PC\n") == [], "a row in regression-known.tsv is not a failure")
check(trouble('echo skip > "$TOY_SKIP_FILE"; exit 1') == [], "a row whose toy wrote TOY_SKIP_FILE is skipped, not a failure (a pipe hides exit 77)")
check(trouble("exit 77") == [], "a row that exits 77 is skipped, not a failure")
check(trouble("exit 1", passed="PASS") == [], "a row already recorded PASS on this commit is not run again")
check(trouble("exit 1", passed="FAIL") != [], "control: a row recorded FAIL still runs and fails")
sys.exit(1 if failed else 0)
