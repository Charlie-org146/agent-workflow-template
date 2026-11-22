#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/scripts/goal.py
"""DEL-1, issue 3468: `goal.py new --here` refuses in the repo's main checkout and names the worktree command, and passes
in a goal worktree under <common>/loop/worktrees. Calls fit.main_here the way goal.py new does, in throwaway repos.
DEL-19: the fixed goal format, a skipped review refuses the PR, and the drawn steps block goes stale with the code."""
import os
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-delivery", "scripts")
sys.path.insert(0, scripts)
import fit  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def git(*args):
    return subprocess.run(("git",) + args, check=True, capture_output=True, text=True).stdout.strip()


def refusal():
    """The refusal text main_here raises from the current folder, or ''."""
    def no(text):
        raise SystemExit("REFUSED: " + text)
    try:
        fit.main_here(SimpleNamespace(git=git, no=no), SimpleNamespace(slug="demo"))
    except SystemExit as stop:
        return str(stop)
    return ""


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
    main = os.path.join(tmp, "repo")
    os.makedirs(main)
    os.chdir(main)
    git("init", "-q", "-b", "main", ".")
    git("config", "user.email", "t@example.test")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "first")
    check(refusal() == "", "#3468: a main checkout of a repo with no worker worktrees is let through")
    os.makedirs(os.path.join(main, ".git", "loop", "worktrees"))
    said = refusal()
    check(said.startswith("REFUSED: --here in the repo's main checkout"), "#3468: the main checkout refuses")
    check("git worktree add -b loop/demo " in said and "/loop/worktrees/demo origin/main" in said, "#3468: the refusal names the worktree command")
    check("\n" not in said, "#3468: the refusal is one line")
    tree = os.path.join(main, ".git", "loop", "worktrees", "demo")
    git("worktree", "add", "-q", "-b", "loop/demo", tree)
    os.chdir(tree)
    check(refusal() == "", "#3468: a goal worktree under loop/worktrees is let through")
    os.chdir(root)

with open(os.path.join(scripts, "goal.py")) as handle:
    check("fit.main_here(" in handle.read(), "#3468: goal.py new calls the check")
# DEL-19: the goal format, the PR gate and the drawn steps
sys.path.insert(0, os.path.join(root, "skills", "workflow-docs", "scripts"))
import role  # noqa: E402
import sections  # noqa: E402
import proctree  # noqa: E402


def no(text):
    raise SystemExit("REFUSED: " + text)


def said(fn, *a):
    try:
        fn(*a)
    except SystemExit as stop:
        return str(stop)
    return ""


plain = tempfile.mkdtemp()
GF = fit.monitor("brief", False, "workflow-release").freeze_check
stub = SimpleNamespace(no=no, root=lambda: plain)
good = ["1. Given a repo, when a goal is frozen, then it names its task."]
check("no task" in said(GF, stub, SimpleNamespace(task=""), good), "DEL-19 freezing a goal with no task named is refused")
check("no task" in said(GF, stub, SimpleNamespace(task="  "), good), "DEL-19 a blank task counts as none")
check("not Given" in said(GF, stub, SimpleNamespace(task="t"), ["1. it works"]), "DEL-19 a done line that is not Given, when, then is refused")
check("not Given" in said(GF, stub, SimpleNamespace(task="t"), good + ["2. Given a repo, when x"]), "DEL-19 one bad line among good ones is refused")
check(said(GF, stub, SimpleNamespace(task="t"), good) == "", "DEL-19 a goal with a task and Given/when/then lines is accepted")
with_tasks = tempfile.mkdtemp()
os.makedirs(os.path.join(with_tasks, ".loop", "tasks"))
starts = SimpleNamespace(no=no, root=lambda: with_tasks)
import io, contextlib  # noqa: E401,E402
err = io.StringIO()
with contextlib.redirect_stderr(err):
    said(GF, starts, SimpleNamespace(task="no-brief"), good)
check("BRF-5" in err.getvalue() and "no-brief" in err.getvalue(), "DEL-23 a goal that names a task with no brief is refused when the repo keeps tasks")
for kind, name in (("feature", "newthing"), ("fix", "bugfix")):
    open(os.path.join(with_tasks, ".loop", "tasks", name + ".md"), "w").write("# T\n\n- Feature: ZZ-1\n- Kind: %s\n\n## Purpose\n\np\n\n## Done when\n\n- x\n" % kind)
os.makedirs(os.path.join(with_tasks, "docs", "wiki"))
open(os.path.join(with_tasks, "docs", "wiki", "P.md"), "w").write("- ZZ-1: **Unreviewed** a feature\n")
import hashlib  # noqa: E402
for name in ("newthing", "bugfix"):
    pth = os.path.join(with_tasks, ".loop", "tasks", name + ".md")
    body = open(pth).read()
    open(pth, "a").write("Frozen: %s r1 2026-11-22\n" % hashlib.sha256(body.encode()).hexdigest())
