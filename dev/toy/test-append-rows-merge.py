#!/usr/bin/env python3
"""#TD231: rows PRs add to the two regression tables merge without conflict in any order and sort to one byte order."""
import itertools
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TOP, "skills", "workflow-regression", "scripts"))
sys.dont_write_bytecode = True
import regression  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@e.test", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@e.test",
           GIT_TERMINAL_PROMPT="0")
ATTRS = open(os.path.join(TOP, ".gitattributes")).read()
ROWS, ISSUES = ".loop/regression.tsv", ".loop/regression-issues.tsv"


def git(cwd, *args, check=True):
    done = subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "core.autocrlf=" + AUTOCRLF] + list(args), cwd=cwd,
                          capture_output=True, text=True, env=ENV)
    if check and done.returncode:
        sys.exit("FAIL: git %s: %s" % (" ".join(args), done.stderr.strip()[:300]))
    return done


def put(cwd, name, text):
    os.makedirs(os.path.dirname(os.path.join(cwd, name)), exist_ok=True)
    with open(os.path.join(cwd, name), "w", newline="") as handle:
        handle.write(text)


def build(attrs):
    """A repo with the tables and one branch per goal: g1..g3 each add a row and a link; d1, d2 both edit row base."""
    cwd = tempfile.mkdtemp(prefix="rowsmerge-")
    git(cwd, "init", "-q", "-b", "main")
    put(cwd, ".gitattributes", attrs)
    put(cwd, ROWS, "# id\tlevel\tcommand\nbase\tland\ttrue\n")
    put(cwd, ISSUES, "# link\tstate\nhttps://x/issues/1\tclosed\n")
    git(cwd, "add", "-A")
    git(cwd, "commit", "-q", "-m", "base")
    for name in ("g1", "g2", "g3", "d1", "d2"):
        git(cwd, "checkout", "-q", "-b", name, "main")
        if name[0] == "g":
            put(cwd, ROWS, open(os.path.join(cwd, ROWS), newline="").read() + "row-%s\tland\ttrue\n" % name)
            put(cwd, ISSUES, open(os.path.join(cwd, ISSUES), newline="").read() + "https://x/issues/9%s\topen\n" % name[1])
        else:
            put(cwd, ROWS, "# id\tlevel\tcommand\nbase\tland\techo %s\n" % name)
        git(cwd, "commit", "-q", "-am", name)
    git(cwd, "checkout", "-q", "main")
    return cwd


def merged(cwd, order):
    git(cwd, "checkout", "-q", "-f", "-B", "t", "main")
    for name in order:
        if git(cwd, "merge", "-q", "--no-edit", name, check=False).returncode:
            git(cwd, "merge", "--abort", check=False)
            return False
    return True


def tables(cwd):
    return tuple(open(os.path.join(cwd, name), "rb").read() for name in (ROWS, ISSUES))


for AUTOCRLF in ("false", "true"):
    cwd = build(ATTRS)
    try:
        seen = set()
        for order in itertools.permutations(("g1", "g2", "g3")):
            if not merged(cwd, order):
                sys.exit("FAIL: merging %s conflicted with merge=union (autocrlf=%s)" % (order, AUTOCRLF))
            regression.sort_tables(cwd)
            seen.add(tables(cwd))
        if len(seen) != 1 or b"\r" in next(iter(seen))[0]:
            sys.exit("FAIL: the six orders gave %d different tables (autocrlf=%s)" % (len(seen), AUTOCRLF))
        print("PASS: #TD231: three goals' rows merge in all six orders without a conflict and sort to one table (autocrlf=%s)" % AUTOCRLF)
        if not merged(cwd, ("d1", "d2")):
            sys.exit("FAIL: two edits of one row should keep both under union, not conflict (autocrlf=%s)" % AUTOCRLF)
        try:
            regression.sort_tables(cwd)
            sys.exit("FAIL: a duplicate id was not refused (autocrlf=%s)" % AUTOCRLF)
        except SystemExit as error:
            if "duplicate base" not in str(error.code):
                sys.exit("FAIL: the refusal did not name the id: %s" % error.code)
        print("PASS: #TD231: a row two goals both edited is a duplicate id, and sort refuses it naming base (autocrlf=%s)" % AUTOCRLF)
    finally:
        shutil.rmtree(cwd, ignore_errors=True)

cwd = build("")
try:
    if all(merged(cwd, order) for order in itertools.permutations(("g1", "g2", "g3"))):
        sys.exit("FAIL: negative control: without .gitattributes the merges did not conflict")
    print("PASS: #TD231: negative control: without merge=union the same merges conflict")
finally:
    shutil.rmtree(cwd, ignore_errors=True)

# An old-order branch merged around a sorted one keeps both orders under union: the identical rows collapse, nothing is refused.
for AUTOCRLF in ("false",):
    cwd = tempfile.mkdtemp(prefix="rowsmerge-")
    try:
        git(cwd, "init", "-q", "-b", "main")
        put(cwd, ".gitattributes", ATTRS)
        put(cwd, ROWS, "# id\tlevel\tcommand\nrow-c\tland\ttrue\nrow-a\tland\ttrue\nrow-b\tland\ttrue\n")
        put(cwd, ISSUES, "# link\tstate\nhttps://x/issues/1\tclosed\n")
        git(cwd, "add", "-A")
        git(cwd, "commit", "-q", "-m", "base")
        git(cwd, "checkout", "-q", "-b", "sorted", "main")
        regression.sort_tables(cwd)
        git(cwd, "commit", "-q", "-am", "sorted")
        git(cwd, "checkout", "-q", "-b", "old", "main")
        put(cwd, ROWS, open(os.path.join(cwd, ROWS), newline="").read() + "row-d\tland\ttrue\n")
        git(cwd, "commit", "-q", "-am", "old order plus a row")
        out = set()
        for order in (("sorted", "old"), ("old", "sorted")):
            if not merged(cwd, order):
                sys.exit("FAIL: an old-order branch and a sorted one conflicted under union: %s" % (order,))
            regression.sort_tables(cwd)
            out.add(tables(cwd))
        text = next(iter(out))[0].decode().replace("\r\n", "\n")
        if len(out) != 1 or text.count("row-a\t") != 1 or "row-d\t" not in text:
            sys.exit("FAIL: the old-order merge left %d tables or a duplicate row:\n%s" % (len(out), text))
        print("PASS: #TD231: an old-order branch merged around a sorted one leaves no duplicate and sort refuses nothing")
    finally:
        shutil.rmtree(cwd, ignore_errors=True)

print("PASS: #TD231: rows added by separate goals merge in any order and release sorts them to one byte order")
