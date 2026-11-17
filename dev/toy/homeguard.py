#!/usr/bin/env python3
"""Fail loudly when a toy test changes the owner's real ~/.workflow-loop (issue 4393).

usage: homeguard.py snap FILE   write what ~/.workflow-loop holds now (each file's path and sha256) to FILE
       homeguard.py diff FILE   compare with that snapshot; print a LEAK line per change and exit 1, else exit 0

The folder is os.path.expanduser("~/.workflow-loop") at snap time, so on Windows it follows USERPROFILE as Python does; the
snapshot remembers it, so a toy that changes HOME later is still judged on the owner's folder. A home inside the system temp
folder (a lane's own) is not the owner's and is not judged. TOY_REAL_WL names another folder (the test of this guard). It
reads files and never writes inside the folder; the snapshot goes to FILE.
"""
import hashlib
import json
import os
import sys
import tempfile


def folder():
    return os.environ.get("TOY_REAL_WL") or os.path.expanduser("~/.workflow-loop")


def other_runs(top, here, name=""):
    """True for what other sessions' runs write in the owner's real folder, which a toy can't be judged on: compiled caches, the lane
    tickets under lanes/, and the scheduler's own files under schedule/ (log/, each repo's health-report.txt and tree/). Anything else
    under schedule/ (repos.json, a new entry) is state a toy must not touch (#4683). TOY_GUARD_STRICT judges a fresh home in full."""
    rel = os.path.relpath(os.path.join(here, name), top).replace(os.sep, "/").split("/")
    if "__pycache__" in rel:
        return True
    if os.environ.get("TOY_GUARD_STRICT"):
        return False
    return rel[0] == "lanes" or (rel[0] == "schedule" and (rel[1:2] == ["log"] or rel[2:3] == ["tree"] or rel[2:] == ["health-report.txt"]))


def scan(top):
    found = {}
    for here, _dirs, names in os.walk(top):
        _dirs[:] = [d for d in _dirs if not other_runs(top, here, d)]
        for name in names:
            if other_runs(top, here, name):
                continue
            path = os.path.join(here, name)
            try:
                with open(path, "rb") as handle:
                    found[os.path.relpath(path, top).replace(os.sep, "/")] = hashlib.sha256(handle.read()).hexdigest()
            except OSError:
                found[os.path.relpath(path, top).replace(os.sep, "/")] = "unreadable"
    return found


def main(argv):
    if len(argv) != 2 or argv[0] not in ("snap", "diff"):
        sys.exit(__doc__)
    if argv[0] == "snap":
        top = folder()
        own = os.environ.get("TOY_REAL_WL") or not os.path.realpath(top).startswith(os.path.realpath(tempfile.gettempdir()))
        with open(argv[1], "w") as handle:
            json.dump({"top": top, "files": scan(top)} if own else {}, handle)
        return 0
    try:
        with open(argv[1]) as handle:
            seen = json.load(handle)
        top, before = seen["top"], seen["files"]
    except KeyError:
        return 0
    except (OSError, ValueError):
        sys.stderr.write("LEAK GUARD: no snapshot was taken, so a change there is not judged\n")
        return 0
    after = scan(top)
    changes = ["%s %s" % (what, name) for what, name in sorted(
        [("added", n) for n in after if n not in before] + [("removed", n) for n in before if n not in after]
        + [("changed", n) for n in after if n in before and after[n] != before[n]], key=lambda c: c[1])]
    for line in changes[:10]:
        sys.stderr.write("LEAK: this test changed the real %s: %s\n" % (top, line))
    return 1 if changes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
