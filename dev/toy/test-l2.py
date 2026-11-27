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


def check(ok, text, detail=""):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)
        detail and print("  " + str(detail)[:600].replace("\n", "\n  "))


from lvl_fixture import sha  # noqa: E402


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
    run_env = {"PATH": os.path.join(top, "bin") + ":" + os.environ["PATH"], "HOME": top, "USERPROFILE": top, "FAKE_GH_DIR": top, "TOY_LOG": log,
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


def l2mod():
    sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
    import l2
    return l2


def verdict():
    print("== items 9 and 10: one verdict, with completeness apart from colour")
    # Value: protects=an L2 run is never green after a shard was lost, a row did not run or a write failed; fails_when=a
    #   missing shard, an unrun row, a failed write or a cancelled matrix reads green; why_new=no verdict existed
    l2 = l2mod()
    ok = "# started 1\na\tPASS\nb\tPASS\n# end\n"
    got = lambda *args, **kw: l2.verdict(*args, **kw)
    v = got(["a", "b"], ok, 1, "success")
    check(v["state"] == "GREEN" and v["complete"], "every row passed, every shard closed, the matrix succeeded: GREEN")
    v = got(["a", "b", "c"], ok, 1, "success")
    check(v["state"] == "RED" and v["unfinished"] == ["c"], "a row with no result line is unfinished and the run is RED")
    v = got(["a", "b"], "a\tPASS\nb\tPASS\n", 1, "success")
    check(v["state"] == "INCOMPLETE" and not v["complete"], "a shard file with no closing line makes the run INCOMPLETE, not green")
    check(got(["a", "b"], ok, 1, "cancelled")["state"] == "INCOMPLETE", "a cancelled matrix is INCOMPLETE")
    check(got(["a", "b"], ok + "# gh-failed\n", 1, "success")["state"] == "INCOMPLETE", "a failed issue write makes the run INCOMPLETE")
    check(got(["a", "b"], "", 1, "failure")["state"] == "RED", "no results file at all: every row is unfinished, RED")
    v = got(["a", "b"], "a\tPASS\nb\tSKIPPED\n# unrun b\n# end\n", 1, "success")
    check(v["state"] == "RED" and v["skipped"] == {"b": "out of job time"}, "a row that never started is RED and named with its cause")
    v = got(["a", "b"], "a\tPASS\n# exempt b macOS only\nb\tSKIPPED\n# end\n", 1, "success")
    check(v["state"] == "GREEN" and v["exempt"] == 1 and not v["skipped"], "a by-design skip is exempt and the run stays GREEN")
    v = got(["a", "b"], "a\tPASS\nb\tFAIL\n# end\n", 1, "failure")
    check(v["state"] == "RED" and l2.tally(v) == "L2 RED: ran 1, known 0, exempt 0, skipped 0, failed 1", "a failed row is RED, and the tally line reads as the plan says")
    check(got(["a", "b"], ok + ok, 2, "success")["state"] == "GREEN", "two shards that both closed are complete")
    check(got(["a", "b"], ok, 2, "success")["state"] == "INCOMPLETE", "one shard of two closed is INCOMPLETE")
    cut = "# started 1\na\tPASS\nb\tPASS\n"
    v = got(["a", "b"], ok + cut, 2, "success")
    check(v["state"] == "INCOMPLETE" and not v["unfinished"] and not v["complete"], "a truncated shard file, with every row's line in from the other, is INCOMPLETE")


def covered():
    print("== checks 22 and 23: covered rows in the report")
    # Value: protects=a covered row reads as its worst cover; two rows excused by the record print excepted (record);
    #   fails_when=an excused row makes the run incomplete or a covered row prints nothing
    l2 = l2mod()
    record = "# id\told\tlevel\trisk\tcovers\tseconds\tcmdhash\treason\n" \
             "c1\tcovered\tL1\tnone\tx,y\t\t\tcovers\ne1\tcovered\tL1\tnone\t\t\t\texcepted:o988\nc2\tcovered\tL1\tnone\tz\t\t\tcovers\n"
    states = {"x": "PASS", "y": "FAIL"}
    lines, incomplete = l2.covered_lines(record, states)
    check("L2_COVERED c1 -> FAIL via y" in lines and "excepted (record) e1" in lines, "a covered row reads its worst cover, and an excused row reads excepted (record)")
    check(incomplete == ["c2"], "a covered row whose cover has no result makes the run incomplete, and an excused row does not")
    lines, incomplete = l2.covered_lines(None, states)
    check(incomplete == [], "with no record file nothing is incomplete")


GH2 = """#!/usr/bin/env python3
import json, os, sys
d = os.environ["FAKE_GH_DIR"]; a = sys.argv[1:]
open(d + "/calls.log", "a").write(" ".join(a) + "\\n")
if os.environ.get("FAKE_GH_FAIL") and os.environ["FAKE_GH_FAIL"] in " ".join(a):
    sys.exit(print("HTTP 403: forbidden", file=sys.stderr) or 1)
path = d + "/db.json"
db = json.load(open(path)) if os.path.exists(path) else {"issues": []}
def arg(name):
    return a[a.index(name) + 1] if name in a else ""
def body():
    return open(arg("--body-file")).read() if "--body-file" in a else arg("--body")
labels = [a[i + 1] for i, x in enumerate(a) if x == "--label"]
if a[:2] == ["issue", "list"]:
    print(json.dumps([{"number": i["number"], "body": i["body"]} for i in db["issues"] if i["state"] == "open" and all(l in i["labels"] for l in labels)]))
elif a[:2] == ["issue", "create"]:
    n = len(db["issues"]) + 1
    db["issues"].append({"number": n, "title": arg("--title"), "labels": labels, "body": body(), "comments": [], "state": "open"})
    print("https://example.test/issues/%d" % n)
elif a[:2] in (["issue", "edit"], ["issue", "close"], ["issue", "comment"], ["issue", "view"]):
    i = [x for x in db["issues"] if x["number"] == int(a[2])][0]
    if a[1] == "edit":
        i["title"], i["body"] = arg("--title"), body()
    elif a[1] == "close":
        i["state"] = "closed"
    elif a[1] == "comment":
        i["comments"].append(body())
    else:
        print("\\n".join([i["body"]] + i["comments"]))
json.dump(db, open(path, "w"))
"""
SUMMARY = "      - name: Write one run summary, one table per feature\n"


def summary(top, results, target="L2", matrix="success", cleanup="", fail="", ref="refs/heads/main", routine="true"):
    """Run the yml's summary step as GitHub would, over the shard result files given; returns (rc, output, calls, issues)."""
    text = open(os.path.join(top, ".github", "workflows", "regression.yml")).read()
    part = text.split(SUMMARY, 1)[1].split("\n      - ", 1)[0]
    head, body = part.split("        run: |\n", 1)
    env = dict(re.findall(r"^          ([A-Z_]+): \"?([^\"$\n#]*?)\"?\s*(?:#.*)?$", head, re.M))
    open(os.path.join(top, "sum.sh"), "w").write("\n".join(line[10:] for line in body.split("\n")))
    shards = os.path.join(top, "shards")
    for n, shard in enumerate(results):
        os.makedirs(os.path.join(shards, "results-%d" % n), exist_ok=True)
        open(os.path.join(shards, "results-%d" % n, "regression-results.tsv"), "w").write(shard)
    open(os.path.join(top, "calls.log"), "w").close()
    run_env = {"PATH": os.path.join(top, "bin") + ":" + os.environ["PATH"], "HOME": top, "USERPROFILE": top, "FAKE_GH_DIR": top, "RUNNER_TEMP": top,
               "GITHUB_STEP_SUMMARY": os.path.join(top, "step-summary.md"), "GITHUB_SHA": "abc123", "GITHUB_REF": ref, "FAKE_GH_FAIL": fail,
               "REGRESSION_TARGET": target, "REGRESSION_CLEANUP": cleanup, "MATRIX": matrix, "SHARDS": str(len(results) or 1)}
    run_env.update({k: v for k, v in env.items() if v and k not in run_env})
    done = subprocess.run(["bash", "sum.sh"], cwd=top, capture_output=True, text=True, env=run_env)
    db = os.path.join(top, "db.json")
    return done.returncode, done.stdout + done.stderr, open(os.path.join(top, "calls.log")).read(), json.load(open(db))["issues"] if os.path.exists(db) else []


def shim(top):
    open(os.path.join(top, "bin", "gh"), "w").write(GH2)
    os.chmod(os.path.join(top, "bin", "gh"), 0o755)


def stepcheck():
    print("== the summary step: refusals, the routine, red runs and what it files")
    # Value: protects=done lines 2 and 3 (a short shard is red and named in one issue; a failing row is named in the main-red
    #   goal's issue); fails_when=the step goes green after a lost shard, files twice, or names a row twice
    top = repo(rows=[("a", "land", "true"), ("b", "land", "true"), ("c", "nightly", "true")])
    shim(top)
    start = "# started 1\n"
    code, said, calls, _ = summary(top, [start], target="L3")
    check(code == 1 and said.splitlines()[0].startswith("REFUSED (BAD_TARGET)") and calls == "", "an unknown target: the step's first line is BAD_TARGET, it exits 1 and calls no gh")
    code, said, calls, _ = summary(top, [start], cleanup="true")
    check(code == 1 and "REFUSED (L2_CLEANUP_EXCLUSIVE)" in said.splitlines()[0] and calls == "", "L2 with cleanup refuses and calls no gh")
    empty = repo(rows=[("only", "covered", "true")])
    shim(empty)
    code, said, calls, _ = summary(empty, [start])
    check(code == 1 and "REFUSED (L2_NO_ROWS)" in said.splitlines()[0], "an empty L2 selection is refused as L2_NO_ROWS, never green")
    short = start + "a\tPASS\nb\tSKIPPED\n# unrun b\nc\tSKIPPED\n# unrun c\n# end\n"
    code, said, calls, issues = summary(top, [short])
    check(code == 1 and said.splitlines()[0].startswith("L2 RED:") and "L2_VERDICT abc123 red" in said, "a shard out of job time: the step is red, with the tally first and the verdict line")
    skipped = [i for i in issues if "loop-l2-skipped" in i["body"]]
    check(len(skipped) == 1 and "`b`" in skipped[0]["body"] and "`c`" in skipped[0]["body"] and skipped[0]["title"].endswith("(2)"), "one issue names each skipped row")
    code, said, calls, issues = summary(top, [short])
    check(len([i for i in issues if "loop-l2-skipped" in i["body"]]) == 1, "a second run edits that issue and files no second one")
    check(re.fullmatch(r"L2_VERDICT [0-9a-f]+ (red|incomplete|green)\n", (open(os.path.join(top, "l2-verdict.txt")).read() if os.path.exists(os.path.join(top, "l2-verdict.txt")) else "")) is not None,
          "the published l2-verdict file holds only the one L2_VERDICT line: a sha and a word, no row id or output")
    code, said, calls, issues = summary(top, [start + "a\tPASS\nb\tPASS\nc\tPASS\n# end\n"])
    check(code == 0 and said.splitlines()[0].startswith("L2 GREEN:") and [i["state"] for i in issues if "loop-l2-skipped" in i["body"]] == ["closed"], "a complete green run closes the skipped issue")
    os.path.exists(os.path.join(top, "l2-verdict.txt")) and os.remove(os.path.join(top, "l2-verdict.txt"))
    code, said, calls, issues = summary(top, [short], ref="refs/heads/topic")
    check(code == 1 and "L2_VERDICT" not in said and not os.path.exists(os.path.join(top, "l2-verdict.txt")) and "issue" not in calls, "off main there is no verdict line or file and no issue is written")
    code, said, calls, _ = summary(top, [short], fail="issue")
    check(code == 1 and said.splitlines()[0].startswith("L2 "), "a crashing issue writer cannot stop the summary: the tally is still printed")
    os.makedirs(os.path.join(top, ".loop"), exist_ok=True)
    os.remove(os.path.join(top, "l2-verdict.txt")) if os.path.exists(os.path.join(top, "l2-verdict.txt")) else None
    red = start + "a\tPASS\nb\tFAIL\nc\tPASS\n# end\n"
    top2 = repo(rows=[("a", "land", "true"), ("b", "land", "true"), ("c", "nightly", "true")])
    shim(top2)
    json.dump({"issues": [{"number": 1, "title": "Regression: b", "labels": ["regression", "l2-red"], "body": "x", "comments": [], "state": "open"}]}, open(os.path.join(top2, "db.json"), "w"))
    before = sh(top2, "git", "log", "--oneline").stdout
    for _ in range(2):
        code, said, calls, issues = summary(top2, [red])
    goal = [i for i in issues if "loop-l2-main-red" in i["body"]]
    check(code == 1 and len(goal) == 1 and goal[0]["comments"].count("L2 red: #1") == 1 and goal[0]["labels"] == [], "a failing row is named once in an unlabelled failing-rows issue, however often the run repeats")
    check(len(goal) == 1 and sh(top2, "git", "log", "--oneline").stdout == before and "revert" not in open(os.path.join(top2, ".github", "workflows", "regression.yml")).read().replace("git revert", "git revert", 0).lower().split("# written")[0], "the run adds no commit to the repository")


def second():
    print("== item 15: a silent failing row's second run takes the job time that is left")
    # Value: protects=the loud rerun of a silent failing row never outlives the job; fails_when=it gets the row's whole limit
    #   with no time left, or runs at all; why_new=the rerun used the row's limit alone
    import time
    l2 = l2mod()
    l2.time = time
    seen = []
    again = lambda row_s, job_s, ago: l2.l2_again(lambda c, limit: seen.append(limit) or (1, "loud"), row_s, job_s, time.time() - ago, 9)
    check(again(900, 100, 0)("c") == (1, "loud") and 99 <= seen[-1] <= 100, "with 100 s of job time left the second run gets 100 s, not the row's 900")
    check(again(30, 100, 0)("c") == (1, "loud") and seen[-1] == 30, "with more time than the row's limit it gets the row's limit")
    seen.clear()
    check(again(900, 100, 150)("c") == (9, "") and seen == [], "with no time left the second run is not run, and the issue gets the exit code and no output")


def marker():
    print("== review round 1: markers only count at the top of an issue, and a number is named by its whole digits")
    # Value: protects=a failing row's output cannot make the writer edit or close its issue, and #1 is named even when #12 is;
    #   fails_when=a marker inside a body or a longer issue number is taken for the real one
    top = repo(rows=[("a", "land", "true"), ("b", "land", "true"), ("c", "nightly", "true")])
    shim(top)
    start = "# started 1\n"
    red = start + "a\tPASS\nb\tFAIL\nc\tPASS\n# end\n"
    quote = "<!-- loop-regression b placed= -->\nThe row `b` fails.\n```\nL2 failing rows <!-- loop-l2-skipped --> <!-- loop-l2-main-red -->\n```\n"
    db = {"issues": [{"number": 1, "title": "Regression: b", "labels": ["regression", "l2-red"], "body": quote, "comments": [], "state": "open"},
                     {"number": 2, "title": "Regression: L2 failing rows", "labels": [], "body": "<!-- loop-l2-main-red -->\nx", "comments": ["L2 red: #12"], "state": "open"}]}
    json.dump(db, open(os.path.join(top, "db.json"), "w"))
    code, said, calls, issues = summary(top, [red])
    one = [i for i in issues if i["number"] == 1][0]
    check(one["title"] == "Regression: b" and one["state"] == "open" and one["body"] == quote, "a row's own issue that quotes a marker is never edited or closed")
    two = [i for i in issues if i["number"] == 2][0]
    check(two["comments"].count("L2 red: #1") == 1, "#1 is named in the failing-rows issue although #12 already is")
    code, said, calls, issues = summary(top, [start + "a\tPASS\nb\tPASS\nc\tPASS\n# end\n"])
    check([i["state"] for i in issues if i["number"] == 1] == ["open"], "a complete green run does not close an unrelated issue that quotes the skipped-rows marker")


def usage():
    print("== l2.py run alone, as the package check runs it: no arguments and --help print the usage")
    # Value: protects=the package's run-alone check of every script; fails_when=l2.py stops with a traceback and a non-zero
    #   exit when it gets no argument or --help (the IndexError of 0118e9595)
    import shutil
    scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
    lone = tempfile.mkdtemp(prefix="test-l2-lone.")
    shutil.copytree(scripts, os.path.join(lone, "scripts"))
    for args in ([], ["--help"]):
        done = subprocess.run([sys.executable, "-E", "-s", os.path.join(lone, "scripts", "l2.py")] + args, cwd=lone, capture_output=True, text=True, timeout=60)
        check(done.returncode == 0 and "l2.py check TARGET CLEANUP" in done.stdout and "Traceback" not in done.stderr, "l2.py run alone with %s prints its usage and exits 0" % (args or "no argument"))


def guard():
    print("== DEL-10: l2.py's gh calls carry their own no-prompt env, and importing it changes nothing")
    # Value: protects=the summary job's gh calls never wait on a prompt, with the guard on the call and not process-wide (TD2266(4));
    #   fails_when=the gh call runs with the caller's env, or importing l2 rewrites os.environ
    scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
    env = {"PATH": os.environ["PATH"], "HOME": tempfile.mkdtemp(prefix="test-l2-home."), "USERPROFILE": "x", "GH_PROMPT_DISABLED": "0", "GIT_EDITOR": "vim"}
    code = ("import sys, os, subprocess; sys.path.insert(0, %r); import l2; seen = []\n"
            "subprocess.run = lambda *a, **k: seen.append(k.get('env')) or subprocess.CompletedProcess(a, 0, '', '')\n"
            "l2.gh('issue', 'list'); g = seen[0] or {}\n"
            "print(os.environ['GIT_EDITOR'], os.environ['GH_PROMPT_DISABLED'], g.get('GIT_TERMINAL_PROMPT'), g.get('GH_PROMPT_DISABLED'), g.get('GIT_EDITOR'), g.get('GIT_ASKPASS'), g.get('SSH_ASKPASS'))") % scripts
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    check(done.stdout.split()[:2] == ["vim", "0"], "importing l2 leaves the process's own GIT_EDITOR and GH_PROMPT_DISABLED alone")
    check(done.stdout.split()[2:] == ["0", "1", "true", "true", "true"], "the gh call's own env sets GIT_TERMINAL_PROMPT=0, GH_PROMPT_DISABLED=1, GIT_EDITOR, GIT_ASKPASS and SSH_ASKPASS")


def draftearly():
    print("== R6: a refused target still names the drafts")
    # Value: protects=the not-run lines come before any early exit; fails_when=a bad target exits before them
    top = repo(rows=[("l1", "land", 'echo l1 >> "$TOY_LOG"'), ("drf", "draft", 'echo drf >> "$TOY_LOG"')])
    code, said, results, calls = step(top, "no-such-target")
    check(code != 0 and "BAD_TARGET" in said and "not run: draft drf" in said.splitlines(), "a bad target is refused and the draft is named first")


def l2_level_pick_typo():
    l2 = l2mod()
    folder = tempfile.mkdtemp(prefix="test-l2-typo.")
    os.makedirs(os.path.join(folder, ".loop"))
    open(os.path.join(folder, ".loop", "regression-relevel.tsv"), "w").write("")
    cwd = os.getcwd()
    os.chdir(folder)
    try:
        l2.level_pick.__defaults__[0].clear()
        return [w for w in ("Draft", "lnd", "Land", "") if l2.level_pick("L1", ["x", w])]
    finally:
        os.chdir(cwd)


def levelrun():
    print("== R11: the generated runner selects L0 and L1 as regression.py run <level> does, and only when armed")
    # Value: protects=the scheduled runner and the local runner pick the same rows for L0, L1 and L2, a missing record fails loudly, and an
    #   unarmed table is as before; fails_when=the runner has no L0 or L1, the sets differ (security, private, no entry, draft, covered, a row
    #   named like a level), or an unarmed repository takes the new targets
    sys.path.insert(0, os.path.join(here))
    from lvl_fixture import Repo, entry, row
    risks = ["label\tsecurity\tsecurity\tfixture label", "label\tprivate\tprivate\tfixture label"]
    cmd = lambda key: 'echo %s >> "$TOY_LOG"' % key
    spec = [("lvl-armed", "land", "L1", "none"), ("l0row", "land", "L0", "none"), ("l1row", "land", "L1", "none"), ("l2row", "nightly", "L2", "none"),
            ("secrow", "nightly", "L1", "security"), ("privrow", "land", "L1", "private"), ("L1", "land", "L2", "none"),
            ("drf", "draft", "L1", "none"), ("cov", "covered", "L1", "none")]
    rows = [row(k, level=old, command=cmd(k)) for k, old, lv, rk in spec]
    ents = [entry(k, old=old, level=lv, risk=rk, covers="l1row" if old == "covered" else "", seconds="1.0" if lv == "L0" else "",
                  cmdhash=sha(cmd(k)) if lv == "L0" else "", reason="time:1.0" if lv == "L0" else ("risk:" + rk if rk != "none" else "default")) for k, old, lv, rk in spec]
    for mark, nine in ((True, False), (True, True), (False, False)):
        repo = Repo(rows, ents, risks)
        if nine:  # a record written by this goal's tools: a ninth cell, the state; level and risk stay cells 3 and 4
            text = repo.read(".loop/regression-relevel.tsv")
            repo.write(".loop/regression-relevel.tsv", "".join(l + ("\tdraft" if l.startswith("drf\t") else "\t") + "\n" for l in text.splitlines()))
        mark and repo.write(".github/workflows/regression-pr.yml", "# Written by workflow-regression\n")
        repo.write(".loop/config.json", "{}")
        repo.commit()
        sh(repo.path, sys.executable, reg, "workflow", "--visibility", "public", env=repo.env)
        os.makedirs(os.path.join(repo.path, "bin"), exist_ok=True)
        open(os.path.join(repo.path, "bin", "gh"), "w").write(GH)
        os.chmod(os.path.join(repo.path, "bin", "gh"), 0o755)
        for level in ("L0", "L1", "L2"):
            log = os.path.join(repo.path, "local.log")
            open(log, "w").close()
            done, said = repo.run("run", level, TOY_LOG=log)
            local = sorted(open(log).read().split())
            code, out, results, calls = step(repo.path, level)
            ran = sorted(open(os.path.join(repo.path, "ran.log")).read().split())
            if mark:
                check(code == 0 and ran == local and (level == "L2" or local), "armed, %s-cell record: the runner's %s rows equal regression.py run %s: %s" % ("nine" if nine else "eight", level, level, local), (code, ran, local, out[-300:]))
            elif level == "L0":
                check(code != 0 and "BAD_TARGET" in out and not ran, "unarmed: the runner refuses L0 as it did before", (code, out[-300:]))
            elif level == "L1":
                check(code == 0 and ran == ["L1"], "unarmed: L1 is only the row called L1, as it was before", (code, ran, out[-300:]))
        mark and check(sorted(open(os.path.join(repo.path, "ran.log")).read().split()) != [], "control: the L2 run ran rows")
        repo.close()
    check(not l2_level_pick_typo(), "the runner's L0/L1 pick runs only land and nightly rows: a typo or capitalised word never runs (review round 1)")
    # a row with no record entry cannot be in a valid table (every run refuses LEVELS_NO_ENTRY), so it is compared as functions: l2.level_pick against
    # completion.at_level on one record that lacks the row
    scripts = os.path.join(root, "skills", "workflow-regression", "scripts")
    sys.path.insert(0, scripts)
    import completion, l2
    table = [["noent", "land"], ["recd", "land"], ["sec", "nightly"]]
    record = {"recd": ("L2", "none"), "sec": ("L2", "security")}
    cwd = os.getcwd()
    folder = tempfile.mkdtemp(prefix="test-l2-fn.")
    os.makedirs(os.path.join(folder, ".loop"))
    open(os.path.join(folder, ".loop", "regression-relevel.tsv"), "w").write("".join("\t".join([k, "x", lv, rk, "", "", "", "default", ""]) + "\n" for k, (lv, rk) in record.items()))
    os.chdir(folder)
    try:
        for level in ("L0", "L1"):
            l2.level_pick.__defaults__[0].clear()
            want = sorted(r["id"] for r in completion.at_level([{"id": k, "level": lv} for k, lv in table], level, record))
            got = sorted(r[0] for r in table if l2.level_pick(level, r))
            check(got == want, "%s: l2.level_pick equals completion.at_level on a record with no entry for one row: %s" % (level, want), (got, want))
    finally:
        os.chdir(cwd)
    repo = Repo(rows, ents, risks)
    repo.write(".github/workflows/regression-pr.yml", "# Written by workflow-regression\n")
    repo.write(".loop/config.json", "{}")
    repo.commit()
    sh(repo.path, sys.executable, reg, "workflow", "--visibility", "public", env=repo.env)
    os.makedirs(os.path.join(repo.path, "bin"), exist_ok=True)
    open(os.path.join(repo.path, "bin", "gh"), "w").write(GH)
    os.chmod(os.path.join(repo.path, "bin", "gh"), 0o755)
    os.remove(os.path.join(repo.path, ".loop", "regression-relevel.tsv"))
    code, out, results, calls = step(repo.path, "L1")
    check(code != 0 and "NO_RECORD" in out, "armed but the committed levels record is missing: the runner refuses loudly (NO_RECORD) and selects nothing quietly", (code, out[-300:]))
    repo.close()


def order():
    print("== TD2358: one worst-state order, and a covered row asked for by id is refused")
    # Value: protects=the summary job and the pages rank states by the same order (FLAKY included, an unknown state worst, no traceback), and a
    #   covered row targeted by its id never runs; fails_when=the two orders differ, ORDER.index raises, or the runner runs a covered row
    l2 = l2mod()
    sys.path.insert(0, os.path.join(root, "skills", "workflow-regression", "scripts"))
    import level_words
    states = ("FAIL", "FLAKY", "no result", "draft", "SKIPPED", "KNOWN", "EXEMPT", "excepted", "PASS")
    check(tuple(l2.ORDER) == states and tuple(level_words.ORDER) == states, "one order, worst first, in l2.py and level_words.py", (l2.ORDER, level_words.ORDER))
    yml = open(os.path.join(root, ".github", "workflows", "regression.yml"), encoding="utf-8").read()
    copy = re.search(r"^\s+ORDER = (\(.*?\))", yml, re.M)
    check(copy and tuple(eval(copy.group(1))) == states, "the order in regression.yml's summary job is the same tuple", copy and copy.group(1))
    check(l2.rank("FLAKY") < l2.rank("PASS") and l2.rank("FAIL") < l2.rank("FLAKY"), "a FLAKY cover ranks worse than PASS and better than FAIL")
    check(all(level_words.worst([s, "PASS"]) == (s if s != "PASS" else "PASS") for s in states), "level_words.worst gives the same answer for every state against PASS")
    record = "c1\tcovered\tL1\tnone\tx,y\t\t\tcovers\n"
    for s in states:
        lines, incomplete = l2.covered_lines(record, {"x": s, "y": "PASS"})
        check(("L2_COVERED c1 -> %s via x" % s) in lines or s == "PASS", "the summary ranks %s as worst against PASS" % s, lines)
    for other in ("PASS", "FAIL"):
        try:
            lines, incomplete = l2.covered_lines(record, {"x": "weird", "y": other})
            check("L2_COVERED c1 -> weird via x" in lines, "an unknown state next to %s ranks worst and is shown, with no traceback" % other, lines)
            check(incomplete == ["c1"], "an unknown state next to %s is NOT green: the cover counts as incomplete (the verdict cannot be GREEN)" % other, incomplete)
        except ValueError as error:
            check(False, "an unknown state next to %s ranks worst, with no traceback" % other, error)


def coveredid():
    print("== TD2358: a covered row targeted by its id is refused and runs nothing")
    # Value: protects=R2: a covered row never makes a PASS of its own; fails_when=the runner runs a covered row's command by id
    top = repo(rows=[("l1", "land", 'echo l1 >> "$TOY_LOG"'), ("cov", "covered", 'echo cov >> "$TOY_LOG"')],
               files={"regression-relevel.tsv": "l1\tland\tL1\tnone\t\t\t\tdefault\ncov\tcovered\tL1\tnone\tl1\t\t\tcovers\n"})
    code, said, results, calls = step(top, "cov")
    ran = open(os.path.join(top, "ran.log")).read().split()
    check(code != 0 and "REFUSED (COVERED_ROW)" in said and "covered by l1; run those" in said and ran == [], "target = a covered row's id is refused: covered by l1; run those, and nothing ran", (code, said[-300:], ran))
    code, said, results, calls = step(top, "l1")
    check(code == 0 and "l1" in open(os.path.join(top, "ran.log")).read().split(), "a plain row's id still runs", (code, said[-200:]))
    os.remove(os.path.join(top, ".loop", "regression-relevel.tsv"))
    open(os.path.join(top, "ran.log"), "w").close()
    code, said, results, calls = step(top, "cov")
    ran = open(os.path.join(top, "ran.log")).read().split()
    check(code != 0 and "REFUSED (COVERED_ROW)" in said and "(levels record unreadable)" in said and ran == [],
          "a covered row asked for by id is refused even when the levels record is missing, and nothing ran (fail closed)", (code, said[-300:], ran))


def draftrun():
    print("== R6: the scheduled runner never runs a draft, even asked for by its row id")
    # Value: protects=a draft's command never runs in the generated workflow and the log says so; fails_when=the runner runs a draft named by
    #   its id, or a run says nothing about it
    top = repo(rows=[("l1", "land", 'echo l1 >> "$TOY_LOG"'), ("drf", "draft", 'echo drf >> "$TOY_LOG"')])
    for target in ("drf", "nightly", "L2"):
        code, said, results, calls = step(top, target)
        ran = open(os.path.join(top, "ran.log")).read().split()
        check("drf" not in ran, "target %s: the draft's command did not run" % target)
        check([l for l in said.splitlines() if "drf" in l] == ["not run: draft drf"], "target %s: the log names the draft once, as not run: draft drf" % target)


cases = {"target": target, "label": label, "pick": pick, "state": state, "jobtime": jobtime, "concurrency": concurrency, "verdict": verdict, "covered": covered, "step": stepcheck, "second": second, "marker": marker, "usage": usage, "guard": guard, "draftrun": draftrun, "draftearly": draftearly, "levelrun": levelrun, "order": order, "coveredid": coveredid}
for name in (sys.argv[1:] or list(cases)):
    cases[name]()
print("%d failed" % len(failed))
print("ALL PASS" if not failed else "FAILED")
sys.exit(1 if failed else 0)
