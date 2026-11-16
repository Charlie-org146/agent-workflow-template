#!/usr/bin/env python3
# windows: ok
# reads: dev/toy/homeguard.py dev/toy/reap.sh dev/toy/test-settings.sh
"""home-guard (issue 4393): a toy never reads or writes the owner's real ~/.workflow-loop. The harness (reap.sh) snapshots
that folder when a toy starts and fails the toy at exit with a LEAK line when anything there changed; every toy that sets
HOME also sets USERPROFILE, because Python's expanduser reads USERPROFILE on Windows.

Never touches the real folder: TOY_REAL_WL points the guard at a throwaway one. usage: test-home-guard.py [guard|isolate]"""
import glob
import os
import re
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LEG = sys.argv[1] if len(sys.argv) > 1 else ""
fails = 0


def check(name, ok, extra="", leg="guard"):
    global fails
    print(("PASS: " if ok else "FAIL: ") + name + ("" if ok else "  " + extra))
    fails += 0 if ok or (LEG and LEG != leg) else 1


def toy(tmp, name, body):
    """Run a one-line toy that sources the harness, with TOY_REAL_WL at tmp/wl; (exit code, stderr)."""
    path = os.path.join(tmp, name)
    open(path, "w", newline="\n").write('#!/bin/bash\n# windows: ok\nhere="%s"\n. "$here/dev/toy/reap.sh"\n%s\n' % (root.replace("\\", "/"), body))
    done = subprocess.run(["bash", path], capture_output=True, text=True, env=dict(os.environ, TOY_REAL_WL=os.path.join(tmp, "wl")))
    return done.returncode, done.stderr + done.stdout


with tempfile.TemporaryDirectory() as tmp:
    os.makedirs(os.path.join(tmp, "wl"))
    open(os.path.join(tmp, "wl", "flow.json"), "w").write('{"limit": 600}')
    code, said = toy(tmp, "quiet.sh", "true")
    check("a toy that leaves the real folder alone passes the guard", code == 0 and "LEAK" not in said, said)
    code, said = toy(tmp, "writes.sh", 'echo \'{"limit": 99}\' > "$TOY_REAL_WL/flow.json"')
    check("a toy that rewrites a file there fails with a LEAK line", code != 0 and "LEAK" in said and "flow.json" in said, said)
    open(os.path.join(tmp, "wl", "flow.json"), "w").write('{"limit": 600}')
    code, said = toy(tmp, "adds.sh", 'echo x > "$TOY_REAL_WL/new.json"')
    check("a toy that adds a file there fails with a LEAK line", code != 0 and "LEAK" in said and "new.json" in said, said)
    code, said = toy(tmp, "flow.sh", 'case "$LOOP_FLOW" in "$TOY_REAL_WL"*|"") exit 3;; esac; [ "$LOOP_HEALTH" != "" ] || exit 4')
    check("the harness points LOOP_FLOW and LOOP_HEALTH at temp paths", code == 0, said)

def unpaired(text):
    return bool(re.search(r"(?<![A-Za-z_])HOME[=\"]|\"HOME\"|'HOME'|\bHOME=", text)) and "USERPROFILE" not in text


check("control: a toy text that sets HOME alone is found", unpaired("export HOME=/tmp/x"), "", "isolate")
check("control: a toy text that sets HOME and USERPROFILE is not", not unpaired("export HOME=/tmp/x USERPROFILE=/tmp/x"), "", "isolate")
bad = []
for path in sorted(glob.glob(os.path.join(root, "dev", "toy", "test-*"))):
    if not path.endswith((".sh", ".py")) or path.endswith("test-home-guard.py"):
        continue
    if unpaired(open(path, encoding="utf-8", errors="replace").read()):
        bad.append(os.path.basename(path))
check("every toy that sets HOME also sets USERPROFILE (Python's expanduser reads it on Windows)", not bad, ", ".join(bad), "isolate")
sys.exit(1 if fails else 0)
