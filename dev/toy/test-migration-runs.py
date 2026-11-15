#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/enforce.py skills/workflow-health/scripts/defects.py
# reads: skills/workflow-health/scripts/workflows.py skills/workflow-health/scripts/report.py
"""migration-runs (#3821): migration-check follows the reviewed spec for where the regression runs.

A public repo runs it in Actions (regression_runs actions, with .github/workflows/regression.yml); a private repo runs it on the
Mac (regression_runs mac, and a leftover regression.yml is a gap). Runs the MIG_AUTOMATION rule (enforce.automation_gaps) and
the leftover-workflow check (defects.gaps_files) over a small matrix of settings and files and reads which gaps they report."""
import os
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-health", "scripts"))
sys.dont_write_bytecode = True
import defects  # noqa: E402
import enforce  # noqa: E402

failed = []
BASE = {"regression_cron": "47 */4 * * *", "health_cron": "47 */4 * * *", "automation": []}


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def gaps(fn, repo, cfg, name):
    found = []
    fn(repo, cfg, lambda code, path, why, fix: found.append(path), *([{}] if fn is enforce.automation_gaps else []))
    return [path for path in found if path.endswith(name)]


with tempfile.TemporaryDirectory() as repo:
    os.makedirs(os.path.join(repo, ".loop"))
    os.makedirs(os.path.join(repo, ".github", "workflows"))
    yml = os.path.join(repo, ".github", "workflows", "regression.yml")

    def setting(runs, has_yml):
        if has_yml:
            open(yml, "w").close()
        elif os.path.exists(yml):
            os.remove(yml)
        return dict(BASE, regression_runs=runs)

    cfg = setting("actions", True)
    check(not gaps(enforce.automation_gaps, repo, cfg, "regression_runs"), "a public repo (actions, regression.yml present) is not flagged")
    check(not gaps(defects.gaps_files, repo, cfg, "regression.yml"), "...and its regression.yml is not a leftover")
    cfg = setting("actions", False)
    check(gaps(enforce.automation_gaps, repo, cfg, "regression_runs"), "actions without regression.yml is flagged")
    cfg = setting("mac", False)
    check(not gaps(enforce.automation_gaps, repo, cfg, "regression_runs"), "a private repo (mac) is not flagged")
    cfg = setting("mac", True)
    check(gaps(defects.gaps_files, repo, cfg, "regression.yml"), "a private repo's leftover regression.yml is flagged")
    cfg = setting("elsewhere", True)
    check(gaps(enforce.automation_gaps, repo, cfg, "regression_runs"), "any other setting is flagged")
sys.exit(1 if failed else 0)
