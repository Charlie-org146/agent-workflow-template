#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/wiki.py skills/workflow-release/scripts/merge.py skills/workflow-docs/scripts/audit.py
"""audit-pr-head (#4208): merge.py's wiki check (wiki.pending) audits the goal's PR head render, not the main checkout's.
Main has page B stale (b.txt changed after B.md) and the checkout stays on main. Branch `fixes-b` rewrites B.md, so a PR that
fixes a page main left stale passes; branch `stales-a` changes a.txt, so a PR that stales a page is still refused.
START.md too (#4340): it is judged by the PR head's own skills (entry.py), not the main checkout's. Branch `adds-command`
adds a skill command and carries the START.md the head renders, so it passes; `stale-start` adds the command but keeps the old
START.md, so it is still refused.
usage: test-audit-pr-head.py [fix|stale|start]"""
import contextlib
import io
import shutil
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


def audited(head):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        lines = wiki.pending(repo, {}, head=head)
    return lines, out.getvalue()


def pending(head):
    lines, said = audited(head)
    return [l for l in lines if ": STALE " in l], said


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

if only in ("", "start"):
    repo = tempfile.mkdtemp(prefix="start-from-head-")
    skills = os.path.join(repo, "skills")
    shutil.copytree(os.path.join(root, "skills", "workflow-docs"), os.path.join(skills, "workflow-docs"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(skills, "workflow-setup", "references"))
    shutil.copy(os.path.join(root, "skills", "workflow-setup", "references", "settings.md"),
                os.path.join(skills, "workflow-setup", "references"))
    git("init", "-q", "-b", "main")
    write(".loop/config.json", "{}\n")
    write(".loop/docs.tsv", "A\ta.txt,skills/workflow-docs\n")
    write("a.txt", "one\n")
    write("docs/wiki/A.md", PAGE % ("A", "a") + "\n## Problem\n\nThe docs skill keeps this throwaway page honest.\n\n## Requirements\n\n"
          "### Functional\n\n- A-1: **Unreviewed** It lists the docs commands\n")
    ENTRY = [sys.executable, os.path.join(skills, "workflow-docs", "scripts", "entry.py"), "write", "--repo", repo]
    subprocess.run(ENTRY, capture_output=True)
    commit("start from main's skills")
    git("update-ref", "refs/remotes/origin/main", "main")
    skill = os.path.join(skills, "workflow-docs", "SKILL.md")
    with open(skill, newline="") as handle:
        text = handle.read()
    row = "| `/workflow-docs newcmd` | A command only this head's skills have | `python3 scripts/docs.py newcmd` |\n"
    cut = text.index("## Command map")
    cut = text.index("\n", text.index("|---", cut)) + 1
    for name, again in (("adds-command", True), ("stale-start", False)):
        git("checkout", "-q", "-b", name, "main")
        with open(skill, "w", newline="") as handle:
            handle.write(text[:cut] + row + text[cut:])
        again and subprocess.run(ENTRY, capture_output=True)
        commit("the goal adds a skill command")
        git("update-ref", "refs/remotes/origin/" + name, name)
        git("checkout", "-q", "main")
    check("the head's START.md carries its new command", "newcmd" in git("show", "origin/adds-command:.loop/START.md").stdout)
    lines = audited("origin/adds-command")[0]
    check("a PR that adds a skill command with the START.md its skills render passes (%s)" % lines,
          not any("START.md" in l for l in lines))
    lines = audited("origin/stale-start")[0]
    check("a PR whose START.md is stale for its own skills is still refused (%s)" % lines,
          any("START.md" in l for l in lines))
print("PASS: merge.py audits the PR head's pages" if not fails else "FAILED %d" % fails)
sys.exit(1 if fails else 0)
