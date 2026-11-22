#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/actions.py skills/workflow-regression/scripts/runs.py skills/workflow-regression/scripts/tests.py
"""issue-gate-main: the written workflow's issue block writes issues only when the run is on main.

The block of the generated workflow is cut out and run against a fake gh on PATH that logs every call. The value of L (the
step's one expression, passed on its `python3 -` line) is the one GitHub's expression gives for the ref: --live on refs/heads/main, the word false on any other
ref. On main the failing row's issue is written; on a branch the row still runs and reports and the log holds no write call.
usage: test-issues-main-only.py; LOOP_TOY_GATE_OFF=1 drops the gate from the argument, as a red proof."""
import os
import re
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
scripts = os.path.join(here, "..", "..", "skills", "workflow-regression", "scripts")
sys.path.insert(0, scripts)
sys.dont_write_bytecode = True
import actions  # noqa: E402

failed = []
WRITES = ("issue create", "issue edit", "issue comment", "issue close", "issue reopen", "label create")


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


text = actions.render("17 */4 * * *")
found = re.search(r"python3 - (\$L) <<'PY'\n(.*?)\n\s+PY\n", text, re.S)
check(bool(found), "the issue block's command line passes the step's L variable, so its run text holds no expression")
source = "\n".join(line[10:] for line in found.group(2).split("\n")) if found else ""
env_line = re.search(r"^ +L: (.*)$", text, re.M)
gate = env_line.group(1) if env_line else ""
parts = re.fullmatch(r"\$\{\{ github\.ref == '([^']+)' && '([^']+)' \}\}", gate)
check(bool(parts) and parts.groups() == ("refs/heads/main", "--live"), "L is --live only when github.ref is refs/heads/main (%s)" % gate)
step = text[text.index("here=$(mktemp -d)"):]
step = step[:step.index("\n      - name:")]
check("${{" not in step and len(step) > 0, "the step's run text holds no ${{ expression (it is %d characters; GitHub parses a run text holding one as one expression of at most 21000)" % len(step))
check(all(len(x) <= 21000 for x in re.findall(r"\$\{\{.*?\}\}", text)), "every expression in the written workflow is short")
loaded = None
try:
    import yaml
    loaded = yaml.safe_load(text)
except ImportError:
    done = subprocess.run(["ruby", "-ryaml", "-e", "puts YAML.load(STDIN.read).keys.inspect"], input=text, capture_output=True, text=True) if shutil.which("ruby") else None
    loaded = done is not None and done.returncode == 0 and "jobs" in done.stdout
    if done is None:
        print("NOTE: neither PyYAML nor ruby is here, so the file was not loaded as YAML")
        loaded = True
check(bool(loaded) and (not isinstance(loaded, dict) or "jobs" in loaded), "the written workflow loads as YAML")


def argument(ref):
    """What GitHub puts in L for this ref: the expression's value, false when the comparison is false."""
    if os.environ.get("LOOP_TOY_GATE_OFF"):
        return "--live"
    return gate if not parts else parts.group(2) if ref == parts.group(1) else "false"


def run(ref):
    """The block once on this ref, its row failing: (exit code, output, the gh calls it made)."""
    work = tempfile.mkdtemp(prefix="issue-gate-")
    log, shim = os.path.join(work, "gh.log"), os.path.join(work, "bin")
    os.makedirs(shim)
    with open(os.path.join(shim, "gh"), "w") as handle:
        handle.write('#!/bin/sh\necho "$@" >> "$GH_LOG"\n')
    os.chmod(os.path.join(shim, "gh"), 0o755)
    os.makedirs(os.path.join(work, ".loop"))
    with open(os.path.join(work, ".loop", "regression.tsv"), "w") as handle:
        handle.write("# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n"
                     "red\tland\tpython3 -c 'raise SystemExit(1)'\tREG-5\t2026-11-13\tA failing row.\tcriterion\t\n")
    with open(os.path.join(work, ".loop", "config.json"), "w") as handle:
        handle.write('{"base": "main"}')
    for cmd in (["init", "-q", "-b", "main", "."], ["config", "user.email", "t@example.test"], ["config", "user.name", "t"], ["add", "-A"], ["commit", "-qm", "rows"]):
        subprocess.run(["git"] + cmd, cwd=work, check=True, capture_output=True)
    open(log, "w").close()
    env = dict(os.environ, PATH=shim + os.pathsep + os.environ["PATH"], GH_LOG=log, GH_TOKEN="x", REGRESSION_TARGET="land", GITHUB_REF=ref,
               REGRESSION_RESULTS=os.path.join(work, "res.tsv"), LOOP_PRIVATE_NAMES=os.devnull)
    done = subprocess.run([sys.executable, "-", argument(ref)], input=source, cwd=work, env=env, capture_output=True, text=True, timeout=120)
    return done.returncode, done.stdout + done.stderr, [x.strip() for x in open(log).read().splitlines()]


for ref, writes in (("refs/heads/main", True), ("refs/heads/some-branch", False), ("refs/pull/9/merge", False), ("refs/tags/main", False)):
    code, out, calls = run(ref)
    wrote = [x for x in calls if x.startswith(WRITES)]
    if writes:
        check(any(x.startswith("issue create") for x in wrote), "on %s the failing row's issue is written (writes: %s)" % (ref, wrote[:2]))
    else:
        check(not wrote and "red" in out and code == 1, "on %s the row runs and fails the run but no issue call is made (writes: %s, exit %d)" % (ref, wrote[:2], code))
print("ALL PASS" if not failed else "%d FAILED" % len(failed))
sys.exit(1 if failed else 0)