check("Unreviewed" in said(GF, starts, SimpleNamespace(task="newthing"), good), "DOC-27 freezing a new-work goal whose task serves an Unreviewed feature is refused")
check(said(GF, starts, SimpleNamespace(task="bugfix"), good) == "", "DOC-27 a bug-fix goal is allowed against an Unreviewed feature")
open(os.path.join(with_tasks, "docs", "wiki", "P.md"), "w").write("- ZZ-1: **Reviewed 2026-11-22** a feature\n")
check(said(GF, starts, SimpleNamespace(task="newthing"), good) == "", "DOC-27 the same goal freezes once the feature is Reviewed")
text = proctree.TEMPLATE.format(goal="G", slug="s", touches="a", eta="1m", task="t1", release="none", done="1. Given a, when b, then c.")
check("\n- Task: t1\n- Release: none\n\n## Done lines" in text and text.index("## Done lines") < text.index("1. Given"), "DEL-19 the goal file is title, slug, touches, ETA, task, release, then the done lines")
copies = {open(os.path.join(root, "skills", name, "scripts", "proctree.py"), "rb").read() for name in ("workflow-delivery", "workflow-monitoring", "workflow-regression")}
check(len(copies) == 1, "DEL-19 the three proctree.py copies stay identical")
skipped = SimpleNamespace(no=no, load=lambda slug: {"flow": {"review": "skipped no reviewer"}}, fit=fit, read=lambda p: "", goal_file=lambda slug: "")
check("review step was skipped" in said(role.requirement_gate, skipped, "g"), "DEL-19 a goal that skipped its review cannot open its pull request")
GOODFILE = proctree.TEMPLATE.format(goal="G", slug="s", touches="a", eta="1m", task="t1", release="none", done="1. Given a, when b, then c.")
gfile = os.path.join(plain, "s.md")
open(gfile, "w").write(GOODFILE)
done_review = SimpleNamespace(no=no, load=lambda slug: {"flow": {"review": "done"}}, guards=SimpleNamespace(extra=lambda d, s: {"findings": []}), state_dir=lambda: "", SKILLS="/nowhere", run=lambda *a: None, config=lambda: {"base": "main"},
                              fit=fit, read=lambda p: open(p).read(), goal_file=lambda slug: gfile)
check("review step was skipped" not in said(role.requirement_gate, done_review, "g"), "DEL-19 a goal whose review is done passes that gate")
check(said(role.requirement_gate, done_review, "g") == "", "DEL-19 a goal file with every part passes the pull request gate")
open(gfile, "w").write(GOODFILE.replace("- Release: none\n", ""))
check("lacks Release" in said(role.requirement_gate, done_review, "g"), "DEL-19 a goal file missing its Release line cannot open its pull request")
open(gfile, "w").write(GOODFILE.replace("- Touches: a\n", ""))
check("lacks Touches" in said(role.requirement_gate, done_review, "g"), "DEL-19 a goal file missing its Touches line cannot open its pull request")
open(gfile, "w").write(GOODFILE.replace("1. Given a, when b, then c.", ""))
check("lacks" in said(role.requirement_gate, done_review, "g"), "DEL-19 a goal file with no done line cannot open its pull request")
# adopt: the goal file already names the task
adopt_args = SimpleNamespace(slug="s")
adopting = SimpleNamespace(no=no, root=lambda: plain, goal_file=lambda slug: gfile)
open(gfile, "w").write(GOODFILE)
GF(adopting, adopt_args, good)
check(adopt_args.task == "t1", "DEL-19 an adopted goal takes the task its goal file names")
open(gfile, "w").write(GOODFILE.replace("- Task: t1\n", ""))
check("no task" in said(GF, adopting, SimpleNamespace(slug="s"), good), "DEL-19 an adopted goal file with a Release line and no task is refused")
block = lambda body: "x\n<!-- steps -->%s<!-- /steps -->\n" % body
check(sections.stale("P", block(sections.steps())) == [] and sections.stale("P", "no block here") == [], "DEL-19 a drawn steps block equal to the code's steps is fresh")
check(bool(sections.stale("P", block("Steps: idea, plan."))) and "DEL-19.4" in sections.stale("P", block("Steps: idea, plan."))[0][2], "DEL-19 a step added to the code without regenerating the block fails the docs check")
with open(os.path.join(scripts, "flow.py")) as handle:
    steps = re.findall(r'"(\w+)"', re.search(r"^STEPS = \(([^)]*)\)", handle.read(), re.M)[1])
check(sections.steps() == "Steps: " + ", ".join(steps) + ".", "DEL-19 the steps are read from flow.py's STEPS")
with open(os.path.join(root, "docs", "wiki", "Delivery.md")) as handle:
    check(sections.stale("Delivery", handle.read()) == [], "DEL-19 the Delivery page's drawn steps match the code today")
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
