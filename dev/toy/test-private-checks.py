#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/tests.py skills/workflow-delivery/scripts/private.py skills/workflow-delivery/scripts/fit.py
"""Proves a private repo's required checks (#4537): the pr step runs and posts a status for each required check whose job is plain
`run:` steps, names each one it can't satisfy (a third-party action) and stops before the PR opens, never posts a failing job
green, and a repo requiring only the regression check passes as before. Fixture repos only; gh is stubbed."""
import contextlib
import io
import os
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(here, "skills", "workflow-delivery", "scripts"))
sys.path.insert(0, os.path.join(here, "skills", "workflow-regression", "scripts"))
import private  # noqa: E402
import tests  # noqa: E402

fails = []

WORKFLOW = """name: ci
on: [push]
jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 skills/workflow-regression/scripts/regression.py run land
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo plain > made.txt
          test -f made.txt
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: some-org/third-party-action@v1
      - run: scan.sh
  badcheck:
    runs-on: ubuntu-latest
    steps:
      - run: exit 3
"""


def check(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fails.append(name)


def refusal(top, required):
    """private.cannot() for a private fixture repo whose base branch requires the named checks."""
    was = private.repo_is_private, private.required_checks
    private.repo_is_private, private.required_checks = (lambda top: True), (lambda top, base: (required, []))
    try:
        return private.cannot(top, "main")
    finally:
        private.repo_is_private, private.required_checks = was


with tempfile.TemporaryDirectory() as top:
    os.makedirs(os.path.join(top, ".github", "workflows"))
    with open(os.path.join(top, ".github", "workflows", "ci.yml"), "w", newline="\n") as handle:
        handle.write(WORKFLOW)
    reg, local, no = tests.classify(top, ["regression", "checks", "scan", "badcheck"])
    check("a regression-only job, plain script jobs and a third-party-action job are told apart",
          reg == ["regression"] and sorted(local) == ["badcheck", "checks"] and no == ["scan"])
    check("a block `run: |` job keeps all its lines", local["checks"] == ["echo plain > made.txt\ntest -f made.txt"])
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        posted = tests.lane_checks(top, ["regression", "checks"])
    check("the pr step runs a plain job's steps here and posts its status with the regression one",
          posted == ["regression", "checks"] and os.path.exists(os.path.join(top, "made.txt")) and "BLOCKS" not in out.getvalue())
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        posted = tests.lane_checks(top, ["badcheck", "scan"])
    check("a plain job whose step fails is never posted green, and the third-party one is named",
          posted == [] and "BLOCKS: badcheck fails run here" in out.getvalue() and "BLOCKS: scan cannot be run here" in out.getvalue())
    stop = refusal(top, ["regression", "checks", "scan"])
    check("the pr step names the check it cannot satisfy and stops before the PR opens",
          stop is not None and stop[2] == "PR_CHECKS" and "scan" in stop[0] and "checks," not in stop[0])
    check("a repo requiring a regression check and a plain script check is not stopped", refusal(top, ["regression", "checks"]) is None)
    check("negative control: a repo requiring only the regression check passes as before", refusal(top, ["regression"]) is None)
sys.exit(1 if fails else 0)
