#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/actions.py skills/workflow-regression/scripts/regression.py skills/workflow-regression/scripts/tests.py
"""G3 (v110-lvl-l2): L2 is the scheduled run's default target; a failed L2 label write is reported, never swallowed.

Runs the written regression.yml's "Run the rows" step as GitHub would (bash, its literal env values) in a temporary git
folder with a stand-in gh on PATH. No network, no model. usage: test-l2.py [target|label]  (no argument: all)"""
import json
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
reg = os.path.join(root, "skills", "workflow-regression", "scripts", "regression.py")
failed = []
STEP = "      - name: Run the rows, and keep one issue per failing row\n"
GH = """#!/bin/bash
echo "$*" >> "$FAKE_GH_DIR/calls.log"
[ -n "${FAKE_GH_FAIL:-}" ] && [[ "$*" == *"$FAKE_GH_FAIL"* ]] && { echo "HTTP 403: forbidden" >&2; exit 1; }
[ "$1" = api ] && exit 0
case "$1 $2" in "issue create") echo "https://example.test/issues/1";; esac
exit 0
"""


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def sh(cwd, *cmd, env=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def repo(levels=None, rows=None, files=None):
    """A temporary git folder with one passing land row, one passing nightly row and one failing nightly row."""
    top = tempfile.mkdtemp(prefix="test-l2.")
    sh(top, "git", "init", "-q", "-b", "main")
    os.makedirs(os.path.join(top, ".loop"))
    head = "# id\tlevel\tcommand\tgoal\tseen_red\tdescription\tcategory\tlink\n"
    rows = rows or [("l1", "land", 'echo l1 >> "$TOY_LOG"'), ("n1", "nightly", 'echo n1 >> "$TOY_LOG"'),
                    ("bad", "nightly", 'echo bad >> "$TOY_LOG"; echo boom; exit 1')]
    for name, text in (files or {}).items():
        open(os.path.join(top, ".loop", name), "w").write(text)
    open(os.path.join(top, ".loop", "regression.tsv"), "w").write(head + "".join(
        "%s\t%s\t%s\t-\t2026-01-01\tA row.\tcriterion\t\n" % row for row in rows))
    open(os.path.join(top, ".loop", "config.json"), "w").write(json.dumps({"ci_levels": levels} if levels else {}))
    os.makedirs(os.path.join(top, "bin"))
    open(os.path.join(top, "bin", "gh"), "w").write(GH)
    os.chmod(os.path.join(top, "bin", "gh"), 0o755)
    sh(top, "python3", reg, "workflow", "--visibility", "public")
    return top


def step(top, target, fail="", live=False, extra=None):
    """Run the yml's run step; returns (exit status, output, results file text, gh calls)."""
    text = open(os.path.join(top, ".github", "workflows", "regression.yml")).read()
    part = text.split(STEP, 1)[1].split("\n      - ", 1)[0]
    head, body = part.split("        run: |\n", 1)
    env = dict(re.findall(r"^          ([A-Z_]+): \"?([^\"$\n#]*?)\"?\s*(?:#.*)?$", head, re.M))
    open(os.path.join(top, "step.sh"), "w").write("\n".join(line[10:] for line in body.split("\n")))
    calls, results, log = (os.path.join(top, n) for n in ("calls.log", "results.tsv", "ran.log"))
    for path in (calls, results, log):
        open(path, "w").close()
    run_env = {"PATH": os.path.join(top, "bin") + ":" + os.environ["PATH"], "HOME": top, "FAKE_GH_DIR": top, "TOY_LOG": log,
               "REGRESSION_RESULTS": results, "SUITE_TIME_FILE": os.path.join(top, "suite-time.tsv"), "REGRESSION_TARGET": target,
               "FAKE_GH_FAIL": fail, "L": "--live" if live else ""}
    run_env.update({k: v for k, v in env.items() if v and k not in run_env})
    run_env.update(extra or {})
    done = subprocess.run(["bash", "step.sh"] + (["--live"] if live else []), cwd=top, capture_output=True, text=True, env=run_env)
    return done.returncode, done.stdout + done.stderr, open(results).read(), open(calls).read()


def target():
    print("== B7: the template, the toy and the settings agree on the default target")
    # Value: protects=the schedule's default target is L2 for ci_levels nightly and unchanged for land (item 1, B7);
    #   fails_when=the written yml, the runner or the setting name a different default; why_new=L2 did not exist
    top = repo()
    yml = open(os.path.join(top, ".github", "workflows", "regression.yml")).read()
    want = "REGRESSION_TARGET: ${{ inputs.target || (inputs.cleanup && 'nightly' || 'L2') }}"
    check(want in yml, "with ci_levels nightly the written target expression defaults to L2, and to nightly for a cleanup")
    code, said, results, _ = step(top, "L2")
    check(code == 1 and "REFUSED" not in said and all(("PASS %s" % row) in said for row in ("l1", "n1")),
          "target L2 is accepted and runs every land and nightly row (rc=%s)" % code)
    check(os.path.exists(os.path.join(top, "suite-time.tsv")) and "SUITE_TIME" in said, "a run at L2 records the suite time")
    code, said, _, _ = step(top, "L3")
    check(code == 1 and "use land, nightly, L2 or a row id" in said, "an unknown target lists L2 among the targets")
    top = repo("land")
    yml = open(os.path.join(top, ".github", "workflows", "regression.yml")).read()
    check("REGRESSION_TARGET: ${{ inputs.target }}\n" in yml and "'L2'" not in yml, "with ci_levels land the target stays the dispatch input")


def label():
    print("== R5: a failed label write is reported, never swallowed")
    # Value: protects=a failing L2 row whose l2-red label could not be set is still reported (item 14, R5);
    #   fails_when=the failure is printed and forgotten, so the run reads complete; why_new=l2-red is new
    top = repo()
    code, said, results, calls = step(top, "L2", fail="l2-red", live=True)
    check("# gh-failed" in results, "a label that cannot be set records a gh-failed line in the results")
    check(code == 1 and "FAILED label l2-red" in said, "the failed label write is reported in the log")
    creates = [line for line in calls.splitlines() if line.startswith("issue create")]
    check(len(creates) == 2 and "l2-red" in creates[0] and "l2-red" not in creates[1],
          "the issue is still filed, without the l2-red label")
    code, said, results, calls = step(top, "L2", live=True)
    check("# gh-failed" not in results and "--label l2-red" in calls, "with the label writable it is set on a new issue and no failure is recorded")


def pick():
    print("== check 22: covered rows are not counted as run when the level picked is L2")
    # Value: protects=L2 means every land and nightly row (item 1, TD2224); fails_when=a typed `run L2` also selects a covered
    #   row by its recorded level; why_new=G2's pick takes every row recorded L0, L1 or L2
    sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
    import completion
    rows = [{"id": name, "level": level} for name, level in (("a", "land"), ("b", "nightly"), ("c", "covered"))]
    record = {"a": ("L1", "none"), "b": ("L2", "none"), "c": ("L1", "none")}
    check([row["id"] for row in completion.pick(rows, "L2", record)] == ["a", "b"], "L2 picks the land and nightly rows and not the covered one")
    check([row["id"] for row in completion.pick(rows, "L1", record)] == ["a", "c"], "L1 still picks by the recorded stage")


def state():
    print("== item 7: what counts as run at L2")
    # Value: protects=a by-design skip counts as run and is shown apart; any other skip is named; a known row is KNOWN;
    #   fails_when=a skip-list row files an issue or reads as a failure, or an unlisted skip reads as run
    rows = [("ok", "land", "true"), ("des", "land", "exit 77"), ("both", "land", "exit 77"), ("nostart", "nightly", "echo 'pnpm: command not found'; exit 127"),
            ("other", "nightly", "exit 77"), ("kn", "nightly", "echo nope; exit 1")]
    files = {"regression-skips.tsv": "# id\treason\tflag\ndes\tmacOS only\t\nboth\tby design\t\nnostart\tno pnpm here\tnotrun\n",
             "regression-known.tsv": "both\tknown\nkn\tknown\n"}
    top = repo(rows=rows, files=files)
    code, said, results, calls = step(top, "L2", live=True)
    check(code == 0 and "SKIPPED des (macOS only)" in said and "# exempt des macOS only" in results, "a listed row that exits 77 is SKIPPED and exempt, and the shard stays green")
    check("# exempt both by design" in results and "KNOWN both" not in said, "a row on both lists is exempt, not known")
    check("# exempt nostart no pnpm here" in results, "a notrun row whose tool is missing is exempt")
    check("# skipped other cannot run here" in results and "SKIPPED other (cannot run here)" in said, "an unlisted row that exits 77 is a named skip, not run")
    check("KNOWN kn" in said and "issue create" not in calls, "a known failing row is KNOWN and files no issue")


def jobtime():
    print("== items 6 and 8: a row that never started is not run")
    # Value: protects=a shard out of job time names every unrun row, known and listed ones included; fails_when=a row that
    #   never started reads as run or exempt
    rows = [("a", "land", "true"), ("kn", "nightly", "exit 1"), ("des", "nightly", "exit 77")]
    files = {"regression-skips.tsv": "# id\treason\tflag\ndes\tmacOS only\t\n", "regression-known.tsv": "kn\tknown\n"}
    top = repo(rows=rows, files=files)
    code, said, results, _ = step(top, "L2", extra={"REGRESSION_JOB_SECONDS": "10"})
    ids = ("a", "kn", "des")
    check(all("SKIPPED %s (out of job time)" % one in said for one in ids), "each row prints SKIPPED with the cause out of job time")
    check(all("# unrun %s" % one in results for one in ids) and not any("# exempt" in line for line in results.splitlines()), "each is written as unrun, and none as exempt")
    check(code == 0, "the shard itself stays green; the summary turns the run red")


def concurrency():
    print("== item 16 (GRD-7): one run writes issues at a time on main")
    # Value: protects=main never cancels a running L2 run; fails_when=cancel-in-progress is still true on main
    top = repo()
    yml = open(os.path.join(top, ".github", "workflows", "regression.yml")).read()
    check("group: regression-${{ github.ref }}" in yml and "cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}  # GRD-7" in yml,
          "the group stays per ref and only runs off main are cancelled")


cases = {"target": target, "label": label, "pick": pick, "state": state, "jobtime": jobtime, "concurrency": concurrency}
for name in (sys.argv[1:] or list(cases)):
    cases[name]()
print("%d failed" % len(failed))
print("ALL PASS" if not failed else "FAILED")
sys.exit(1 if failed else 0)
