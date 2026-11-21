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

# the archive's own edge cases (ENG-10): the version of a source archive is the VERSION file of its tree
import contextlib  # noqa: E402
import io  # noqa: E402
import zipfile  # noqa: E402


def archive(version_text):
    path = os.path.join(tempfile.mkdtemp(prefix="upd-tree-"), "tree.zip")
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr("template/skills/workflow-x/SKILL.md", "# x\n")
        if version_text is not None:
            bundle.writestr("template/VERSION", version_text)
    return path


manifest, _ = update.load(archive("1.0.158\n"))
check(manifest["version"] == "1.0.158" and update.version_key(manifest["version"]) > update.version_key("1.0.157"),
      "a source archive reports the VERSION of its tree, and an adopter on 1.0.157 sees 1.0.158 as newer")
try:
    update.load(archive(None))
    refused = False
except ValueError as error:
    refused = "VERSION" in str(error)
check(refused, "a source archive without a VERSION file is refused (the caller refuses it as UPDATE_BAD_ARCHIVE and writes nothing)")
manifest, _ = update.load(archive("garbage\n"))
check(update.version_key(manifest["version"]) == () and update.version_key(manifest["version"]) < update.version_key("1.0.157"),
      "a VERSION that is not a number reads as older than any installed version, so only a numeric VERSION in the tag updates anyone")
stale, _ = update.load(archive("1.0.112\n"))
check(update.version_key(stale["version"]) < update.version_key("1.0.157"),
      "the verified stranding: an archive whose VERSION lags the tag (1.0.112) reads as older than an installed 1.0.157, which is why the release tag carries its own VERSION")
bindir = tempfile.mkdtemp(prefix="upd-nogh-")
open(os.path.join(bindir, "gh"), "w").write("#!/bin/sh\nexit 1\n")
os.chmod(os.path.join(bindir, "gh"), 0o755)
os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
into, err = tempfile.mkdtemp(prefix="upd-into-"), io.StringIO()
with contextlib.redirect_stderr(err):
    try:
        update.fetch("owner/template", "test", "v1.2.3", into)
        code = 0
    except SystemExit as stop:
        code = stop.code
check(code == 2 and "UPDATE_GH" in err.getvalue() and os.listdir(into) == [], "a release with no package and no source archive is refused as UPDATE_GH and nothing is written")

if failed:
    sys.exit(1)
print("PASS: REL-15: update prefers the release's package asset and falls back to the source archive")
