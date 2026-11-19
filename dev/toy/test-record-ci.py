#!/usr/bin/env python3
# windows: ok
# reads: dev/recordonly.py skills/workflow-regression/scripts/lanes_cli.py
# reads: skills/workflow-delivery/scripts/role.py
"""record-ci (DEL-1): CI skips the affected rows only for goal.py pr's record commit on a parent whose check passed.

`python3 dev/toy/test-record-ci.py skip` proves the skips (and that the workflow template wires the step in);
`... full` proves every other head still gets the full round."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "dev"))
import recordonly  # noqa: E402

SUBJECT = recordonly.SUBJECT
ROW = '| [t](Tests#t-x) | defect | open (2026-11-17) | x |\n'
fails = 0


def check(name, ok):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name)
    fails += 0 if ok else 1


def repo():
    top = tempfile.mkdtemp()
    os.chdir(top)
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"], ["config", "commit.gpgsign", "false"], ["config", "core.autocrlf", "false"]):
        subprocess.run(["git"] + cmd, check=True)
    os.makedirs("docs/wiki")
    os.makedirs(".loop")
    for path, text in ((recordonly.ISSUES, "a\topen\n"), ("docs/wiki/Tests.md", "# T\n" + ROW + "prose\n"), ("x.py", "1\n")):
        open(path, "w", newline="\n").write(text)
    return commit("work")


def commit(subject, **files):
    for path, text in files.items():
        open(path.replace("__", "/").replace("_dot_", "."), "w", newline="\n").write(text)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-q", "-m", subject], check=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def decide(runs, **kw):
    recordonly.runs_of = lambda sha: runs
    return recordonly.decide(wait=kw.get("wait", 0), nap=0)


GREEN = [{"name": "affected", "status": "completed", "conclusion": "success"}]
mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode == "skip":
    parent = repo()
    commit(SUBJECT, **{".loop__regression-issues_dot_tsv": "a\tclosed\n", "docs__wiki__Tests_dot_md": "# T\n" + ROW.replace("open", "closed") + "prose\n"})
    code, line = decide(GREEN)
    check("a record commit on a parent with a passing check skips the rows", code == 0 and line == "RECORD-ONLY " + parent)
    code, line = decide([{"name": "affected", "status": "completed", "conclusion": "cancelled"}] + GREEN)
    check("one passing affected run among several is enough", code == 0)
    check("recordonly.py names the subject role.py gives the record commit", SUBJECT in open(os.path.join(root, "skills", "workflow-delivery", "scripts", "role.py")).read())
    text = open(os.path.join(root, "skills", "workflow-regression", "scripts", "lanes_cli.py")).read()
    check("the workflow template runs recordonly.py and skips the rows on RECORD-ONLY", "recordonly.py" in text and "steps.rec.outputs.skip != 'true'" in text and "checks: read" in text)
elif mode == "full":
    parent = repo()
    commit(SUBJECT, x_dot_py="2\n")
    check("a record commit that touches another file runs the rows", decide(GREEN)[0] == 1)
    repo()
    commit(SUBJECT, docs__wiki__Tests_dot_md="# T\n" + ROW + "prose changed\n")
    check("a wiki line that is not a result row runs the rows", decide(GREEN)[0] == 1)
    repo()
    commit("work 2", **{".loop__regression-issues_dot_tsv": "a\tclosed\n"})
    check("a commit with another subject runs the rows", decide(GREEN)[0] == 1)
    repo()
    commit(SUBJECT, **{".loop__regression-issues_dot_tsv": "a\tclosed\n"})
    check("a parent with no affected check runs the rows", decide([])[0] == 1)
    check("a parent whose check failed runs the rows", decide([{"name": "affected", "status": "completed", "conclusion": "failure"}])[0] == 1)
    check("a parent whose check is still running runs the rows after the wait", decide([{"name": "affected", "status": "in_progress", "conclusion": None}])[0] == 1)
    out = lambda *a: subprocess.run(["git"] + list(a), capture_output=True, text=True, check=True).stdout.strip()
    merge = out("commit-tree", "HEAD^{tree}", "-p", "HEAD", "-p", "HEAD~1", "-m", SUBJECT)
    recordonly.runs_of = lambda sha: GREEN
    code = recordonly.decide(merge, wait=0, nap=0)[0]
    check("a merge commit runs the rows", code == 1)
elif mode == "adopter":  # a repo without dev/recordonly.py: the step must not fail, and the rows must run
    import shutil
    sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
    import lanes_cli
    if not shutil.which("bash"):
        sys.exit(77)
    text = lanes_cli.NARROW.replace("@BASE@", "main").replace("@LEVELS@", "nightly")
    run = text.split("id: rec")[1].split("run: |\n")[1].split("      - if:")[0]
    script = "\n".join(line[10:] for line in run.split("\n")).replace("${{ github.event.pull_request.head.sha || github.sha }}", "HEAD")
    top = tempfile.mkdtemp()
    out = os.path.join(top, "out")
    done = subprocess.run(["bash", "-e", "-c", script], cwd=top, env=dict(os.environ, GITHUB_OUTPUT=out), capture_output=True, text=True)
    check("without dev/recordonly.py the step exits 0", done.returncode == 0)
    check("and it reports skip=false, so the rows run", open(out).read().strip() == "skip=false")
    import re
    bad = [x for x in text.split(chr(10)) if re.match(r"^\s*[\w-]+: \$\{\{", x) and ": " in x.split("}}")[0].split(": ", 1)[1]]
    check("no workflow value is an unquoted expression holding a colon and space (invalid YAML)", not bad)
    check("and the rows step runs unless skip is true", "- if: steps.rec.outputs.skip != 'true'" in text and "continue-on-error" not in text)
else:
    sys.exit("usage: test-record-ci.py skip|full|adopter")
sys.exit(1 if fails else 0)
