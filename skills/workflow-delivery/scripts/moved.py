"""Helpers moved out of the near-cap scripts, and the one way to reach the shared steps.py (skills/ in the repo, shared/ in a pack)."""
import importlib
import os
import sys


def steps():
    """The shared steps.py by name, found in skills/ (repo) or shared/ (pack); a named refusal when it is missing."""
    if "steps" not in sys.modules:
        sys.dont_write_bytecode = True  # the one shared file sits where a cache folder would break the package check
        here = os.path.dirname(os.path.abspath(__file__))
        for path in (os.path.join(here, "..", ".."), os.path.join(here, "..", "..", "..", "shared")):
            if os.path.exists(os.path.join(path, "steps.py")):
                sys.path.insert(0, os.path.normpath(path))
                break
    try:
        return importlib.import_module("steps")
    except ImportError:
        sys.exit("REFUSED: steps.py is missing. Fix: reinstall the workflow package (SC_MISSING).")


import re  # noqa: E402


def sync_touches(goal_file, touches):
    try:
        with open(goal_file) as handle:
            text = handle.read()
    except OSError:
        return False
    line = "- Touches: " + (", ".join(touches) or "not declared")
    new = re.sub(r"^- Touches: .*$", lambda _: line, text, count=1, flags=re.M)
    if new == text:
        return False
    with open(goal_file, "w") as handle:
        handle.write(new)
    return True
