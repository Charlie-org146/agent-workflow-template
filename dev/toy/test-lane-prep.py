#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/lane.py skills/workflow-release/scripts/wiki.py
"""lane-prep (#5728, #5735): a lane started in a fresh clone makes its runs folder; goal.py pr's regen commits the README
the tool itself re-rendered, and leaves a hand-edited README alone so the lane still refuses it.
usage: test-lane-prep.py [runs|readme]   Builds throwaway git repos; no lane starts, no model is called."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
sys.dont_write_bytecode = True
os.environ["LOOP_ROLE"] = "worker"
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
import wiki  # noqa: E402
import lane  # noqa: E402

fails = 0
only = sys.argv[1] if len(sys.argv) > 1 else ""


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def git(repo, *args):
    done = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t"] + list(args), cwd=repo, capture_output=True, text=True)
    return done.stdout.strip()


def fresh_repo():
    repo = tempfile.mkdtemp()
    git(repo, "init", "-q", "-b", "main")
    open(os.path.join(repo, "README.md"), "w").write("# r\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "first")
    return repo


if only in ("", "runs"):
    with tempfile.TemporaryDirectory() as top:
        runs = os.path.join(top, "loop", "runs")
        saved = lane.prep
        lane.prep = lambda top_, cfg, log: (None, "STOP: prep refused on purpose")  # no lane may start: only the folder is judged
        os.chdir(fresh_repo())
        try:
            status, line, _ = lane.lane(runs, "g", "qa", lane.flow_spec(), {}, 0)
        finally:
            lane.prep = saved
        check("a lane start in a clone with no runs folder makes the folder and does not crash", os.path.isdir(runs) and status == "fail")
        absent = os.path.join(top, "never", "runs")
        check("negative control: lane_status on an absent runs folder says no lane and makes nothing", lane.lane_status(absent, "g", "qa")[0] != "pass" and not os.path.exists(absent))

if only in ("", "readme"):
    import argparse

    def prepare(repo, write, stale=None, hook=False, page=False):
        """wiki.py prepare --commit in a throwaway repo; pending() stands in for the audit and writes README like the render does."""
        os.chdir(repo)
        if hook:
            open(os.path.join(repo, ".git", "hooks", "pre-commit"), "w").write("#!/bin/sh\nexit 1\n")
            os.chmod(os.path.join(repo, ".git", "hooks", "pre-commit"), 0o755)

        def fake(top, cfg, fix=False):
            write and open(os.path.join(repo, "README.md"), "a").write(write)
            page and open(os.path.join(repo, "docs", "wiki", "P.md"), "a").write("rendered\n")
            return stale or []
        wiki.top_of, wiki.read_config, wiki.pending = (lambda: repo), (lambda top: {}), fake
        try:
            return wiki.cmd_prepare(argparse.Namespace(slug="slug", commit=True))
        except SystemExit:
            return "exit"

    def last(repo):
        return git(repo, "log", "-1", "--format=%s"), git(repo, "log", "-1", "--name-only", "--format=")

    repo = fresh_repo()
    os.makedirs(os.path.join(repo, "docs", "wiki"))
    open(os.path.join(repo, "docs", "wiki", "P.md"), "w").write("p\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "wiki")
    before = git(repo, "rev-parse", "HEAD")
    prepare(repo, "\nConfidence 99%\n")
    check("a README only the render changed is committed, and the tree is clean", git(repo, "rev-parse", "HEAD") != before and git(repo, "status", "--porcelain") == "")
    repo = fresh_repo()
    os.makedirs(os.path.join(repo, "docs", "wiki"))
    open(os.path.join(repo, "docs", "wiki", "P.md"), "w").write("p\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "wiki")
    prepare(repo, "\nConfidence 99%\n", page=True)
    subject, names = last(repo)
    check("the wiki page and README land in one commit named for the wiki update", subject == "Wiki: update pages for slug" and set(names.split()) == {"README.md", "docs/wiki/P.md"})
    repo = fresh_repo()
    before = git(repo, "rev-parse", "HEAD")
    prepare(repo, "")
    check("a README the render did not change makes no commit", git(repo, "rev-parse", "HEAD") == before)
    repo = fresh_repo()
    open(os.path.join(repo, "README.md"), "a").write("hand edit\n")
    before = git(repo, "rev-parse", "HEAD")
    prepare(repo, "\nConfidence 99%\n")
    check("negative control: a README already hand-edited is not committed, so the lane still refuses it", git(repo, "rev-parse", "HEAD") == before and git(repo, "status", "--porcelain").startswith("M README.md"))
    repo = fresh_repo()
    before = git(repo, "rev-parse", "HEAD")
    prepare(repo, "\nConfidence 99%\n", stale=["REWRITE P: still stale"])
    check("negative control: when a page is still stale README is not committed alone", git(repo, "rev-parse", "HEAD") == before)
    repo = fresh_repo()
    before = git(repo, "rev-parse", "HEAD")
    prepare(repo, "\nConfidence 99%\n", hook=True)
    check("a refused commit leaves README and the wiki together uncommitted, never README alone", git(repo, "rev-parse", "HEAD") == before)

print("ALL PASS" if not fails else "%d FAILED" % fails)
sys.exit(1 if fails else 0)
