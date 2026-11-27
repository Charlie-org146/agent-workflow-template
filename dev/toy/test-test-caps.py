#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/role.py skills/workflow-delivery/scripts/role_gate.py skills/workflow-setup/scripts/settings.py
"""Proves the test cap (#4511, owner o51; principle 5 retired the row count, o988): a goal that adds rows net while the full
suite is over max_suite_seconds is refused at qa with the seconds; one that adds none net (+1/-1, merges, only consolidates)
always passes, and so does one when the suite is under its cap or unmeasured; the cap is the base branch's, so a goal can't
raise its own."""
import json
import os
import subprocess
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for skill in ("workflow-delivery", "workflow-setup"):
    sys.path.insert(0, os.path.join(here, "skills", skill, "scripts"))
import role  # noqa: E402
import settings  # noqa: E402

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


def table(n, start=0):
    return "# id\tlevel\tcommand\n" + "".join("r%d\tland\ttrue\n" % i for i in range(start, start + n))


def config(secs=100, **extra):
    return json.dumps(dict({"base": "main", "max_suite_seconds": secs}, **extra))


def goal(base_rows, work_table, work_config=None, base_config=None, record_seconds=500):
    """role.over_caps() in a repo whose origin/main holds base_rows rows and whose work tree holds work_table; the recorded full
    suite took record_seconds (0: no record) and the base's cap is 100 s unless base_config says otherwise."""
    with tempfile.TemporaryDirectory() as repo:
        git(repo, "init", "-q", "-b", "main")
        put(repo, ".loop/config.json", base_config or config())
        put(repo, ".loop/regression.tsv", table(base_rows))
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "base")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        put(repo, ".loop/regression.tsv", work_table)
        if work_config:
            put(repo, ".loop/config.json", work_config)
        if record_seconds:
            put(repo, ".git/loop/tests/main.json", json.dumps({"at": "x", "total_seconds": record_seconds, "rows": {}}))
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "goal")
        was = os.getcwd()
        os.chdir(repo)
        try:
            return role.over_caps()
        finally:
            os.chdir(was)


# the suite (500 s) is over its cap (100 s) unless a case says otherwise
slow = goal(3, table(4))
check("a goal that adds rows while the suite is over max_suite_seconds is refused with the seconds",
      slow is not None and slow[2] == "TEST_CAPS" and "the full suite takes 500 s, max_suite_seconds is 100" in slow[0]
      and "adds 1 rows net (+1, -0)" in slow[0])
check("a goal that adds rows while the suite is under its cap passes", goal(3, table(4), base_config=config(1000)) is None)
check("a goal that removes as many rows as it adds passes", goal(3, table(3, 1)) is None)
merged = table(4, 2) + "rX\tland\ttrue\n"  # drops r0 and r1, adds rX: net -1, while the suite is over its cap
check("a goal that merges two rows into one, while over the cap, passes", goal(6, merged) is None)
check("a goal that only consolidates passes even though the repo is over the cap", goal(5, table(4)) is None)
check("a goal that adds rows with no measured suite passes", goal(3, table(4), record_seconds=0) is None)
check("a goal can't raise its own cap", goal(3, table(4), work_config=config(100000)) is not None)
check("the owner raising the cap on the base lets the goal pass", goal(3, table(4), base_config=config(600)) is None)

text = open(os.path.join(here, "skills", "workflow-setup", "scripts", "settings.py"), encoding="utf-8").read()
check("max_suite_seconds is a setting with a default", '"max_suite_seconds", REPO' in text)
check("the retired max_regression_rows key is ignored: a goal adding a row to a repo at that old cap passes",
      goal(3, table(4), base_config=config(100000, max_regression_rows=3)) is None and '"max_regression_rows", REPO' not in text)
check("the refusal names the one cap and the fix",
      slow is not None and slow[0].startswith("over the test cap (the full suite takes") and "owner raises max_suite_seconds" in slow[1])
sys.exit(1 if fails else 0)
