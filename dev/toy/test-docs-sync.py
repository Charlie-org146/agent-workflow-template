#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py skills/workflow-docs/scripts/docs.py skills/workflow-docs/scripts/deployments.py
"""external-sync (DOC-17): docs.py sync reads each feature's external PRD (a url or an MCP connector) and reports DRIFT when
the repo's copy, .loop/prd/<Page>.md, differs; it rewrites only that file, only when sync owns it, never writes to the
source, and prints 'not connected' with no connector."""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, "skills", "workflow-docs", "scripts", "docs.py")
bad = 0


def ok(good, text):
    global bad
    print(("PASS: " if good else "FAIL: ") + text)
    bad += not good


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as handle:
        handle.write(text)


def prd(*rows):
    return "# Thermis PRD\n\n## Requirements\n\n" + "".join("- %s: **Unreviewed** %s\n  - a sub-bullet\n\n" % row for row in rows)


def sync(repo, *args, reader=None):
    env = {k: v for k, v in os.environ.items() if k != "LOOP_PRD_READER"}
    if reader:
        env["LOOP_PRD_READER"] = reader
    done = subprocess.run([sys.executable, DOCS, "sync", *args], cwd=repo, env=env, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def read(path):
    with open(path, newline="") as handle:
        return handle.read()


with tempfile.TemporaryDirectory() as tmp:
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo)
    subprocess.run(["git", "init", "-q", "-b", "main", repo], capture_output=True)
    source = os.path.join(tmp, "thermis-sensor.md")
    write(source, prd(("TH-1", "Reads the sensor every second"), ("TH-2", "Alerts above 80 degrees")))
    write(os.path.join(repo, ".loop", "docs.tsv"), "Sensor\tsrc\turl:%s\nDelivery\tsrc\tpage\nHub\tsrc\tmcp:notion:4178261590fd\n" % source.replace("\\", "/"))
    mirror = os.path.join(repo, ".loop", "prd", "Sensor.md")

    code, out = sync(repo)
    ok(code == 0 and "DRIFT Sensor: TH-1 added" in out and "SYNCED Sensor" in out, "a first sync reports the ids as DRIFT and writes the repo copy")
    ok(os.path.exists(mirror) and "- TH-2: Alerts above 80 degrees" in read(mirror), "the repo copy holds each requirement id and its text")
    code, out = sync(repo)
    ok("DRIFT Sensor" not in out and "in step" in out, "a second sync finds the copy in step")

    write(source, prd(("TH-1", "Reads the sensor every two seconds"), ("TH-3", "Logs every alert")))
    before = read(source)
    code, out = sync(repo, "--dry-run")
    ok(code == 1 and "DRIFT Sensor: TH-1 changed" in out and "TH-2 removed" in out and "TH-3 added" in out, "a changed, removed and added requirement are each DRIFT, and --dry-run exits 1")
    ok("every second" in read(mirror), "--dry-run writes nothing")
    code, out = sync(repo)
    text = read(mirror)
    ok(code == 0 and "every two seconds" in text and "TH-3" in text and "TH-2" not in text, "sync rewrites the repo copy to match the changed source")
    ok(read(source) == before, "the source is only read: its text is unchanged by a sync")

    code, out = sync(repo)
    ok("not connected: Hub" in out and code == 0 and not os.path.exists(os.path.join(repo, ".loop", "prd", "Hub.md")), "an mcp source with no connector prints not connected, writes nothing and exits 0")
    reader = os.path.join(tmp, "reader.py")
    write(reader, "import sys\nprint(open(%r).read() if sys.argv[1].startswith('mcp:notion:') else '')\n" % source)
    code, out = sync(repo, reader="%s %s" % (sys.executable, reader))
    ok("SYNCED Hub" in out and "TH-3" in read(os.path.join(repo, ".loop", "prd", "Hub.md")), "an mcp source is read through the configured connector")
    ok("Delivery" not in out, "a page whose source is page is not visited")

    hand = os.path.join(repo, ".loop", "prd", "Sensor.md")
    write(hand, "# my own notes\n- TH-9: mine\n")
    code, out = sync(repo)
    ok("SKIPPED Sensor" in out and read(hand).startswith("# my own notes"), "a hand-written file at the path is never overwritten")
    ok(read(source) == before and not os.path.exists(os.path.join(repo, "thermis-sensor.md")), "no sync wrote to the source or put a copy beside it")
raise SystemExit(1 if bad else 0)
