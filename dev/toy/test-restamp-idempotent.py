#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/counting.py
"""restamp-own is idempotent (#5797, Operation TD969): with nothing stale it makes no commit and appends no rows; with
one really stale page it restamps that page once, and a second run makes no commit. The negative control runs the same
check against a copy with each fix undone (an empty stale set restamping every page; a failed check restamping on) and the check must fail.
usage: test-restamp-idempotent.py"""
import atexit
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


# No GIT_* variable from the caller (a hook's GIT_DIR, GIT_INDEX_FILE, GIT_CONFIG_PARAMETERS) may steer the fixture's git
# into the caller's checkout; no global signing, hooks or identity reach it either.
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
REPOS = []
atexit.register(lambda: [shutil.rmtree(path, ignore_errors=True) for path in REPOS])


def git(repo, *args):
    return subprocess.run(["git"] + list(args), cwd=repo, capture_output=True, text=True, env=ENV).stdout.strip()


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
    REPOS.append(repo)
    git(repo, "init", "-q", "-b", "main")
    for key, value in (("user.name", "t"), ("user.email", "t@t"), ("commit.gpgsign", "false"), ("core.hooksPath", os.devnull), ("core.autocrlf", "false")):
        git(repo, "config", key, value)
    write(repo, ".loop/config.json", "{}\n")
    write(repo, ".loop/docs.tsv", "A\ta.py\nAB\tab.py\n")
    for n in ("a", "ab"):
        write(repo, n + ".py", '"""Docs."""\n\n\ndef run():\n    return 1\n')
        write(repo, "docs/wiki/%s.md" % n.upper(), page(n.upper(), "Readers need a page that says what %s.py does today." % n))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "two pages and their code")
    return repo


def restamp(repo, folder):
    out = subprocess.run([sys.executable, os.path.join(folder, "audit.py"), "restamp-own", "my-goal"], cwd=repo, capture_output=True, text=True, env=ENV)
    if out.returncode:
        print("restamp-own exited %d: %s" % (out.returncode, out.stderr.strip()[-300:]))
    return out.stdout.split() if not out.returncode else ["EXIT-%d" % out.returncode]


def snap(repo):
    """HEAD, the kept file, the working tree and the reviews log: what one restamp-own call may change."""
    log = os.path.join(repo, ".git", "loop", "reviews.tsv")
    return (git(repo, "rev-parse", "HEAD"), kept(repo), git(repo, "status", "--porcelain"), open(log).read() if os.path.isfile(log) else "")


def count(repo):
    return int(git(repo, "rev-list", "--count", "HEAD"))


def kept(repo):
    path = os.path.join(repo, ".loop", "kept", "my-goal.tsv")
    return open(path).read().splitlines() if os.path.isfile(path) else []


def run(folder):
    """Two scenarios (nothing stale; one real change) against the scripts in folder; returns both outcomes."""
    repo = build()
    s0 = snap(repo)
    one = restamp(repo, folder)
    s1 = snap(repo)
    two = restamp(repo, folder)
    s2 = snap(repo)
    clean = (one, two, s0 == s1 == s2, kept(repo) == [] and s2[2] == "" and s2[3] == "")
    write(repo, "a.py", '"""Docs."""\n\n\ndef run():\n    return 2\n')
    git(repo, "commit", "-q", "-am", "a real change to a.py")
    base = count(repo)
    done = restamp(repo, folder)
    t1 = snap(repo)
    again = restamp(repo, folder)
    t2 = snap(repo)
    rows = [row.split("\t")[0] for row in kept(repo)]
    return clean, (done, again, count(repo) == base + 1 and t1 == t2 and t2[2] == "" and t1[3].count("\n") == 1 and "restamp\tA\tmy-goal" in t1[3], rows)


def crash_case(folder):
    """A failed docs.py check (here: an unreadable .loop/config.json) makes restamp-own exit non-zero and change nothing."""
    repo = build()
    write(repo, ".loop/config.json", "{not json")
    s0 = snap(repo)
    out = subprocess.run([sys.executable, os.path.join(folder, "audit.py"), "restamp-own", "my-goal"], cwd=repo, capture_output=True, text=True, env=ENV)
    return out.returncode, snap(repo) == s0


