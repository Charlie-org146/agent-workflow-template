#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/counting.py skills/workflow-docs/scripts/prd.py skills/workflow-health/scripts/health.py skills/workflow-monitoring/scripts/board.py
"""ext-two-way (DOC-17): either side of a PRD kept elsewhere can change. docs.py sync compares the external document with the
repo's copy, .loop/prd/<Page>.md, against what both last agreed on: a difference is a DELTA naming the page, the id, the side
and both texts, and neither side is overwritten. Each new delta is posted once as a GitHub issue and once as a comment on the
external page; --accept PAGE:ID=repo|source writes that side's text, that id only, to the other side and closes the issue;
no connector prints 'not connected' and never fails. The fake gh and the fake writer here only record their calls: the real
Notion is never used."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, "skills", "workflow-docs", "scripts", "docs.py")
bad = 0

FAKE_GH = '''import json, os, sys
open(os.environ["TOY_LOG"], "a").write(json.dumps(["gh"] + sys.argv[1:]) + "\\n")
if os.environ.get("TOY_GH_FAIL"):
    sys.exit("gh: not logged in")
if sys.argv[1:3] == ["issue", "create"]:
    n = sum(1 for x in open(os.environ["TOY_LOG"]) if '"issue", "create"' in x)
    print("https://example.test/issues/%d" % n)
'''
FAKE_WRITER = '''import json, os, re, sys
source, action = sys.argv[1], sys.argv[2:]
text = sys.stdin.read()
open(os.environ["TOY_LOG"], "a").write(json.dumps(["writer"] + action + [text]) + "\\n")
if os.environ.get("TOY_WRITER_FAIL"):
    sys.exit(1)
if action[0] in ("replace", "remove"):
    path = source[4:]
    lines = open(path).read().split("\\n")
    keep = [x for x in lines if not x.startswith("- %s:" % action[1])]
    if action[0] == "replace":
        keep.insert(lines.index(next(x for x in lines if x.startswith("- %s:" % action[1]))), "- %s: **Unreviewed** %s" % (action[1], text))
    open(path, "w").write("\\n".join(keep))
'''


def ok(good, text):
    global bad
    print(("PASS: " if good else "FAIL: ") + text)
    bad += not good


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as handle:
        handle.write(text)


def read(path):
    with open(path, newline="") as handle:
        return handle.read()


def prd(*rows):
    return "# Thermis PRD\n\n## Requirements\n\n" + "".join("- %s: **Unreviewed** %s\n  - a sub-bullet\n\n" % row for row in rows)


def calls(log, *words):
    try:
        return [x for x in read(log).splitlines() if all(w in x for w in words)]
    except OSError:
        return []


with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", "-b", "main", repo], capture_output=True)
    log = os.path.join(tmp, "calls.log")
    write(os.path.join(tmp, "gh.py"), FAKE_GH)
    write(os.path.join(tmp, "writer.py"), FAKE_WRITER)
    source = os.path.join(tmp, "thermis-sensor.md")
    write(source, prd(("TH-1", "Reads the sensor every second"), ("TH-2", "Alerts above 80 degrees")))
    write(os.path.join(repo, ".loop", "docs.tsv"), "Sensor\tsrc\turl:%s\nDelivery\tsrc\tpage\nHub\tsrc\tmcp:notion:4178261590fd\n" % source.replace("\\", "/"))
    copy = os.path.join(repo, ".loop", "prd", "Sensor.md")
    ENV = {"TOY_LOG": log, "LOOP_GH": "%s %s" % (sys.executable, os.path.join(tmp, "gh.py")),
           "LOOP_PRD_WRITER": "%s %s" % (sys.executable, os.path.join(tmp, "writer.py"))}

    def sync(*args, **extra):
        env = {k: v for k, v in os.environ.items() if k not in ("LOOP_PRD_READER", "LOOP_PRD_WRITER", "LOOP_GH")}
        env.update(ENV)
        env.update(extra)
        for gone in [k for k, v in env.items() if v is None]:
            del env[gone]
        done = subprocess.run([sys.executable, DOCS, "sync", *args], cwd=repo, env=env, capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def edit(path, old, new):
        write(path, read(path).replace(old, new))

    code, out = sync()
    ok(code == 0 and "SYNCED Sensor" in out and "DELTA" not in out and not calls(log), "the first sync adopts the source: a copy and a baseline, no delta, nothing posted")
    ok(os.path.exists(copy) and os.path.exists(copy[:-3] + ".base") and "- TH-2: Alerts above 80 degrees" in read(copy), "the repo copy holds each requirement id and its text beside its baseline")

    edit(copy, "every second", "every two seconds")
    code, out = sync("--dry-run")
    ok(code == 1 and "DELTA Sensor: TH-1 the repo changed (repo: Reads the sensor every two seconds | source: Reads the sensor every second)" in out,
       "a requirement changed only in the repo is a DELTA naming the page, the id, the repo as the side, and both texts, and --dry-run exits 1")
    ok(not calls(log) and "every two seconds" in read(copy), "--dry-run posts nothing and writes nothing")

    before = read(source), read(copy)
    code, out = sync()
    ok(code == 0 and "DELTA Sensor: TH-1 the repo changed" in out and (read(source), read(copy)) == before, "a delta overwrites neither side")
    ok(len(calls(log, "issue", "create")) == 1 and "DELTA Sensor TH-1" in calls(log, "issue", "create")[0] and '"--milestone", "Sensor"' in calls(log, "issue", "create")[0]
       and len(calls(log, "writer", "comment")) == 1 and "every two seconds" in calls(log, "writer", "comment")[0],
       "a new delta is posted once as an issue on the page's milestone and once as a comment on the external page, with both texts")
    code, out = sync()
    ok(len(calls(log, "issue", "create")) == 1 and len(calls(log, "writer", "comment")) == 1 and "POSTED" not in out, "a second sync posts nothing more")

    edit(source, "above 80", "above 90")
    code, out = sync()
    ok("DELTA Sensor: TH-2 the source changed (repo: Alerts above 80 degrees | source: Alerts above 90 degrees)" in out and len(calls(log, "issue", "create")) == 2,
       "a requirement changed only in the external document is a DELTA naming the source, and is posted as its own issue")
    edit(source, "every second", "every three seconds")
    code, out = sync()
    ok("DELTA Sensor: TH-1 both sides changed" in out and len(calls(log, "issue", "comment")) == 1, "a requirement changed on both sides is a DELTA for both, commented on its issue again")

    code, out = sync("--accept", "Sensor:TH-2=source")
    text = read(copy)
    ok("ACCEPTED Sensor: TH-2" in out and "- TH-2: Alerts above 90 degrees" in text and "every two seconds" in text and len(calls(log, "issue", "close")) == 1 and "TH-2" not in out.split("ACCEPTED")[1].split("\n", 1)[1],
       "accept source writes only that requirement into the repo copy, leaves every other as it was, and closes its issue")
    code, out = sync("--accept", "Sensor:TH-1=repo")
    ok("ACCEPTED Sensor: TH-1" in out and "- TH-1: **Unreviewed** Reads the sensor every two seconds" in read(source) and "above 90" in read(source)
       and calls(log, "writer", "replace", "TH-1") and len(calls(log, "issue", "close")) == 2, "accept repo writes only that requirement into the document through the writer and closes its issue")
    code, out = sync()
    ok(code == 0 and "DELTA" not in out and "1 in step" in out and not sync("--open")[1].strip(), "after both are accepted the sides agree and no delta is open")

    edit(copy, "- TH-2:", "- TH-3: A new alert\n- TH-2:")
    code, out = sync(LOOP_PRD_WRITER=None)
    ok(code == 0 and "DELTA Sensor: TH-3 the repo changed" in out and "not connected to" in out and "POSTED Sensor TH-3" in out, "with no writer the delta is still posted as an issue, and the comment says not connected")
    code, out = sync("--accept", "Sensor:TH-3=repo", LOOP_PRD_WRITER=None)
    ok(code == 0 and "not connected: Sensor" in out and "TH-3" not in read(source) and "- TH-3: A new alert" in read(copy), "accepting the repo's text with no writer says not connected, exits 0 and changes nothing")
    edit(copy, "A new alert", "A newer alert")
    code, out = sync(TOY_GH_FAIL="1")
    ok(code == 0 and "not connected: Sensor TH-3 (gh)" in out and "DELTA Sensor: TH-3" in out, "with no working gh the delta is shown, nothing is posted, and the loop is not broken")
    seen = len(calls(log))
    code, listed = sync("--open")
    ok(code == 0 and "DELTA Sensor: TH-3 the repo changed (review: https://" in listed and len(calls(log)) == seen, "sync --open lists each open delta from the ledger, with no call to gh or the connector")

    import importlib.util

    def load(skill, name):
        folder = os.path.join(ROOT, "skills", skill, "scripts")
        sys.path.insert(0, folder)
        sys.argv[0] = os.path.join(folder, name + ".py")  # health.py finds its sibling skills from argv[0]
        spec = importlib.util.spec_from_file_location(name, os.path.join(folder, name + ".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    health = [r for r in load("workflow-health", "health").docs_check(repo) if r["rule"] == "delta"]
    ok(len(health) == 1 and health[0]["state"] == "FAIL" and health[0]["subject"] == "Sensor" and "TH-3" in health[0]["detail"], "health reports each open delta as a FAIL row of the docs rule")
    waits = load("workflow-monitoring", "board").open_deltas("toy", repo)
    ok(len(waits) == 1 and waits[0]["slug"] == "Sensor:TH-3" and "inconsistency" in waits[0]["ask"] and "--accept Sensor:TH-3=source" in waits[0]["words"], "the check-in's board lists each open delta as waiting on the owner")

    code, out = sync()
    ok("Hub" in out and "not connected: Hub (mcp:notion:4178261590fd)" in out, "an mcp source with no connector prints not connected, writes nothing and exits 0")
    ok(not os.path.exists(os.path.join(repo, ".loop", "prd", "Hub.md")) and not os.path.exists(os.path.join(repo, ".loop", "prd", "Delivery.md")), "a page whose source is page, or an unreachable one, is never given a copy")
    write(os.path.join(repo, ".loop", "prd", "Other.md"), "hand written\n")
    write(os.path.join(repo, ".loop", "docs.tsv"), "Other\tsrc\turl:%s\n" % source.replace("\\", "/"))
    code, out = sync()
    ok("SKIPPED Other" in out and read(os.path.join(repo, ".loop", "prd", "Other.md")) == "hand written\n", "a hand-written file at the copy's path is never overwritten")

raise SystemExit(1 if bad else 0)
