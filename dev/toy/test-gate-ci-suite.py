#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-release/scripts/review.py docs/wiki/Release.md
"""gate-ci-suite (REL-3, owner o191): `review.py gate vX --suite-from RUN` reads the full suite from a GitHub Actions run of the
regression workflow instead of running it. It takes only a run on the gate ref that completed, with every shard reported, nothing
UNRUN and every land or nightly row logged; any other run refuses "suite run does not cover the candidate". Rows that are not PASS
still refuse without a waiver, and the run id goes in loop/gate/vX.json.

Builds a throwaway repo; gh is stood in for with fixture logs shaped like the real CI log (no network). usage: test-gate-ci-suite.py"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-release", "scripts"))
for key in ("AUTHOR", "COMMITTER"):
    os.environ.setdefault("GIT_%s_NAME" % key, "t")
    os.environ.setdefault("GIT_%s_EMAIL" % key, "t@t")
fails = 0


def check(name, ok, extra=""):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok else 1


def git(*args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false"] + list(args),
                          cwd=repo, capture_output=True, text=True)


tmp = tempfile.mkdtemp(prefix="gate-ci-suite-")
origin, repo = os.path.join(tmp, "origin.git"), os.path.join(tmp, "repo")
subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], capture_output=True)
subprocess.run(["git", "clone", "-q", origin, repo], capture_output=True)
os.makedirs(os.path.join(repo, ".loop", "goals"))
os.makedirs(os.path.join(repo, "docs", "wiki"))
TAB = chr(9)
ROWS = [("a", "land"), ("broken-row", "nightly"), ("stale-row", "nightly"), ("skipped-row", "land"), ("later-row", "draft"), ("done-row", "covered")]
open(os.path.join(repo, ".loop", "config.json"), "w").write('{"auto_merge": true, "base": "main"}\n')
open(os.path.join(repo, ".loop", "docs.tsv"), "w").write("Page" + TAB + "foo.txt\n")
open(os.path.join(repo, ".loop", "regression.tsv"), "w").write("# id" + TAB + "level" + TAB + "command\n" + "".join(k + TAB + v + TAB + "true\n" for k, v in ROWS))
open(os.path.join(repo, "docs", "wiki", "Page.md"), "w").write("## Requirements\n\n- PG-1: **Reviewed 2026-11-01** one\n  - a\n")
open(os.path.join(repo, "foo.txt"), "w").write("a\n")
git("add", "-A"); git("commit", "-q", "-m", "the candidate"); git("push", "-q", "origin", "main")
sha = git("rev-parse", "HEAD").stdout.strip()
common = os.path.abspath(os.path.join(repo, git("rev-parse", "--git-common-dir").stdout.strip()))
os.makedirs(os.path.join(common, "loop"), exist_ok=True)

import release  # noqa: E402
import review  # noqa: E402

SHARDS = "SHARDS 8 of 8 reported. UNRUN 0 (rows skipped for out of job time)."
ran = []
review.run_in = lambda work, script, *args: (ran.append(script), "HEALTH: green")[1]
release.docs_trouble = lambda *a, **k: []


def log(rows, summary=SHARDS):
    """A CI log: each row's result line, a code echo that must not count, and the summary job's shard line."""
    stamp = "2026-11-18T17:46:09.0895112Z "
    body = ["regression (%d)%sUNKNOWN STEP%s%s%s %s" % (n % 8, TAB, TAB, stamp, state, row) for n, (state, row) in enumerate(rows)]
    body.append("regression (0)%sUNKNOWN STEP%s%s    print(state, row[0])" % (TAB, TAB, stamp))
    body.append("summary%sUNKNOWN STEP%s%s%s" % (TAB, TAB, stamp, summary))
    return "\n".join(body) + "\n"


GOOD = [("PASS", "a"), ("PASS", "broken-row"), ("PASS", "stale-row"), ("SKIPPED", "skipped-row")]
RUNS = {}  # run id -> (head sha, status, log)
real_run = subprocess.run


def fake_run(args, *a, **k):
    if args and args[0] == "gh":
        if args[1:3] == ["issue", "list"]:
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[1:3] == ["run", "view"] and args[3] in RUNS:
            head, status, text = RUNS[args[3]]
            return subprocess.CompletedProcess(args, 0, json.dumps({"headSha": head, "status": status}) if "--json" in args else text, "")
        return subprocess.CompletedProcess(args, 1, "", "not found")
    return real_run(args, *a, **k)


def call(*argv):
    out, old = io.StringIO(), os.getcwd()
    os.chdir(repo)
    sys.argv = ["x"] + list(argv)
    subprocess.run = fake_run
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = review.main()
            except SystemExit as stop:
                code = stop.code
                print(code)
    finally:
        subprocess.run = real_run
        os.chdir(old)
    return code, out.getvalue()


def gate(run, *more, cmd="gate"):
    return call(cmd, "v2", "--ref", sha, "--suite-from", run, *more)


def suite_lines(said):
    return sorted(l for l in said.splitlines() if "(suite):" in l)


def waive(*ids):
    open(os.path.join(common, "loop", "owner-words.tsv"), "w").write(TAB.join(("o9", "t", "operation", "waive " + " ".join(ids) + ", issue 9", " ".join(ids))) + "\n")
    open(os.path.join(common, "loop", "release-waivers.tsv"), "w").write("".join(TAB.join(("red", i, "#9", "o9")) + "\n" for i in ids))


RUNS["100"] = (sha, "completed", log(GOOD))
code, said = gate("100")
check("a completed run on the candidate, every row PASS or skipped, passes the gate", code == 0 and "GATE PASS v2.0" in said, said)
check("a draft or covered row missing from the log does not count against the run", "unlogged" not in said, said)
check("the local suite is not run when --suite-from is given", not any("regression" in s for s in ran), str(ran))
check("the run id is recorded in loop/gate/v2.json", json.load(open(os.path.join(common, "loop", "gate", "v2.json"))).get("suite_run") == "100")

RUNS["101"] = (sha, "completed", log([("PASS", "a"), ("FAIL", "broken-row"), ("KNOWN", "stale-row"), ("SKIPPED", "skipped-row")]))
code, said = gate("101")
check("the run's non-PASS rows refuse, naming exactly them", code == 1 and len(suite_lines(said)) == 2 and "row broken-row is FAIL" in said and "row stale-row is KNOWN" in said, said)
check("a skipped row and a PASS row do not refuse", "row a " not in said and "row skipped-row" not in said, said)
waive("broken-row", "stale-row")
code, said = gate("101")
check("rows the owner waived by name with an issue pass", code == 0 and "GATE PASS v2.0" in said, said)
waive()
open(os.path.join(common, "loop", "owner-words.tsv"), "w").write("")

NO = "suite run does not cover the candidate"
RUNS["102"] = ("0" * 40, "completed", log(GOOD))
code, said = gate("102")
check("a run for a different commit refuses: " + NO, code == 1 and NO in said and "another commit" in said, said)
RUNS["103"] = (sha, "in_progress", "")
code, said = gate("103")
check("an unfinished run refuses: " + NO, code == 1 and NO in said and "not completed" in said, said)
RUNS["104"] = (sha, "completed", log(GOOD, "SHARDS 8 of 8 reported. UNRUN 3 (rows skipped for out of job time)."))
code, said = gate("104")
check("a run with rows UNRUN for job time refuses: " + NO, code == 1 and NO in said and "cut by budget" in said, said)
RUNS["105"] = (sha, "completed", log(GOOD, "SHARDS 7 of 8 reported. UNRUN 0 (rows skipped for out of job time)."))
code, said = gate("105")
check("a run with a shard that never reported refuses: " + NO, code == 1 and NO in said and "cut by budget" in said, said)
RUNS["106"] = (sha, "completed", log(GOOD[:2] + GOOD[3:]))
code, said = gate("106")
check("a run whose log lacks a nightly row refuses: " + NO, code == 1 and NO in said and "1 rows are unlogged" in said, said)
RUNS["107"] = (sha, "completed", log(GOOD, ""))
code, said = gate("107")
check("a run with no shard summary line refuses: " + NO, code == 1 and NO in said, said)
code, said = gate("999")
check("a run gh cannot read refuses: " + NO, code == 1 and NO in said, said)

open(os.path.join(common, "loop", "owner-words.tsv"), "w").write(TAB.join(("o1", "t", "operation", "promote v2.0.0", "v2.0.0")) + "\n")
code, said = call("promote", "v2", "--owner-record", "o1", "--ref", sha, "--suite-from", "102")
check("promote takes --suite-from and refuses a run that does not cover the candidate, tagging nothing",
      code == 1 and NO in said and "NOT PROMOTED v2.0.0" in said and "v2.0.0" not in git("tag", "--list").stdout, said)
code, said = call("--help")
check("--help names --suite-from", code == 0 and "--suite-from RUN" in said, said)

print("passed all" if not fails else "failed %d" % fails)
print("ALL PASS" if not fails else "")
sys.exit(1 if fails else 0)