def relock_all(folder):
    """relock with a slug and an empty set still means every Reviewed page (the overload restamp-own's guard leans on)."""
    repo = build()
    code = "import sys; sys.path.insert(0, sys.argv[1]); import audit; print(' '.join(audit.relock(sys.argv[2], 'my-goal', ())))"
    out = subprocess.run([sys.executable, "-c", code, folder, repo], cwd=repo, capture_output=True, text=True, env=ENV)
    return sorted(out.stdout.split()) if not out.returncode else ["EXIT-%d" % out.returncode]


clean, stale = run(scripts)
check("nothing stale: two runs restamp nothing (%s)" % (clean[0] + clean[1]), clean[0] == [] and clean[1] == [])
check("nothing stale: no commit and no kept rows", clean[2] and clean[3])
check("one stale page: the first run restamps exactly that page (%s)" % stale[0], stale[0] == ["RESTAMPED", "A"])
check("one stale page: it appends only that page's row, once, in one commit (%s)" % stale[3], stale[3] == ["A"] and stale[2])
check("one stale page: the second run restamps nothing", stale[1] == [])
relocked = relock_all(scripts)
check("relock with a slug and an empty set still restamps every Reviewed page (%s)" % relocked, relocked == ["A", "AB"])
code, same = crash_case(scripts)
check("a failed docs check: restamp-own exits non-zero (%s) and changes nothing" % code, code != 0 and same)

def copy_scripts(*edits):
    """A copy of skills/workflow-docs (scripts and references, so the rules block loads) whose docs.py has each (old, new) edit applied."""
    broken = tempfile.mkdtemp(prefix="restamp-idem-broken-")
    shutil.rmtree(broken)
    shutil.copytree(os.path.dirname(scripts), broken, ignore=shutil.ignore_patterns("__pycache__"))
    copy = os.path.join(broken, "scripts", "docs.py")
    text = open(copy).read()
    for old, new in edits:
        check("negative control: %r is in docs.py to change" % old, old in text)
        text = text.replace(old, new)
    with open(copy, "w") as handle:
        handle.write(text)
    return os.path.join(broken, "scripts"), broken


def killed_case(guard):
    """The docs check prints a STALE line and then exits 3 (a stub standing in for a crash or a kill): restamp-own must exit non-zero and restamp nothing."""
    stub = os.path.join(tempfile.mkdtemp(prefix="restamp-idem-stub-"), "check.py")
    write(os.path.dirname(stub), "check.py", "import sys\nprint('STALE A: 1 commits since the page')\nsys.exit(3)\n")
    edits = [("os.path.abspath(__file__)", repr(stub))] + ([] if guard else [("r.returncode not in (0, 1) or ", "")])
    folder, broken = copy_scripts(*edits)
    repo = build()
    out = subprocess.run([sys.executable, os.path.join(folder, "audit.py"), "restamp-own", "my-goal"], cwd=repo, capture_output=True, text=True, env=ENV)
    shutil.rmtree(broken, ignore_errors=True)
    shutil.rmtree(os.path.dirname(stub), ignore_errors=True)
    return out.returncode, [row.split("\t")[0] for row in kept(repo)]


code, rows = killed_case(True)
check("a docs check that prints a STALE line and then exits 3: restamp-own exits non-zero (%s) and restamps nothing (%s)" % (code, rows), code != 0 and rows == [])
folder, broken = copy_scripts(("if only else []", ""))
bad_clean, bad_stale = run(folder)
check("negative control: with the empty-set fix undone, a run with nothing stale restamps pages and makes a commit",
      bad_clean[0] != [] and not (bad_clean[2] and bad_clean[3]))
check("negative control: with the empty-set fix undone, the second run after a real stale page makes another commit", bad_stale[1] != [] or not bad_stale[2])
shutil.rmtree(broken, ignore_errors=True)
folder, broken = copy_scripts(('sys.exit(r.stderr or "no check report")', "pass"))
code, same = crash_case(folder)
check("negative control: with the report-shape check undone, a failed docs check still exits zero (%s)" % code, code == 0)
shutil.rmtree(broken, ignore_errors=True)
code, rows = killed_case(False)
check("negative control: with the exit-status test undone, the killed check restamps A anyway (%s, %s)" % (code, rows), code == 0 and rows == ["A"])
sys.exit(1 if fails else 0)
