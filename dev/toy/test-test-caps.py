#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/role.py skills/workflow-health/scripts/lean.py skills/workflow-setup/scripts/settings.py
"""Proves the test caps (#4511, owner o51): a goal that adds rows while the repo is over max_regression_rows or max_suite_seconds
is refused at qa with the numbers; one that removes or merges as many as it adds, or only consolidates, always passes; the
caps are the base branch's, so a goal can't raise its own; and health warns at 90% and fails over each cap."""
import json
import os
import subprocess
import sys
import tempfile

here = os.environ.get("TOY_HERE") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for skill in ("workflow-delivery", "workflow-health", "workflow-setup"):
    sys.path.insert(0, os.path.join(here, "skills", skill, "scripts"))
import role  # noqa: E402
import lean  # noqa: E402
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


def config(rows=3, secs=0):
    return json.dumps({"base": "main", "max_regression_rows": rows, "max_suite_seconds": secs or 100000})


def goal(base_rows, work_table, work_config=None, base_config=None, record_seconds=0):
    """role.over_caps() in a repo whose origin/main holds base_rows rows and whose work tree holds work_table."""
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


refused = goal(3, table(4))
check("a goal that adds a row to a repo at its cap is refused with the numbers",
      refused is not None and refused[2] == "TEST_CAPS" and "4 rows, max_regression_rows is 3" in refused[0] and "adds 1 rows net" in refused[0])
check("a goal that removes as many rows as it adds passes", goal(3, table(3, 1)) is None)
merged = table(4, 2) + "rX	land	true
"  # drops r0 and r1, adds rX: net -1, still over the cap
check("a goal that merges two rows into one, while over the cap, passes", goal(6, merged) is None)
check("a goal that only consolidates passes even though the repo is over the cap", goal(5, table(4)) is None)
check("a goal that stays at or under the cap passes", goal(2, table(3)) is None)
check("a goal that goes over the cap from under it is refused", goal(2, table(4)) is not None)
check("a goal can't raise its own cap", goal(3, table(4), work_config=config(rows=100)) is not None)
check("the owner raising the cap on the base lets the goal pass", goal(3, table(4), base_config=config(rows=10)) is None)
slow = goal(3, table(4), base_config=config(rows=100, secs=100), record_seconds=500)
check("a goal that adds rows while the suite is over max_suite_seconds is refused with the seconds",
      slow is not None and "the full suite takes 500 s, max_suite_seconds is 100" in slow[0])
check("a goal that adds rows while the suite is under its cap passes", goal(3, table(4), base_config=config(rows=100, secs=1000), record_seconds=500) is None)

text = open(os.path.join(here, "skills", "workflow-setup", "scripts", "settings.py"), encoding="utf-8").read()
check("both caps are settings with defaults", all('"%s", REPO' % key in text for key in ("max_regression_rows", "max_suite_seconds")))

with tempfile.TemporaryDirectory() as repo:
    put(repo, ".loop/regression.tsv", table(10))
    put(repo, ".loop/config.json", json.dumps({"base": "main", "max_regression_rows": 20}))
    states = lambda rows: [r["state"] for r in rows]  # noqa: E731
    check("health passes a table under 90% of its cap", states(lean.rows_cap(repo)) == ["PASS"])
    put(repo, ".loop/config.json", json.dumps({"base": "main", "max_regression_rows": 11}))
    check("health warns at 90% of the cap", states(lean.rows_cap(repo)) == ["WARN"])
    put(repo, ".loop/config.json", json.dumps({"base": "main", "max_regression_rows": 9}))
    check("health fails over the cap", states(lean.rows_cap(repo)) == ["FAIL"])
    put(repo, ".loop/config.json", json.dumps({"base": "main", "max_regression_rows": 0}))
    check("a cap of 0 turns the rule off", lean.rows_cap(repo) == [])
sys.exit(1 if fails else 0)
