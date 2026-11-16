#!/usr/bin/env python3
# reads: skills/workflow-release/scripts/release.py skills/workflow-release/scripts/review.py
"""Proves the cut's row proof (#4508): release.py cut reruns a row whose only PASS is on an older commit, skips a row with a PASS on the
current commit, and prints the rows it did not run before its stop as LEFT with their count, in the cut's output and the release
notes; with nothing left it prints no LEFT section."""
import json
import os
import subprocess
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(here, "skills", "workflow-release", "scripts"))
import release  # noqa: E402
import review  # noqa: E402

fails = []


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-c", "commit.gpgsign=false"] + list(args), cwd=repo, env=env, capture_output=True, text=True,
                          check=True).stdout.strip()


def put(repo, rel, text):
    os.makedirs(os.path.dirname(os.path.join(repo, rel)), exist_ok=True)
    with open(os.path.join(repo, rel), "w", newline="\n") as handle:
        handle.write(text)


def cut(seconds=None, current=(), older=()):
    """(rows the cut ran, rows it left) for a repo with requirements AA-1..AA-3 on one page, each with a row r1..r3: rows in
    `current` have a PASS on HEAD in a lane record, rows in `older` only a PASS on an older commit (and in regression-runs.tsv)."""
    with tempfile.TemporaryDirectory() as repo:
        git(repo, "init", "-q", "-b", "main")
        put(repo, "docs/wiki/Page.md", "# Page\n\n## Requirements\n\n- AA-1: one\n- AA-2: two\n- AA-3: three\n\n## Non-goals\n")
        put(repo, ".loop/docs.tsv", "Page\tx\n")
        put(repo, ".loop/regression.tsv", "# id\tlevel\tcommand\tgoal\n" + "".join("r%d\tland\ttrue\tAA-%d\n" % (n, n) for n in (1, 2, 3)))
        put(repo, ".loop/regression-runs.tsv", "# id\tstatus\tdate\trun\tflaky\n" + "".join("r%d\tPASS\t2026-11-15\t\t\n" % n for n in (1, 2, 3)))
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "old")
        old = git(repo, "rev-parse", "HEAD")
        put(repo, "x.txt", "change\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "now")
        head = git(repo, "rev-parse", "HEAD")
        rows = {"r%d" % n: {"status": "PASS", "commit": head} for n in current}
        rows.update({"r%d" % n: {"status": "PASS", "commit": old} for n in older})
        put(repo, ".git/loop/tests/main.json", json.dumps({"at": "x", "rows": rows}))
        ran = []
        was = os.environ.get("LOOP_CUT_SECONDS")
        if seconds is not None:
            os.environ["LOOP_CUT_SECONDS"] = str(seconds)
        try:
            unmet, left = review.criteria(repo, {}, release.doc_rows, lambda command, top: ran.append(command) or False)
        finally:
            os.environ.pop("LOOP_CUT_SECONDS", None)
            if was is not None:
                os.environ["LOOP_CUT_SECONDS"] = was
        return ran, unmet, left


ran, unmet, left = cut(current=(1,), older=(2,))
check("a row with a PASS on the current commit is not rerun, and one whose only PASS is on an older commit is", len(ran) == 2 and unmet == [] and left == [])
ran, unmet, left = cut(current=(1, 2, 3))
check("when every row has a PASS on the current commit nothing runs and nothing is left", ran == [] and left == [])
ran, unmet, left = cut(seconds=0, current=(1,), older=(2,))
check("a forced stop runs nothing and lists the unrun rows as LEFT", ran == [] and left == ["r2", "r3"])
text = review.left_text(left)
check("the LEFT section names the count and the rows", "LEFT 2 rows were not run" in text and "r2, r3" in text and "## LEFT" in text)
ran, unmet, left = cut()
check("negative control: with time to run every row, nothing is LEFT and the notes carry no LEFT section", left == [] and review.left_text(left) == "" and len(ran) == 3)
source = open(os.path.join(here, "skills", "workflow-release", "scripts", "release.py"), encoding="utf-8").read()
check("the cut prints the LEFT section and writes it into the release notes", source.count("review.left_text(left)") == 2)
sys.exit(1 if fails else 0)
