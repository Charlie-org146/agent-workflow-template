#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/wiki.py skills/workflow-release/scripts/merge.py skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/docs.py
"""merge-main-own (#4020): merge.py runs from the main checkout, where HEAD is the base itself. wiki.pending must judge a
goal's pages by the goal's own diff, origin/<base>...origin/<branch>, never by the working directory's HEAD: a page that
main made stale (another goal's commit) is a FINDING, not a refusal, The goal's own staleness is judged where its files are (wiki.py prepare in the worktree, before the PR).

Builds a throwaway repo with a bare origin: main has page B stale; goal branch loop/g pushed to origin changes c.txt (no page
maps it) or a.txt (page A). The cwd is always the main checkout. usage: test-merge-main-own.py"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
os.environ["LOOP_ROLE"] = "worker"
import wiki  # noqa: E402

fails = 0


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok else 1


def git(*args, cwd=None):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=cwd or repo, capture_output=True, text=True)


def write(path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", newline="\n").write(text)


def commit(message):
    git("add", "-A"); git("commit", "-q", "-m", message)


def pending(**more):
    out, old = io.StringIO(), os.getcwd()
    os.chdir(repo)
    try:
        with contextlib.redirect_stdout(out):
            lines = wiki.pending(repo, {}, **more)
    finally:
        os.chdir(old)
    return [l for l in lines if ": STALE " in l], out.getvalue()


PAGE = "<!-- workflow-docs -->\n# %s\nThis page describes the %s file in this throwaway repo and what it is for today.\n"
tmp = tempfile.mkdtemp(prefix="merge-main-own-")
origin, repo = os.path.join(tmp, "origin.git"), os.path.join(tmp, "repo")
git("init", "-q", "--bare", "-b", "main", origin, cwd=tmp)
git("clone", "-q", origin, repo, cwd=tmp)
write(".loop/config.json", "{}\n")
write(".loop/docs.tsv", "A\ta.txt\nB\tb.txt\n")
write("a.txt", "one\n"); write("b.txt", "one\n")
write("docs/wiki/A.md", PAGE % ("A", "a")); write("docs/wiki/B.md", PAGE % ("B", "b"))
commit("pages")
git("push", "-q", "origin", "main")
git("switch", "-q", "-c", "loop/g")
write("c.txt", "goal work\n")
commit("the goal adds c.txt, which no page maps")
git("push", "-q", "origin", "loop/g")
git("switch", "-q", "main")
write("b.txt", "two\n")
commit("another goal's commit makes B stale on main")
git("push", "-q", "origin", "main")
git("switch", "-q", "loop/g")  # goal.py pr merges main into the goal's branch, so the head tree holds main's stale B too (#4343)
git("merge", "-q", "--no-edit", "origin/main")
git("push", "-q", "origin", "loop/g")
git("switch", "-q", "main")
# the main checkout: HEAD is the base; the goal exists only on origin
stale, said = pending()
check("judged by the main checkout's HEAD, every page stale on main refuses (the old behaviour)", len(stale) == 1 and stale[0].startswith("REWRITE B:"), str(stale))
stale, said = pending(head="origin/loop/g")
check("judged by the goal's branch, a page main made stale is no refusal (stale lines: %s)" % stale, not stale)
check("and it is printed as a FINDING for health", "FINDING STALE B" in said, said)
sys.exit(1 if fails else 0)
