#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-delivery/scripts/lanekit.py skills/workflow-docs/scripts/docs.py
"""stale-code-page (#4442, DOC-2): a page made stale only by the goal's own code change is re-stamped on the branch before the lane's rows run;
a page whose text really changed stays stale.

Done 1: the lane prep (lanekit.prep) re-stamps a Reviewed page and an Unreviewed page that only mapped code staled, in its commit, so docs check --own is clean.
Done 2: a Reviewed page whose reviewed wording changed is not re-stamped and still fails."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for sub in ("workflow-docs", "workflow-delivery", "workflow-regression"):
    sys.path.insert(0, os.path.join(root, "skills", sub, "scripts"))
os.environ["LOOP_ROLE"] = "worker"
sys.dont_write_bytecode = True
import criteria  # noqa: E402
import docs  # noqa: E402
import lanekit  # noqa: E402
import prd  # noqa: E402

TAB, NL = chr(9), chr(10)
fails = 0
repo = ""


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def git(*args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=repo, capture_output=True, text=True)


def write(path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", newline="\n") as handle:
        handle.write(text)


def commit(message):
    git("add", "-A")
    git("commit", "-q", "-m", message)


def body(problem):
    return ("<!-- workflow-docs -->\n# A\nReview: **Unreviewed**\n\n## Problem\n%s\n\n## Requirements\n- A-1: Be useful\n\n"
            "## Non-goals\nNothing else here.\n\n## Success metrics\nIt stays fresh.\n\n## Tests\nNone yet.\n") % problem


def reviewed(problem):
    text = body(problem)
    now = prd.prints(criteria.sections(text), criteria.rules())
    return prd.set_review(text, "Review: **Reviewed 2026-01-01** <!-- prd %s -->" % " ".join("%s=%s" % (k, now[k]) for k in prd.KEYS))


def build(page_text):
    """A one-page repo on branch loop/my-goal whose mapped code then changes; origin/main is the page's commit."""
    global repo
    repo = tempfile.mkdtemp(prefix="stale-code-page-")
    git("init", "-q", "-b", "main")
    write(".loop/config.json", "{}\n")
    write(".loop/docs.tsv", "A\ta.py\n")
    write("a.py", "def run():\n    return 1\n")
    write("docs/wiki/A.md", page_text)
    subprocess.run([sys.executable, os.path.join(root, "skills", "workflow-docs", "scripts", "criteria.py"), "render", "--tables"], cwd=repo, capture_output=True, text=True)
    commit("a page and its code")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("switch", "-q", "-c", "loop/my-goal")
    write("a.py", "def run():\n    return 2\n")
    commit("a real code change")
    os.chdir(repo)


def stale():
    return [p for k, p, _ in docs.problems(repo, "origin/main") if k == "STALE" and p == "A"]


def lane_prep():
    return lanekit.prep(repo, {}, os.path.join(repo, "lane.log"))


for label, text in (("a Reviewed page", reviewed("Readers need a page that says what a.py does today.")),
                    ("an Unreviewed page", body("Readers need a page that says what a.py does today."))):
    build(text)
    check("%s is stale after the goal's code change" % label, stale() == ["A"])
    out, why = lane_prep()
    check("the lane prep re-stamps %s in its commit (%s)" % (label, why or out), why is None and "LANE_PREP" in (out or ""))
    check("%s is fresh before the rows run, and the tree is clean" % label, not stale() and not git("status", "--porcelain").stdout.strip())

build(reviewed("Readers need a page that says what a.py does today."))
write("docs/wiki/A.md", reviewed("Readers need a page that says what a.py does today.").replace("Be useful", "Be very useful"))
commit("a wording change after the review")
write("a.py", "def run():\n    return 3\n")
commit("another code change")
was = stale()
out, why = lane_prep()
review = [l for l in open(os.path.join(repo, "docs/wiki/A.md")).read().splitlines() if l.startswith("Review")]
check("negative control: a page whose reviewed wording changed is stale and the prep does not re-stamp it (%s)" % review, was == ["A"] and "kept my-goal" not in review[0])
# a page that only main's code staled is not the goal's: it is left alone, and so is every page when the lane runs on main
def two_pages():
    build(reviewed("Readers need a page that says what a.py does today."))
    git("switch", "-q", "main")
    write(".loop/docs.tsv", TAB.join(("A", "a.py")) + NL + TAB.join(("B", "b.py")) + NL)
    write("b.py", NL.join(("def other():", "    return 1", "")))
    write("docs/wiki/B.md", reviewed("Readers need a page that says what b.py does today.").replace("# A", "# B"))
    commit("page B and its code, on main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    write("b.py", NL.join(("def other():", "    return 2", "")))
    commit("main changes b.py")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("switch", "-q", "loop/my-goal")
    git("merge", "-q", "--no-edit", "main")


two_pages()
before = [p for k, p, _ in docs.problems(repo, "") if k == "STALE"]
out, why = lane_prep()
text_b = open(os.path.join(repo, "docs/wiki/B.md")).read()
check("a page that only main's code staled stays stale and unmarked (before %s)" % before, "B" in before and "kept my-goal" not in text_b)
check("the goal's own page A was re-stamped beside it", "kept my-goal" in open(os.path.join(repo, "docs/wiki/A.md")).read())
two_pages()
git("switch", "-q", "main")
git("merge", "-q", "--no-edit", "loop/my-goal")
out, why = lane_prep()
check("a lane on the base branch re-stamps nothing", "kept" not in open(os.path.join(repo, "docs/wiki/A.md")).read() + open(os.path.join(repo, "docs/wiki/B.md")).read())
sys.exit(1 if fails else 0)
