#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/wiki.py skills/workflow-release/scripts/merge.py skills/workflow-docs/scripts/audit.py
"""audit-pr-head (#4208): merge.py's wiki check (wiki.pending) audits the goal's PR head render, not the main checkout's.
Main has page B stale (b.txt changed after B.md) and the checkout stays on main. Branch `fixes-b` rewrites B.md, so a PR that
fixes a page main left stale passes; branch `stales-a` changes a.txt, so a PR that stales a page is still refused.
usage: test-audit-pr-head.py [fix|stale]"""
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
only = sys.argv[1] if len(sys.argv) > 1 else ""


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


def pending(head):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        lines = wiki.pending(repo, {}, head=head)
    return [l for l in lines if ": STALE " in l], out.getvalue()


PAGE = "<!-- workflow-docs -->\n# %s\nThis page describes the %s file in this throwaway repo and what it is for today.\n"
repo = tempfile.mkdtemp(prefix="audit-pr-head-")
git("init", "-q", "-b", "main")
write(".loop/config.json", "{}\n")
write(".loop/docs.tsv", "A\ta.txt\nB\tb.txt\n")
write("a.txt", "one\n")
write("b.txt", "one\n")
write("docs/wiki/A.md", PAGE % ("A", "a"))
write("docs/wiki/B.md", PAGE % ("B", "b"))
commit("pages")
write("b.txt", "two\n")
commit("main changes b.txt, so B is stale on main")
git("update-ref", "refs/remotes/origin/main", "main")
git("checkout", "-q", "-b", "fixes-b")
write("b.txt", "three\n")
commit("the goal changes b.txt too, so the mapped path is its own")
write("docs/wiki/B.md", PAGE % ("B", "b") + "It now says what b.txt holds.\n")
commit("the goal rewrites page B")
git("update-ref", "refs/remotes/origin/fixes-b", "fixes-b")
git("checkout", "-q", "main")
git("checkout", "-q", "-b", "stales-a")
write("a.txt", "two\n")
commit("the goal changes a.txt, so A is stale")
git("update-ref", "refs/remotes/origin/stales-a", "stales-a")
git("checkout", "-q", "main")  # the main checkout, where merge.py runs

if only in ("", "fix"):
    stale, said = pending("origin/fixes-b")
    check("a PR that rewrites a page main left stale passes (stale lines: %s)" % stale, not stale)
if only in ("", "stale"):
    stale, said = pending("origin/stales-a")
    check("a PR that makes a page stale is still refused (stale lines: %s)" % stale,
          any(l.startswith("REWRITE A:") for l in stale))
    check("and main's own stale B stays a FINDING, not a refusal", not any("STALE B" in l for l in stale))
print("PASS: merge.py audits the PR head's pages" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
