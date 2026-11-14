#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/where.py skills/workflow-release/scripts/merge.py skills/workflow-release/scripts/wiki.py skills/workflow-release/scripts/autorelease.py
"""merge-from-main-checkout (#4020, #4004): the release runs from the repo's main checkout fast-forwarded to origin/<base>,
or the installed skills: where.where() refuses a script inside the repo's own goal worktrees (RUN_FROM_WORKTREE) and a
checkout behind origin/<base> (CHECKOUT_BEHIND, naming how far and the git merge --ff-only fix); a script outside the repo
is not checked. A merge refused for a moved head or base leaves the goal running at step pr, not done.

Builds a throwaway repo with a bare origin and a second clone that moves origin. usage: test-merge-where.py"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
import autorelease  # noqa: E402
import merge  # noqa: E402
import where  # noqa: E402

fails = 0


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok else 1


def git(*args, cwd):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=cwd, capture_output=True, text=True)


tmp = tempfile.mkdtemp(prefix="merge-where-")
origin, repo, other = (os.path.join(tmp, n) for n in ("origin.git", "repo", "other"))
git("init", "-q", "--bare", "-b", "main", origin, cwd=tmp)
git("clone", "-q", origin, repo, cwd=tmp)
open(os.path.join(repo, "a.txt"), "w").write("a\n")
git("add", "-A", cwd=repo); git("commit", "-q", "-m", "base", cwd=repo); git("push", "-q", "origin", "main", cwd=repo)
common = os.path.join(repo, ".git")
worktree_script = os.path.join(common, "loop", "worktrees", "g", "skills", "workflow-release", "scripts", "merge.py")
os.makedirs(os.path.dirname(worktree_script))
main_script = os.path.join(repo, "skills", "workflow-release", "scripts", "merge.py")
os.makedirs(os.path.dirname(main_script))
away_script = os.path.join(tmp, "installed", "merge.py")
os.makedirs(os.path.dirname(away_script))


def verdict(script):
    """The SystemExit text where.where(script, 'main') ends with, or '' when it lets the release run (cwd is the repo)."""
    old = os.getcwd()
    os.chdir(repo)
    try:
        where.where(script, "main")
        return ""
    except SystemExit as stop:
        return str(stop.code)
    finally:
        os.chdir(old)


said = verdict(worktree_script)
check("a script inside the repo's own goal worktree refuses RUN_FROM_WORKTREE", "RUN_FROM_WORKTREE" in said, said)
check("and names the main checkout and the installed skills as the fix", os.path.basename(repo) in said and "installed skills" in said, said)
import shutil  # noqa: E402
copy = os.path.dirname(worktree_script)
for name in os.listdir(os.path.join(root, "skills", "workflow-release", "scripts")):
    if name.endswith(".py"):
        shutil.copy(os.path.join(root, "skills", "workflow-release", "scripts", name), copy)
done = subprocess.run([sys.executable, "-B", os.path.join(copy, "wiki.py"), "publish", "g"], cwd=repo, capture_output=True, text=True)
check("wiki.py publish run from a goal worktree refuses RUN_FROM_WORKTREE too", done.returncode != 0 and "RUN_FROM_WORKTREE" in done.stderr + done.stdout, done.stderr[-300:])
check("the main checkout, level with origin, runs", verdict(main_script) == "")
git("clone", "-q", origin, other, cwd=tmp)
open(os.path.join(other, "b.txt"), "w").write("b\n")
git("add", "-A", cwd=other); git("commit", "-q", "-m", "origin moves", cwd=other); git("push", "-q", "origin", "main", cwd=other)
said = verdict(main_script)
check("a main checkout one commit behind origin refuses CHECKOUT_BEHIND, saying how far", "CHECKOUT_BEHIND" in said and "1 commit behind origin/main" in said, said)
check("and prints the fast-forward command", "merge --ff-only origin/main" in said, said)
check("a script outside the repo (the installed skills) is not checked, even while behind", verdict(away_script) == "")
git("merge", "-q", "--ff-only", "origin/main", cwd=repo)
check("once fast-forwarded the main checkout runs", verdict(main_script) == "")

# a refused move sends the goal back to its pr step, live
record = os.path.join(common, "loop", "runs", "g.json")
os.makedirs(os.path.dirname(record))
head = git("rev-parse", "HEAD", cwd=repo).stdout.strip()


def write():
    json.dump({"slug": "g", "branch": "main", "status": "done", "step": "release", "pr": "https://example.test/pull/1",
               "pr_base": head, "pr_head": "a" * 40, "report": {}}, open(record, "w"))
    json.dump({"auto_merge": True, "base": "main"}, open(os.path.join(repo, ".loop.json"), "w"))


os.makedirs(os.path.join(repo, ".loop"))
json.dump({"auto_merge": True, "base": "main"}, open(os.path.join(repo, ".loop", "config.json"), "w"))
write()
real_run = subprocess.run


def fake_run(args, *a, **k):
    if args and args[0] == "gh" and args[1:3] == ["pr", "view"]:
        return subprocess.CompletedProcess(args, 0, json.dumps({"state": "OPEN", "headRefOid": head}), "")
    return real_run(args, *a, **k)


old = os.getcwd()
os.chdir(repo)
sys.argv = ["merge.py", "g"]
subprocess.run = fake_run
out = io.StringIO()
try:
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = merge.main()
finally:
    subprocess.run = real_run
    os.chdir(old)
state = json.load(open(record))
check("a merge refused for HEAD_MOVED exits 4", code == 4 and "HEAD_MOVED" in out.getvalue(), out.getvalue())
check("and leaves the goal running at step pr, not done", state["status"] == "running" and state["step"] == "pr", str(state))
check("the goal is not mergeable until goal.py pr finishes it again", not autorelease.mergeable(state))
state["status"] = "done"
check("reopen gives the BASE_MOVED exit the same way", autorelease.reopen(state, 2) == 2 and state["status"] == "running" and state["step"] == "pr")
sys.exit(1 if fails else 0)
