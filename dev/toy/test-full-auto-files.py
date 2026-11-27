#!/usr/bin/env python3
# reads: .loop/regression.tsv dev/toy/hist.py skills/workflow-delivery/scripts/dlf.py skills/workflow-delivery/scripts/private.py
# History codes, each printed with its fix (dev/toy/hist.py): HIST-E01 the base ref is missing; HIST-E02 the history is shallow;
# HIST-E03 a git command failed; HIST-E04 a fixture could not be built. A history that can't be read fails this test.
"""full-auto-no-new-file (full-auto-all:4, TD1225): the full-auto-all goal's own merge adds no file under skills/ or listing.json.

The row reads that one merge on origin/main (found by its message, compared with its first parent), the way the tasks and
null-report rows do (o863, TD1194). Later goals' new skills files are bounded by GRD-21's package cap, which stays in force.
Negative controls run in this toy: a fixture of that merge adding a skills file, or listing.json, fails; one adding only a
document passes."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hist  # noqa: E402

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PR = r"^Merge pull request #[0-9]* from .*/loop/full-auto-all$"
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def added(repo):
    """(merge found, files the merge added under skills/ or listing.json): the first-parent merge of the goal's pull request on origin/main."""
    return hist.added(repo, PR, "skills", "listing.json", what="the full-auto-all goal's merge")


def fixture(files):
    """A repo whose origin/main has the goal's pull request merged, adding files."""
    repo = tempfile.mkdtemp(prefix="full-auto-files-")
    hist.fixture(repo, "init", "-q", "-b", "main", ".")
    hist.fixture(repo, "commit", "-q", "--allow-empty", "-m", "base")
    hist.fixture(repo, "checkout", "-q", "-b", "loop/full-auto-all")
    for name in files:
        os.makedirs(os.path.dirname(os.path.join(repo, name)) or repo, exist_ok=True)
        open(os.path.join(repo, name), "w").write("x\n")
    hist.fixture(repo, "add", "-A")
    hist.fixture(repo, "commit", "-q", "--allow-empty", "-m", "goal")
    hist.fixture(repo, "checkout", "-q", "main")
    hist.fixture(repo, "merge", "-q", "--no-ff", "-m", "Merge pull request #1 from o/loop/full-auto-all", "loop/full-auto-all")
    hist.fixture(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    return repo


hist.require(root, "the full-auto-all goal's merge")
merge, files = added(root)
check(bool(merge) and files == [], "the full-auto-all merge is found on origin/main and adds no file under skills/ or listing.json: %s" % hist.shown(files))
check(added(fixture(["docs/a.md"]))[1] == [], "control: a fixture of the merge adding only a document reads as clean")
check(added(fixture(["skills/x/scripts/other.py"]))[1] == ["skills/x/scripts/other.py"], "negative control: a fixture of the merge adding a skills file still fails")
check(added(fixture(["listing.json"]))[1] == ["listing.json"], "negative control: a fixture of the merge adding listing.json still fails")
print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
