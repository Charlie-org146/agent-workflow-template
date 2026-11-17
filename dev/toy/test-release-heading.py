#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-docs/scripts/audit.py
"""changelog-v (DOC-13, #4660): release_trouble finds a CHANGELOG heading with or without the tag's leading v, without calling gh."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-docs", "scripts"))
import audit  # noqa: E402

fails = 0


def check(ok, what):
    global fails
    print("%s: %s" % ("PASS" if ok else "FAIL", what))
    fails += not ok


def sh(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


calls = []
real_run = subprocess.run


def fake_run(cmd, *args, **kwargs):
    if cmd[0] == "gh":
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 1, "", "release not found")
    return real_run(cmd, *args, **kwargs)


def trouble(notes, *tags):
    with tempfile.TemporaryDirectory() as repo:
        os.chdir(repo)
        sh("git", "init", "-q")
        sh("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x")
        for tag in tags:
            sh("git", "tag", tag)
        with open("CHANGELOG.md", "w", encoding="utf-8") as handle:
            handle.write(notes)
        calls.clear()
        audit.subprocess.run = fake_run
        try:
            found = audit.release_trouble(repo)
        finally:
            audit.subprocess.run = real_run
            os.chdir(root)
        return found


found = trouble("# Changelog\n\n## [1.2.3] - 2026-11-17\n\n- note\n", "v1.2.3")
check(not found and not calls, "a ## [1.2.3] heading is the note for tag v1.2.3 without calling gh")
found = trouble("# Changelog\n\n## v1.2.4 - 2026-11-17\n\n- note\n", "v1.2.4")
check(not found and not calls, "a ## v1.2.4 heading is still the note for tag v1.2.4 without calling gh")
found = trouble("# Changelog\n\n## [1.2.3] - 2026-11-17\n\n- note\n", "v1.2.3", "v1.2.5")
check([x[1] for x in found] == ["v1.2.5"] and [c[:3] for c in calls] == [["gh", "release", "view"]] and calls[0][3] == "v1.2.5",
      "a tag with no CHANGELOG heading still falls back to gh release view")
sys.exit(1 if fails else 0)
