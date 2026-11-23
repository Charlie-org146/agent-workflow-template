#!/usr/bin/env python3
# reads: .loop/regression.tsv
"""full-auto-no-new-file (full-auto-all:4, TD1225): the full-auto-all goal's own merge adds no file under skills/ or listing.json.

The row reads that one merge on origin/main (found by its message, compared with its first parent), the way the tasks and
null-report rows do (o863, TD1194). Later goals' new skills files are bounded by GRD-21's package cap, which stays in force.
Negative controls run in this toy: a fixture of that merge adding a skills file, or listing.json, fails; one adding only a
document passes."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PR = r"^Merge pull request #[0-9]* from .*/loop/full-auto-all$"
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git_in(repo, *args):
    return subprocess.run(["git", "-c", "user.email=t@example.test", "-c", "user.name=t", *args], cwd=repo, capture_output=True, text=True)


def added(repo):
    """(merge found, files the merge added under skills/ or listing.json): the first-parent merge of the goal's pull request on origin/main."""
    merge = git_in(repo, "log", "origin/main", "--first-parent", "--merges", "--format=%H", "-1", "--grep", PR).stdout.strip()
    if not merge:
        return "", []
    out = git_in(repo, "diff", "--diff-filter=A", "--name-only", merge + "^1", merge, "--", "skills", "listing.json").stdout
    return merge, [x for x in out.splitlines() if x.strip()]


def fixture(files):
    """A repo whose origin/main has the goal's pull request merged, adding files."""
    repo = tempfile.mkdtemp(prefix="full-auto-files-")
    git_in(repo, "init", "-q", "-b", "main", ".")
    git_in(repo, "commit", "-q", "--allow-empty", "-m", "base")
    git_in(repo, "checkout", "-q", "-b", "loop/full-auto-all")
    for name in files:
        os.makedirs(os.path.dirname(os.path.join(repo, name)) or repo, exist_ok=True)
        open(os.path.join(repo, name), "w").write("x\n")
    git_in(repo, "add", "-A")
    git_in(repo, "commit", "-q", "--allow-empty", "-m", "goal")
    git_in(repo, "checkout", "-q", "main")
    git_in(repo, "merge", "-q", "--no-ff", "-m", "Merge pull request #1 from o/loop/full-auto-all", "loop/full-auto-all")
    git_in(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


have = git_in(root, "rev-parse", "--verify", "-q", "origin/main").returncode == 0
if not have:
    check(False, "origin/main is missing here, so the goal's merge cannot be read. Fix: fetch it, then run this toy again")
else:
    merge, files = added(root)
    check(bool(merge) and files == [], "the full-auto-all merge is found on origin/main and adds no file under skills/ or listing.json: %s" % files)
check(added(fixture(["docs/a.md"]))[1] == [], "control: a fixture of the merge adding only a document reads as clean")
check(added(fixture(["skills/x/scripts/other.py"]))[1] == ["skills/x/scripts/other.py"], "negative control: a fixture of the merge adding a skills file still fails")
check(added(fixture(["listing.json"]))[1] == ["listing.json"], "negative control: a fixture of the merge adding listing.json still fails")
print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
