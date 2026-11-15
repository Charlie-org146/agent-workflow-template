#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/wiki.py
"""audit-head-docs (#4340's way, for the docs scripts): merge.py's wiki check (wiki.pending) judges a PR head's pages with the
head's own docs.py when its tree has one, so a goal that changes a render or the Review stamp can merge. Each branch changes
a.txt, so main's docs.py calls page A stale. Branch `own-ok` carries a docs.py whose audit finds nothing, so it passes; branch `own-bad`
carries one that finds A stale though main's says otherwise, so it is refused; a head with no docs.py falls back to main's.
usage: test-audit-head-docs.py"""
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


def stale(head):
    with contextlib.redirect_stdout(io.StringIO()):
        lines = wiki.pending(repo, {}, head=head)
    return [l for l in lines if ": STALE " in l]


STUB = "import sys\nprint(%r)\nsys.exit(%d)\n"
repo = tempfile.mkdtemp(prefix="audit-head-docs-")
git("init", "-q", "-b", "main")
write(".loop/config.json", "{}\n")
write(".loop/docs.tsv", "A\ta.txt\n")
write("a.txt", "one\n")
write("docs/wiki/A.md", "<!-- workflow-docs -->\n# A\nThis page describes the a file in this throwaway repo and what it is for today.\n")
commit("page")
write("a.txt", "two\n")
git("update-ref", "refs/remotes/origin/main", "main")
for name, text in (("own-ok", STUB % ("DOCS OK: 1 pages", 0)), ("own-bad", STUB % ("REWRITE A: STALE 1 commits since the page: x", 1)), ("no-own", "")):
    git("checkout", "-q", "-b", name, "main")
    write("a.txt", "two\n")
    commit("the goal changes a.txt, so A is stale under main's docs.py")
    write("skills/workflow-docs/scripts/docs.py" if text else "other.txt", text or "x\n")
    commit("the head " + name)
    git("update-ref", "refs/remotes/origin/" + name, name)
    git("checkout", "-q", "main")
check("a head whose own docs.py finds nothing passes though main's would call A stale", not stale("origin/own-ok"))
check("a head whose own docs.py finds A stale is refused", any(l.startswith("REWRITE A:") for l in stale("origin/own-bad")))
check("a head with no docs.py of its own falls back to main's", any(l.startswith("REWRITE A:") for l in stale("origin/no-own")))
print("PASS: merge.py judges the head's pages with the head's docs scripts" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
