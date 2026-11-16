#!/usr/bin/env python3
# windows: ok
# reads: .github/workflows/regression.yml skills/workflow-regression/scripts/actions.py skills/workflow-regression/scripts/runs.py
"""CI-summary (#4516): the regression job's summary names each failing row and keeps its last 20 lines of output; a passing
row's output stays out of it. Runs the committed workflow's own block over a toy repo, one failing row and one passing row."""
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
text = open(os.path.join(root, ".github", "workflows", "regression.yml"), encoding="utf-8").read().replace("\r\n", "\n")
block = re.search(r"python3 - (?:--live )?<<'PY'\n(.*?)\n\s+PY\n", text, re.S).group(1)
block = "\n".join(line[10:] for line in block.split("\n"))
failed = []


def check(ok, said):
    print(("PASS: " if ok else "FAIL: ") + said)
    if not ok:
        failed.append(said)


with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
    subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
    os.makedirs(os.path.join(tmp, ".loop"))
    long_out = "python3 -c \"print(chr(10).join('line%d' % i for i in range(1, 31))); raise SystemExit(1)\""
    rows = ["bad\tnightly\t%s\tX-1" % long_out, "quiet\tnightly\techo hidden | grep -q nomatch\tX-2", "good\tnightly\techo passoutput\tX-3"]
    rows.append("skipped	nightly	python3 -c \"import os; open(os.environ['TOY_SKIP_FILE'], 'w').write('x'); raise SystemExit(77)\" | grep -q nomatch	X-4")
    with open(os.path.join(tmp, ".loop", "regression.tsv"), "w", newline="\n") as handle:
        handle.write("# id\tlevel\tcommand\n" + "\n".join(rows) + "\n")
    open(os.path.join(tmp, ".loop", "regression-known.tsv"), "w").close()
    summary = os.path.join(tmp, "summary.md")
    env = {k: v for k, v in os.environ.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN")}
    env.update(GITHUB_STEP_SUMMARY=summary, REGRESSION_RESULTS=os.path.join(tmp, "results.tsv"), HOME=home, USERPROFILE=home)
    open(os.path.join(tmp, "ci-block.py"), "w").write(block)
    subprocess.run([sys.executable, "ci-block.py"], cwd=tmp, env=env, capture_output=True, text=True, timeout=120)
    said = open(summary).read() if os.path.exists(summary) else ""
    check("#### FAIL bad" in said and "line30" in said and "line11" in said, "the failing row is named with its last lines")
    check("line10\n" not in said and "line1\n" not in said, "only the last 20 lines are kept")
    check("#### FAIL quiet" in said and "hidden" in said, "a failing row that hides its output with grep -q shows it")
    results = open(env["REGRESSION_RESULTS"]).read()
    check("skipped	SKIPPED" in results and "FAIL skipped" not in said, "a row whose toy wrote TOY_SKIP_FILE behind a pipe is SKIPPED, not FAIL")
    check("good" not in said and "passoutput" not in said, "the passing row's name and output stay out")
sys.exit(1 if failed else 0)
