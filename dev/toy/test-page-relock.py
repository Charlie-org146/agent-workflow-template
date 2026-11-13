#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/relock.py skills/workflow-docs/scripts/prd.py skills/workflow-docs/scripts/criteria.py
"""DOC-2: two branches each change a different reviewed line on one page; the merged page relocks with no new owner words.
A page with an unreviewed line stays LOCKED."""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
docs = os.path.join(here, "..", "..", "skills", "workflow-docs", "scripts")
sys.path.insert(0, docs)
import criteria  # noqa: E402
import prd  # noqa: E402

fails = 0


def check(ok, text):
    global fails
    print(("PASS: " if ok else "FAIL: ") + text)
    fails += 0 if ok else 1


def run(repo, *cmd):
    return subprocess.run(list(cmd), cwd=repo, capture_output=True, text=True, env=dict(os.environ, LOOP_OWNER_WORDS="toy owner"))


def page(a, b, c="gamma"):
    return ("# Toy\n\nReview: **Unreviewed**\n\n## Problem\n\n- p\n\n## Requirements\n\n### Functional\n\n"
            "- TOY-1: **Unreviewed** %s\n- TOY-2: **Unreviewed** %s\n- TOY-3: **Unreviewed** %s\n\n### Non-functional\n\nNone\n\n"
            "## Non-goals\n\n- n\n\n## Success metrics\n\n- m\n\n## Tests\n\n" % (a, b, c))


repo = tempfile.mkdtemp()
for cmd in (["git", "init", "-q", "-b", "main"], ["git", "config", "user.name", "t"], ["git", "config", "user.email", "t@t"]):
    run(repo, *cmd)
os.makedirs(os.path.join(repo, ".loop"))
os.makedirs(os.path.join(repo, "docs", "wiki"))
with open(os.path.join(repo, ".loop", "config.json"), "w") as handle:
    handle.write('{"wiki_dir": "docs/wiki"}')
path = os.path.join(repo, "docs", "wiki", "Toy.md")


def write(text):
    with open(path, "w") as handle:
        handle.write(text)


def read():
    with open(path) as handle:
        return handle.read()


def cli(*args):
    return run(repo, sys.executable, os.path.join(docs, "criteria.py"), *args)


def trouble():
    root = repo
    text = read()
    return prd.trouble(root, "Toy", text, criteria.sections(text), criteria.rules())


os.chdir(repo)
write(page("alpha", "beta"))
cli("review", "TOY-1", "TOY-2", "TOY-3", "Toy", "--user")
run(repo, "git", "add", "-A"); run(repo, "git", "commit", "-qm", "base")
check(not trouble(), "the reviewed page starts clean")
# the other goal: edits TOY-2, the owner reviews it and the page; its text reaches origin/main
run(repo, "git", "checkout", "-qb", "other")
write(read().replace("beta", "beta, edited by the other goal"))
cli("review", "TOY-2", "Toy", "--user")
main_text = read()
run(repo, "git", "commit", "-qam", "other goal")
run(repo, "git", "update-ref", "refs/remotes/origin/main", "HEAD")
run(repo, "git", "checkout", "-q", "main")
# this goal: edits TOY-1, the owner reviews it and the page
write(read().replace("alpha", "alpha, edited here"))
cli("review", "TOY-1", "Toy", "--user")
main_line = [l for l in main_text.splitlines() if l.startswith("- TOY-2:")][0]
write(chr(10).join(main_line if l.startswith("- TOY-2:") else l for l in read().splitlines()))  # the merge: both reviewed lines
red = [t for t in trouble() if t[0] == "LOCKED"]
check(not red, "no LOCKED while every line is owner-reviewed (main's line or reviewed here)")
done = subprocess.run([sys.executable, os.path.join(docs, "relock.py")], cwd=repo, capture_output=True, text=True)
check("RELOCKED Toy" in done.stdout, "relock re-stamps the page (%s)" % done.stdout.strip())
log = os.path.join(repo, ".git", "loop", "reviews.tsv")
check(os.path.exists(log) and "auto-relock: all lines owner-reviewed" in open(log).read(), "the reason is logged in reviews.tsv")
# a line nobody reviewed: the page stays LOCKED
cli("unreview", "TOY-3", "--user")
write(read().replace("gamma", "gamma, never reviewed"))  # a line nobody reviewed, changed
left = [t for t in trouble() if t[0] == "LOCKED"]
check(bool(left), "a line nobody reviewed leaves the page LOCKED")
sys.exit(1 if fails else 0)
