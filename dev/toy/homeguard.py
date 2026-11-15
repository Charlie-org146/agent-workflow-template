#!/usr/bin/env python3
"""Fail loudly when a toy test changes the owner's real ~/.workflow-loop (issue 4393).

usage: homeguard.py snap FILE   write what ~/.workflow-loop holds now (each file's path and sha256) to FILE
       homeguard.py diff FILE   compare with that snapshot; print a LEAK line per change and exit 1, else exit 0

The folder is os.path.expanduser("~/.workflow-loop"), so on Windows it follows USERPROFILE as Python does; TOY_REAL_WL
names another folder (the test of this guard). It reads files and never writes inside the folder; the snapshot goes to FILE.
"""
import hashlib
import json
import os
import sys


def folder():
    return os.environ.get("TOY_REAL_WL") or os.path.expanduser("~/.workflow-loop")


def scan(top):
    found = {}
    for here, _dirs, names in os.walk(top):
        for name in names:
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
    top = folder()
    if argv[0] == "snap":
        with open(argv[1], "w") as handle:
            json.dump(scan(top), handle)
        return 0
    try:
        with open(argv[1]) as handle:
            before = json.load(handle)
    except (OSError, ValueError):
        sys.stderr.write("LEAK GUARD: no snapshot of %s was taken, so a change there is not judged\n" % top)
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
