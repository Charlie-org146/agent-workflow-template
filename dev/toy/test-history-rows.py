#!/usr/bin/env python3
# reads: .loop/regression.tsv dev/toy/approved-row-changes.tsv dev/toy/hist.py dev/toy/test-tasks.py dev/toy/test-full-auto-files.py
# reads: dev/toy/test-guards-null-report.sh dev/toy/reap.sh skills/
"""The three history rows (tasks-rows-only-added, guards-null-report-nofiles, full-auto-no-new-file) fail, with a code and its fix,
whenever they can't read the history they compare. Each case runs a row's own command from the table in a throwaway copy of this
repo. The codes: HIST-E01 the base ref is missing; HIST-E02 the history is shallow; HIST-E03 a git command failed; HIST-E04 a
fixture could not be built. No network."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

top = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ROWS = ("tasks-rows-only-added", "guards-null-report-nofiles", "full-auto-no-new-file")
TOYS = ("dev/toy/test-tasks.py", "dev/toy/test-guards-null-report.sh", "dev/toy/test-full-auto-files.py")
TOUCHED = ("skills/workflow-regression/scripts/actions.py",) + TOYS + ("dev/toy/hist.py", "dev/toy/test-history-rows.py")
LIMIT = 20 * 1024  # dev/package.py's MAX_SCRIPT
WORD = "plantedname" + "qzx"  # a made-up private name, listed only in this test's own list


def history_diff(name, copy_name):
    """The shell condition that makes one read of the copy's own history fail and no fixture's: for the tasks row its diff of the rows
    table, for the null-report row its first diff, for the full-auto row every diff."""
    inside = 'case " $* " in *" diff "*) case "$(pwd -P) $* " in *"/%s "*) true;; *) false;; esac;; *) false;; esac' % copy_name
    if name == ROWS[0]:
        return inside + ' && case "$*" in *.loop/regression.tsv*) true;; *) false;; esac'
    if name == ROWS[1]:
        return inside + ' && [ ! -e "$0.failed" ] && : > "$0.failed"'
    return inside
failed = []


def check(ok, text, seen=""):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)
        if seen:
            print("      saw: " + " | ".join(seen.splitlines()[-3:])[:300])


def sh(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, errors="replace", timeout=600)


work = tempfile.mkdtemp(prefix="history-rows-")
command = {l.split("\t")[0]: l.split("\t")[2] for l in open(os.path.join(top, ".loop", "regression.tsv"), encoding="utf-8")
           if not l.startswith("#") and l.count("\t") >= 2}
base = sh(["git", "rev-parse", "origin/main"], top).stdout.strip()
real_git = shutil.which("git")


def copy(name, shallow=False, ref=True):
    """A throwaway copy of this repo with the working tree's test files; its origin/main is this repo's, unless ref is False."""
    path = os.path.join(work, name)
    if shallow:
        sh([real_git, "clone", "-q", "--depth", "1", "file://" + top, path], work)
    else:
        sh([real_git, "clone", "-q", top, path], work)
    if ref and not shallow:
        sh([real_git, "update-ref", "refs/remotes/origin/main", base], path)
    if not ref:
        sh([real_git, "update-ref", "-d", "refs/remotes/origin/main"], path)
        sh([real_git, "remote", "remove", "origin"], path)
    shutil.copytree(os.path.join(top, "dev", "toy"), os.path.join(path, "dev", "toy"), dirs_exist_ok=True)
    shutil.copy(os.path.join(top, ".loop", "regression.tsv"), os.path.join(path, ".loop", "regression.tsv"))
    return path


def fake_git(name, when, says):
    """A folder holding a git that fails, printing says, whenever the shell condition `when` holds, and is real git otherwise."""
    folder = os.path.join(work, name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "git")
    with open(path, "w") as handle:
        handle.write('#!/bin/sh\nif %s; then printf "%%s\\n" %s >&2; exit 128; fi\nexec %s "$@"\n' % (when, "'%s'" % says, real_git))
    os.chmod(path, 0o755)
    return folder


def row(name, where, extra=None, front=""):
    env = dict(os.environ, **(extra or {}))
    if front:
        env["PATH"] = front + os.pathsep + env["PATH"]
    got = sh(["bash", "-c", command[name]], where, env)
    return got.returncode, got.stdout + got.stderr


def toy_output(name, where, extra=None, front=""):
    """What the row's test prints when run the way the row runs it (the row itself may print nothing)."""
    toy = {ROWS[0]: ["python3", TOYS[0]], ROWS[1]: ["bash", TOYS[1], "nofiles"], ROWS[2]: ["python3", TOYS[2]]}[name]
    env = dict(os.environ, **(extra or {}))
    if front:
        env["PATH"] = front + os.pathsep + env["PATH"]
    got = sh(toy, where, env)
    return got.returncode, got.stdout + got.stderr


def first_fail(text):
    return next((l for l in text.splitlines() if l.startswith("FAIL")), "")


def coded(line, code, fix):
    return code in line and "Fix: " in line and fix in line and "In plain words: " in line and "Side effects: none." in line


good = copy("good")
for name in ROWS:
    rc, out = row(name, good)
    check(rc == 0, "control: %s passes in a copy with full history" % name, out)

