#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-health/scripts/health.py skills/workflow-health/scripts/file.py skills/workflow-health/scripts/issues.py
# reads: skills/workflow-health/scripts/report.py dev/toy/fakegh/fake.py
"""HLT-4, TD451 (c): health files and closes nothing from a checkout behind origin/main.

A checkout 257 commits behind once filed 34 false issues. In a throwaway repo with a bare origin and the fake gh
(dev/toy/fakegh/fake.py), `health.py file --group size` is run level with origin/main (it files one issue, as before),
then 3 commits behind (it prints the findings and `checkout is 3 commits behind origin/main: not filing`, exits 1 and
files nothing even with a new finding), and `triage --close --yes` from the stale checkout closes nothing. usage: test-health-behind.py"""
import contextlib
import io
import json
import os
import runpy
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
scripts = os.path.join(root, "skills", "workflow-health", "scripts")
fake = os.path.join(here, "fakegh", "fake.py")
failed = []
real_run = subprocess.run


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def patched(argv, *a, **kw):
    if argv and argv[0] == "gh":
        args, i = [], 1
        while i < len(argv):
            if argv[i] == "--body-file":
                with open(argv[i + 1], encoding="utf-8") as f:
                    args += ["--body", f.read().rstrip(chr(10))]
                i += 2
            else:
                args.append(argv[i])
                i += 1
        kw.pop("capture_output", None)
        kw.pop("text", None)
        return real_run([sys.executable, fake] + args, capture_output=True, text=True, **kw)
    return real_run(argv, *a, **kw)


def git(*args):
    real_run(("git",) + args, check=True, capture_output=True, text=True)


def health(repo, *args):
    out, code = io.StringIO(), 0
    sys.argv, sys.path[:0] = [os.path.join(scripts, "health.py")] + list(args), [scripts]
    for name in ("health", "file", "issues", "report", "defects", "groups"):
        sys.modules.pop(name, None)
    os.chdir(repo)
    with contextlib.redirect_stdout(out):
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit as stop:
            code = stop.code or 0
    sys.path.pop(0)
    os.chdir(here)
    return out.getvalue(), code


def issues_of(d):
    path = os.path.join(d, "issues.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


subprocess.run = patched
with tempfile.TemporaryDirectory() as tmp:
    repo, other, bare, d = (os.path.join(tmp, n) for n in ("repo", "other", "origin.git", "gh"))
    os.makedirs(d)
    os.environ["FAKE_GH_DIR"] = d
    os.environ.pop("LOOP_HEALTH_GH_FIXTURE", None)
    git("init", "-q", "--bare", "-b", "main", bare)
    os.makedirs(os.path.join(repo, ".loop"))
    os.makedirs(os.path.join(repo, "skills", "x", "scripts"))
    with open(os.path.join(repo, ".loop", "config.json"), "w") as f:
        json.dump({"base": "main"}, f)
    with open(os.path.join(repo, ".loop", "docs.tsv"), "w") as f:
        f.write("Calc\tskills/x\nHome\tREADME.md\n")
    with open(os.path.join(repo, "skills", "x", "scripts", "near.py"), "w", newline="\n") as f:
        f.write("# pad\n" * 3400)
    git("init", "-q", "-b", "main", repo)
    for key, value in (("user.email", "t@example.test"), ("user.name", "t"), ("core.autocrlf", "false")):
        git("-C", repo, "config", key, value)
    git("-C", repo, "add", "-A")
    git("-C", repo, "commit", "-qm", "A near-limit script")
    git("-C", repo, "remote", "add", "origin", bare)
    git("-C", repo, "push", "-q", "origin", "main")
    out, code = health(repo, "file", "--group", "size")
    print(out)
    check(code == 0 and "DONE open" in out and "not filing" not in out and len(issues_of(d)) == 1,
          "a checkout level with origin/main files as before (one issue opened, exit %d)" % code)
    # three commits land on origin/main from another clone; repo has not fetched them
    git("clone", "-q", bare, other)
    for key, value in (("user.email", "t@example.test"), ("user.name", "t")):
        git("-C", other, "config", key, value)
    for n in range(3):
        with open(os.path.join(other, "n%d.txt" % n), "w") as f:
            f.write("x\n")
        git("-C", other, "add", "-A")
        git("-C", other, "commit", "-qm", "main moves %d" % n)
    git("-C", other, "push", "-q", "origin", "main")
    with open(os.path.join(repo, "skills", "x", "scripts", "near2.py"), "w", newline="\n") as f:  # a new finding the stale checkout would file
        f.write("# pad\n" * 3400)
    git("-C", repo, "add", "-A")
    git("-C", repo, "commit", "-qm", "A second near-limit script")
    before = issues_of(d)
    out, code = health(repo, "file", "--group", "size")
    print(out)
    check("checkout is 3 commits behind origin/main: not filing" in out and code == 1 and "DONE" not in out and issues_of(d) == before,
          "3 commits behind: it prints the line, files nothing and exits 1 (exit %d, %d issues)" % (code, len(issues_of(d))))
    check("near2.py" in out and "FINDINGS (2)" in out, "3 commits behind: the findings, the new one included, are still printed")
    out, code = health(repo, "triage", "--close", "--issue", "1", "--why", "the owner said so", "--yes")
    print(out)
    check("not filing" in out and code == 1 and all(i.get("state", "OPEN").upper() == "OPEN" for i in issues_of(d)),
          "3 commits behind: triage --close --yes closes nothing (exit %d)" % code)
os.chdir(here)
subprocess.run = real_run
if not failed:
    print("PASS: a stale checkout files and closes nothing")  # the one line the regression row greps
sys.exit(1 if failed else 0)
