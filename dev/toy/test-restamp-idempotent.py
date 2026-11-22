#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/counting.py
"""restamp-own is idempotent (#5797, Operation TD969): with nothing stale it makes no commit and appends no rows; with
one really stale page it restamps that page once, and a second run makes no commit. The negative control runs the same
check against audit.py with the fix undone (an empty stale set restamping every page) and the check must fail.
usage: test-restamp-idempotent.py"""
import os
import shutil
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
scripts = os.path.join(root, "skills", "workflow-docs", "scripts")
sys.path.insert(0, scripts)
import criteria  # noqa: E402
import prd  # noqa: E402

fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                          cwd=repo, capture_output=True, text=True).stdout.strip()


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", newline="\n") as handle:
        handle.write(text)


def page(name, body_text):
    body = ("<!-- workflow-docs -->\n# %s\nReview: **Unreviewed**\n\n## Problem\n%s\n\n## Requirements\n- %s-1: Be useful\n\n"
            "## Non-goals\nNothing else here.\n\n## Success metrics\nIt stays fresh.\n\n## Tests\nNone yet.\n") % (name, body_text, name[0])
    now = prd.prints(criteria.sections(body), criteria.rules())
    return prd.set_review(body, "Review: **Reviewed 2026-01-01** <!-- prd %s -->" % " ".join("%s=%s" % (k, now[k]) for k in prd.KEYS))


def build():
    repo = tempfile.mkdtemp(prefix="restamp-idem-")
    git(repo, "init", "-q", "-b", "main")
    write(repo, ".loop/config.json", "{}\n")
    write(repo, ".loop/docs.tsv", "A\ta.py\nAB\tab.py\n")
    for n in ("a", "ab"):
        write(repo, n + ".py", '"""Docs."""\n\n\ndef run():\n    return 1\n')
        write(repo, "docs/wiki/%s.md" % n.upper(), page(n.upper(), "Readers need a page that says what %s.py does today." % n))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "two pages and their code")
    return repo


def restamp(repo, folder):
    out = subprocess.run([sys.executable, os.path.join(folder, "audit.py"), "restamp-own", "my-goal"], cwd=repo, capture_output=True, text=True)
    if out.returncode:
        print("restamp-own exited %d: %s" % (out.returncode, out.stderr.strip()[-300:]))
    return out.stdout.split() if not out.returncode else ["EXIT-%d" % out.returncode]


def snap(repo):
    """HEAD, the kept file and the working tree: what one restamp-own call may change."""
    return (git(repo, "rev-parse", "HEAD"), kept(repo), git(repo, "status", "--porcelain"))


def count(repo):
    return int(git(repo, "rev-list", "--count", "HEAD"))


def kept(repo):
    path = os.path.join(repo, ".loop", "kept", "my-goal.tsv")
    return open(path).read().splitlines() if os.path.isfile(path) else []


def run(folder):
    """Both done lines against the audit.py in folder; returns the outcomes."""
    repo = build()
    s0 = snap(repo)
    one = restamp(repo, folder)
    s1 = snap(repo)
    two = restamp(repo, folder)
    s2 = snap(repo)
    clean = (one, two, s0 == s1 == s2, kept(repo) == [] and s2[2] == "")
    write(repo, "a.py", '"""Docs."""\n\n\ndef run():\n    return 2\n')
    git(repo, "commit", "-q", "-am", "a real change to a.py")
    base = count(repo)
    done = restamp(repo, folder)
    t1 = snap(repo)
    again = restamp(repo, folder)
    t2 = snap(repo)
    rows = [row.split("\t")[0] for row in kept(repo)]
    return clean, (done, again, count(repo) == base + 1 and t1 == t2 and t2[2] == "", rows)


def relock_all(folder):
    """relock with a slug and an empty set still means every Reviewed page (the overload restamp-own's guard leans on)."""
    repo = build()
    code = "import sys; sys.path.insert(0, sys.argv[1]); import audit; print(' '.join(audit.relock(sys.argv[2], 'my-goal', ())))"
    out = subprocess.run([sys.executable, "-c", code, folder, repo], cwd=repo, capture_output=True, text=True)
    return sorted(out.stdout.split()) if not out.returncode else ["EXIT-%d" % out.returncode]


clean, stale = run(scripts)
check("nothing stale: two runs restamp nothing (%s)" % (clean[0] + clean[1]), clean[0] == [] and clean[1] == [])
check("nothing stale: no commit and no kept rows", clean[2] and clean[3])
check("one stale page: the first run restamps exactly that page (%s)" % stale[0], stale[0] == ["RESTAMPED", "A"])
check("one stale page: it appends only that page's row, once, in one commit (%s)" % stale[3], stale[3] == ["A"] and stale[2])
check("one stale page: the second run restamps nothing", stale[1] == [])
relocked = relock_all(scripts)
check("relock with a slug and an empty set still restamps every Reviewed page (%s)" % relocked, relocked == ["A", "AB"])

broken = tempfile.mkdtemp(prefix="restamp-idem-broken-")
shutil.rmtree(broken)
shutil.copytree(os.path.dirname(scripts), broken, ignore=shutil.ignore_patterns("__pycache__"))
copy = os.path.join(broken, "scripts", "audit.py")
text = open(copy).read()
undone = text.replace("if only else []", "")
check("negative control: the fix is in audit.py to undo", undone != text)
with open(copy, "w") as handle:
    handle.write(undone)
bad_clean, bad_stale = run(os.path.join(broken, "scripts"))
check("negative control: with the fix undone, a run with nothing stale restamps pages and makes a commit",
      bad_clean[0] != [] and not (bad_clean[2] and bad_clean[3]))
check("negative control: with the fix undone, the second run after a real stale page makes another commit", bad_stale[1] != [] or not bad_stale[2])
shutil.rmtree(broken, ignore_errors=True)
sys.exit(1 if fails else 0)
