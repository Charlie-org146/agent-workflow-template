#!/usr/bin/env python3
"""recordonly.py: may CI skip the affected rows on this head? Run by the regression-pr workflow (DEL-1).

Prints `RECORD-ONLY <parent>` and exits 0 only when HEAD is goal.py pr's one bookkeeping commit on a parent whose
`affected` check already passed: one parent, the record commit's subject, and every change either a line of
.loop/regression-issues.tsv or a result row of a wiki page (a `| ` table row naming a Tests anchor). Anything else prints
`FULL <why>` and exits 1, so the rows run. A parent whose check is still queued or running is waited for (WAIT seconds)."""
import json
import os
import subprocess
import sys
import time

SUBJECT = "pr: record issue states and the lane's results"
ISSUES = ".loop/regression-issues.tsv"
JOB = "affected"
WAIT = 25 * 60


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True).stdout


def result_row(line):
    return line[1:].startswith("| ") and ("Tests#t-" in line or '<a id="t-' in line)


def why_full(head="HEAD"):
    """'' when the commit is record-only, else the reason it is not."""
    parents = git("rev-list", "--parents", "-n1", head).split()[1:]
    if len(parents) != 1:
        return "%d parents" % len(parents)
    if git("log", "-1", "--format=%s", head).strip() != SUBJECT:
        return "not the record commit"
    for path in git("diff", "--name-only", parents[0], head).split("\n"):
        if not path or path == ISSUES:
            continue
        if not (path.startswith("docs/wiki/") and path.endswith(".md")):
            return "%s is not a record file" % path
        for line in git("diff", "-U0", "--no-color", parents[0], head, "--", path).split("\n"):
            if line and line[0] in "+-" and line[:3] not in ("+++", "---") and not result_row(line):
                return "%s changes more than result rows" % path
    return ""


def runs_of(sha):
    seen = subprocess.run(["gh", "api", "repos/%s/commits/%s/check-runs" % (os.environ.get("GITHUB_REPOSITORY", ""), sha)],
                          capture_output=True, text=True)
    try:
        return [r for r in json.loads(seen.stdout).get("check_runs", []) if r.get("name") == JOB]
    except ValueError:
        return []


def verdict(runs):
    """pass, wait or bad for the parent's `affected` runs."""
    if any(r.get("conclusion") == "success" for r in runs):
        return "pass"
    return "wait" if any(r.get("status") != "completed" for r in runs) else "bad"


def decide(head="HEAD", wait=WAIT, nap=30):
    why = why_full(head)
    if why:
        return 1, "FULL " + why
    parent = git("rev-parse", head + "^").strip()
    end = time.time() + wait
    while True:
        seen = verdict(runs_of(parent))
        if seen == "pass":
            return 0, "RECORD-ONLY " + parent
        if seen == "bad" or time.time() >= end:
            return 1, "FULL the parent's %s check %s" % (JOB, "did not pass" if seen == "bad" else "is still running")
        time.sleep(nap)


if __name__ == "__main__":
    if sys.argv[1:2] in (["-h"], ["--help"]):
        sys.exit(print(__doc__))
    code, line = decide(*sys.argv[1:2])
    print(line)
    sys.exit(code)
