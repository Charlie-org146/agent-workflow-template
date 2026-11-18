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
import subprocess
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
    return (rel[:2] == ["routines", "logs"] or rel[0] == "lanes" or rel[0] == "skills-main" or (rel[0] == "schedule" and (rel[1:2] == ["log"] or rel[2:3] == ["tree"] or rel[2:] == ["health-report.txt"]
            or rel[1:2] and rel[1].startswith("repos.json"))))  # skills-main and the registry are judged by who wrote them, below (#4760)


def temp_prefixes():
    base = tempfile.gettempdir()
    return {p.replace(os.sep, "/").lower().rstrip("/") + "/" for p in (base, os.path.realpath(base), "/tmp")}


def in_temp(value):
    """True when a JSON value holds a path under the system temp folder: a toy's fixture, never another session's real repo."""
    if isinstance(value, str):
        return value.replace(os.sep, "/").lower().startswith(tuple(temp_prefixes()))
    if isinstance(value, dict):
        return any(in_temp(v) for v in value.values())
    return isinstance(value, list) and any(in_temp(v) for v in value)


def registry(top):
    """The schedule registry as other sessions leave it is not judged; an entry that points into the temp folder is a toy's, and so is a
    registry that no longer parses. Returns {key: hash} of those only."""
    path = os.path.join(top, "schedule", "repos.json")
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError:
        return {}
    try:
        entries = json.loads(raw).get("repos") or {}
        return {"schedule/repos.json#" + str(name): hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
                for name, entry in entries.items() if in_temp(entry)}
    except (ValueError, AttributeError):
        return {"schedule/repos.json": hashlib.sha256(raw).hexdigest()}


def skills_main(top):
    """The installed template checkout is judged by git, not by file hashes: another session moves it (a checkout rewrites START.md and
    config.json) and leaves it clean, while a toy that writes there leaves an untracked or modified file. Returns {key: hash} of
    what git calls changed; a folder that is not a checkout is hashed whole."""
    folder = os.path.join(top, "skills-main")
    if not os.path.exists(os.path.join(folder, ".git")):
        return {os.path.relpath(os.path.join(h, n), top).replace(os.sep, "/"): hashlib.sha256(open(os.path.join(h, n), "rb").read()).hexdigest()
                for h, _d, ns in os.walk(folder) for n in ns if os.path.isfile(os.path.join(h, n)) and "__pycache__" not in h}
    done = subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=folder, capture_output=True, text=True)
    found = {}
    for line in done.stdout.splitlines():
        name = line[3:].strip().strip('"')
        try:
            with open(os.path.join(folder, name), "rb") as handle:
                found["skills-main/" + name] = line[:2] + hashlib.sha256(handle.read()).hexdigest()
        except OSError:
            found["skills-main/" + name] = line[:2]
    return found


def scan(top):
    found = {} if os.environ.get("TOY_GUARD_STRICT") else dict(registry(top), **skills_main(top))
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
