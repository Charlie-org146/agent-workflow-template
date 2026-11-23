"""Helpers moved whole out of package.py to keep it within its size line."""
import json
import os


def private_prefixes():
    """The private leak_prefixes setting (flow file, outside the repo): case-insensitive regexes the local leak hook blocks."""
    path = os.environ.get("LOOP_FLOW") or os.path.expanduser("~/.workflow-loop/flow.json")
    try:
        with open(path, encoding="utf-8") as handle:
            return [p for p in json.load(handle).get("leak_prefixes", []) if isinstance(p, str) and p]
    except (OSError, ValueError, AttributeError):
        print("NOTE: no leak_prefixes in %s; only the built-in scans ran" % path)
        return []