# the tasks row also needs its test to end cleanly
stub = copy("stub")
with open(os.path.join(stub, TOYS[0]), "w") as handle:
    handle.write("print('PASS: no existing regression row is changed or removed')\nprint('PASS: no file is added under skills/')\n"
                 "print(\"PASS: negative control: a fixture of v110-tasks' merge adding another skills file still fails\")\nraise SystemExit(1)\n")
rc, out = row(ROWS[0], stub)
check(rc != 0, "tasks-rows-only-added fails when its test ends with an error, whatever it printed first", out)

# a read of the project's history that fails
for name in ROWS:
    where = copy("diff-" + name)
    broken = fake_git("fails-" + name, history_diff(name, "diff-" + name), "fatal: injected diff failure")
    rc, out = row(name, where, front=broken)
    check(rc != 0, "%s fails when a read of the project's history fails" % name, out)
    fresh = fake_git("fails-again-" + name, history_diff(name, "diff-" + name), "fatal: injected diff failure")
    line = first_fail(toy_output(name, where, front=fresh)[1])
    check(coded(line, "HIST-E03", "HIST-E01"), "%s: a failed history read gives HIST-E03 with its fix on the first failing line" % name, line)

# a shallow history, and no base ref
for code, fix, kind, args in (("HIST-E02", "git fetch --unshallow", "a shallow clone", dict(shallow=True)),
                              ("HIST-E01", "git fetch origin main:refs/remotes/origin/main", "a copy with no base ref", dict(ref=False))):
    for name in ROWS:
        where = copy(code + "-" + name, **args)
        rc, out = row(name, where)
        line = first_fail(toy_output(name, where)[1])
        check(rc != 0 and coded(line, code, fix), "%s in %s fails with %s and its fix" % (name, kind, code), line or out)

# a fixture that can't be built is its own code
nofixture = fake_git("no-fixture", 'case " $* " in *" commit "*) true;; *) false;; esac', "fatal: injected commit failure")
for name in ROWS:
    where = copy("fixture-" + name)
    line = first_fail(toy_output(name, where, front=nofixture)[1])
    check(coded(line, "HIST-E04", "temporary folder"), "%s: a fixture that can't be built gives HIST-E04 and not a history code" % name, line)

# nothing private or secret-shaped reaches an error line
names = os.path.join(work, "private-names")
with open(names, "w") as handle:
    handle.write(WORD + "\n")
token = "gh" + "p_" + "Q7" * 18
for name in ROWS:
    where = copy("%s-%s" % (WORD, name))
    leaky = fake_git("leaky-" + name, history_diff(name, "%s-%s" % (WORD, name)), "fatal: cannot read %s/%s/repo for %s with %s" % (work, WORD, WORD, token))
    extra = {"LOOP_PRIVATE_NAMES": names}
    out = toy_output(name, where, extra, leaky)[1]
    line = first_fail(out)
    check("HIST-E03" in line and WORD not in out and token not in out and work not in out,
          "%s: the error line holds no listed private name, secret-shaped value or local path, and still gives its code" % name, line)

# the committed headers and code lines name codes and fixes, no repository or merge
scan = os.path.join(top, "skills", "workflow-delivery", "scripts", "private.py")


def clean_text(text):
    path = os.path.join(work, "header.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return sh(["python3", scan, "hook", "message", path], top, dict(os.environ, LOOP_PRIVATE_NAMES=names)).returncode == 0


def code_lines(rel):
    text = open(os.path.join(top, rel), encoding="utf-8").read()
    return "\n".join(l.lstrip("# ") for l in text.splitlines() if "HIST-E0" in l)


lines = {rel: code_lines(rel) for rel in TOYS + ("dev/toy/hist.py",) if os.path.exists(os.path.join(top, rel))}
check(len(lines) == 4 and all(lines.values()) and all(clean_text(t) for t in lines.values()),
      "each history test and its helper list the codes, and those lines pass the private-name scan")
check(not clean_text("HIST-E01 in %s" % WORD), "negative control: a code line naming a listed private name fails that scan")
check(not any(re.search(r"https?://|github\.com|Merge pull request #\d", t) for t in lines.values()), "the code lines name no repository address or merge")


# every script this goal touches stays under the package limit
def over(paths):
    return [p for p in paths if os.path.exists(p) and os.path.getsize(p) >= LIMIT]


check(all(os.path.exists(os.path.join(top, p)) for p in TOUCHED) and over([os.path.join(top, p) for p in TOUCHED if p.startswith("skills/")]) == [],
      "every packaged script this goal touches is under %d bytes" % LIMIT)
new = [p for p in TOUCHED if p.startswith("dev/")]
check(over([os.path.join(top, p) for p in new]) == [], "every test script this goal touches is under %d bytes: %s" % (LIMIT, over([os.path.join(top, p) for p in new])))
big = os.path.join(work, "big.py")
with open(big, "w") as handle:
    handle.write("#" * LIMIT)
check(over([big]) == [big], "negative control: a script at the limit is reported")
shutil.rmtree(work, ignore_errors=True)
print("ALL PASS" if not failed else "FAILED: %d" % len(failed))
sys.exit(1 if failed else 0)
