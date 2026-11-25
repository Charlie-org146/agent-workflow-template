#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-regression/scripts/regression.py skills/workflow-release/scripts/merge.py skills/workflow-delivery/scripts/private.py
"""TSK-1.4 (task first): a red main does not stop task merges by themselves. The real gate here is regression.py's run over the rows of a
pull request's own head: a row red on main and listed in .loop/regression-known.tsv counts as known and the run passes (exit 0), so a
task goal's green pull request goes on; a row red on the head and not known counts failed (exit 1), so a red that reaches the pull
request's own run still stops it; take the known list away (the mutation) and the same run fails. Nothing in the gate is replaced
and no gate file is edited. The safety clause: this toy reports plainly that NO merge-side safety boundary exists (merge.py and the
gate files have no check that refuses a pull request for touching a safety class), so that clause of TSK-1.4 is UNPROVEN.
Hermetic: temp repos, an empty temp HOME, no network."""
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
skills = os.path.join(here, "..", "..", "skills")
REGRESSION = os.path.join(skills, "workflow-regression", "scripts", "regression.py")
failed = []
tmp = tempfile.mkdtemp()
home = tempfile.mkdtemp()


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    ok or failed.append(text)


def row(name, command):
    return "%s\tland\t%s\tTSK-1\t2026-11-24\tGiven %s, when it runs, then it is %s\tcriterion\t\n" % (name, command, name, "red" if command == "false" else "green")


def repo(known=True, extra=""):
    top = tempfile.mkdtemp(dir=tmp)
    git = lambda *a: subprocess.run(["git", "-C", top, *a], capture_output=True, text=True, check=True)
    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    os.makedirs(os.path.join(top, ".loop"))
    open(os.path.join(top, ".loop", "regression.tsv"), "w").write(row("row-main-red", "false") + row("row-green", "true") + extra)
    known and open(os.path.join(top, ".loop", "regression-known.tsv"), "w").write("row-main-red\tred on main since an earlier goal; see #1\n")
    open(os.path.join(top, ".loop", "queue.md"), "w").write("- slug: v110-task | release: v1.1.0 | goal: a task goal | done: d\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main is red on one known row")
    return top


def gate(top):
    """The real gate run from a clean environment: (exit code, the RESULT line)."""
    done = subprocess.run([sys.executable, REGRESSION, "run", "--timeout", "60"], cwd=top, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          env={"HOME": home, "PATH": os.environ["PATH"], "TERM": "dumb"})
    return done.returncode, next((x for x in done.stdout.splitlines() if x.startswith("RESULT")), done.stdout[-200:] + done.stderr[-200:])


top = repo()
code, line = gate(top)
check(code == 0 and "1 known" in line and "0 failed" in line, "main is red on one known row and the run still passes, so a green task pull request is not stopped: %s" % line)
subprocess.run(["git", "-C", top, "checkout", "-q", "-b", "loop/v110-task"], check=True)
open(os.path.join(top, "task.txt"), "w").write("the task goal's change\n")
subprocess.run(["git", "-C", top, "add", "-A"], check=True)
subprocess.run(["git", "-C", top, "commit", "-q", "-m", "the task goal"], check=True)
code, line = gate(top)
check(code == 0 and "0 failed" in line, "the task goal's own pull request head, green on every row but the known one, passes: %s" % line)
code, line = gate(repo(extra=row("row-new-red", "false")))
check(code == 1 and "1 failed" in line, "a red that reaches the pull request's own run (a row not known) still stops it: %s" % line)
code, line = gate(repo(known=False))
check(code == 1 and "1 failed" in line and "0 known" in line, "mutation: without the known list the same main-red row fails the run, so the allowance is what lets the task through: %s" % line)
gone = repo()
open(os.path.join(gone, ".loop", "regression-known.tsv"), "w").write("some-other-row\tnot this one\n")
code, line = gate(gone)
check(code == 1, "a known list that names another row does not excuse this one (the allowance is per row): %s" % line)

# the safety clause: no merge-side boundary exists, said plainly
text = "".join(open(os.path.join(skills, "workflow-release", "scripts", name), encoding="utf-8").read().lower() for name in ("merge.py", "autorelease.py"))
text += open(os.path.join(skills, "workflow-delivery", "scripts", "private.py"), encoding="utf-8").read().lower()
boundary = re.search(r"safety[ _-]?class|safety[ _-]?boundary|risky[ _-]?path", text)
check(not boundary, "UNPROVEN: no merge-side safety boundary exists (merge.py, autorelease.py and private.py name no safety class or risky path), so TSK-1.4's clause that a safety class still stops a merge cannot be tested here; when a boundary is added this case must become a real one")

print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
