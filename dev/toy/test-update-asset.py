#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-setup/scripts/update.py
"""REL-15: update downloads the release's attached package first and falls back to the source archive.

A fake gh on PATH logs each `release download` and writes a package or an archive. With an asset on the release, fetch()
returns the asset and never asks for the archive; with none (gh exits 1, or exits 0 with no file) it returns the archive,
so update keeps working for a release made before release.yml and for one whose package upload failed."""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-setup", "scripts"))
import update  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


GH = r'''#!/bin/sh
echo "$@" >> "$FAKE_LOG"
all="$*"
dir=.; while [ $# -gt 0 ]; do [ "$1" = --dir ] && dir=$2; shift; done
case "$all" in
  *--pattern*) case "$MODE" in asset) : > "$dir/agent-workflow-template-1.2.3.zip"; exit 0;; empty) exit 0;; *) echo "no assets match" >&2; exit 1;; esac;;
  *--archive*) : > "$dir/agent-workflow-template-v1.2.3.zip"; exit 0;;
esac
exit 1
'''


def fetch(mode):
    temp = tempfile.mkdtemp(prefix="upd-asset-")
    bindir, into, log = os.path.join(temp, "bin"), os.path.join(temp, "into"), os.path.join(temp, "log")
    os.makedirs(bindir)
    os.makedirs(into)
    gh = os.path.join(bindir, "gh")
    open(gh, "w").write(GH)
    os.chmod(gh, 0o755)
    os.environ.update(PATH=bindir + os.pathsep + os.environ["PATH"], MODE=mode, FAKE_LOG=log)
    got = update.fetch("owner/template", "test", "v1.2.3", into)
    calls = open(log).read() if os.path.exists(log) else ""
    return os.path.basename(got), calls


name, calls = fetch("asset")
check(name == "agent-workflow-template-1.2.3.zip" and "--archive" not in calls, "a release with a package asset is updated from the asset, not the archive")
name, calls = fetch("none")
check(name == "agent-workflow-template-v1.2.3.zip" and "--pattern" in calls and "--archive" in calls,
      "a release with no asset falls back to the source archive")
name, calls = fetch("empty")
check(name == "agent-workflow-template-v1.2.3.zip" and "--archive" in calls, "a download that wrote no file falls back to the source archive")
if failed:
    sys.exit(1)
print("PASS: REL-15: update prefers the release's package asset and falls back to the source archive")
