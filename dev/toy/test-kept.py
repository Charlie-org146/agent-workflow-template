#!/usr/bin/env python3
# reads: skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/audit.py
"""A re-stamp is a line in the goal's own .loop/kept/<slug>.tsv: the page stays fresh (STALE without it), and three branches
that stamp one page merge in any order with no conflict. Prints PASS or FAIL lines; exit 1 on any FAIL."""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "..", "skills", "workflow-docs", "scripts")
FAILS = []


def run(*args, ok=True):
    done = subprocess.run(args, capture_output=True, text=True, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
    if ok and done.returncode and args[0] == "git":
        sys.exit("git %s: %s" % (" ".join(args[1:]), done.stderr))
    return done.stdout + done.stderr


def check(what, good):
    print(("PASS: " if good else "FAIL: ") + what)
    FAILS.append(what) if not good else None


def keep(slug):
    run(sys.executable, "-c", "import sys;sys.path.insert(0,%r);import audit;audit.keep('.',%r,['Page'])" % (DOCS, slug))


def main():
    os.chdir(tempfile.mkdtemp(prefix="kept-"))
    git = lambda *a: run("git", *a)
    docs = lambda *a: run(sys.executable, os.path.join(DOCS, "docs.py"), *a)
    git("init", "-q", "-b", "main")
    git("config", "user.name", "t"); git("config", "user.email", "t@t")
    os.makedirs(".loop"); open(".loop/config.json", "w").write('{"base": "main", "wiki_dir": "docs/wiki"}')
    open("calc.py", "w").write("X = 1\n")
    docs("add", "Page", "--paths", "calc.py")
    open("docs/wiki/Page.md", "w").write("<!-- workflow-docs -->\n# Page\n\nRun calc.py to use the toy calculator. Its tests sit beside it.\n")
    git("add", "-A"); git("commit", "-qm", "page")
    open("calc.py", "a").write("Y = 2\n"); git("commit", "-qam", "code")
    check("kept: STALE without a fragment", "STALE Page" in docs("check"))
    base = git("rev-parse", "HEAD").strip()
    for slug in ("k1", "k2", "k3"):
        git("switch", "-q", "-c", slug, base); keep(slug)
    for order in (("k1", "k2", "k3"), ("k3", "k2", "k1"), ("k2", "k3", "k1")):
        git("switch", "-q", "-C", "m", base)
        clean = all("onflict" not in git("merge", "-q", "--no-edit", slug) for slug in order)
        files = git("ls-files", ".loop/kept").split()
        check("kept: merged clean, page fresh (%s)" % " ".join(order), clean and len(files) == 3 and "STALE" not in docs("check"))
    return 1 if FAILS else 0


sys.exit(main())
