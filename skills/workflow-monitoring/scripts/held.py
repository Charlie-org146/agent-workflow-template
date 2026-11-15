#!/usr/bin/env python3
"""A pr lane lost to a moved base is held time, not active time (#4261, #3878).

usage: held.py [-h] LOGFILE

Prints the log indexes (one per line) whose preceding gap is a lost lane: a goal's run log is a JSON list of
"<UTC time> <text>" entries, read from LOGFILE (a run record's "log" list, or the whole record). Imported by board_log.py,
whose flow_seconds skips those gaps, so fit.active_minutes (the time budget) and the board's estimate never charge them.

A lane is lost when its refusal was the main branch moving: a `merge refused (exit N)` entry (merge.py's BASE_MOVED and
HEAD_MOVED, logged by autorelease.reopen) or a `main moved, try not counted` entry (pool.pr_moved). The gap before the refusal
is lost, and so is the gap before the `pr` entry just ahead of a `merge refused`: the lane that opened the pull request the base
then left behind. A `try N failed` entry is the goal's own failure and stays charged. It reads a log and nothing else.
"""
import json
import re
import sys

LOST = re.compile(r"merge refused \(exit \d+\)|main moved, try not counted")


def text(entry):
    """What a log entry says after its timestamp."""
    return (str(entry).split(" ", 1) + [""])[1]


def lost(log):
    """The indexes of the log entries whose preceding gap is a lost lane (see the module doc)."""
    drop = set()
    for index, entry in enumerate(log):
        if LOST.match(text(entry)):
            drop.add(index)
            if text(entry).startswith("merge refused") and index and text(log[index - 1]).split(" ", 1)[0].rstrip(":") == "pr":
                drop.add(index - 1)
    return drop


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 2)
    with open(sys.argv[1]) as handle:
        data = json.load(handle)
    for number in sorted(lost(data.get("log") if isinstance(data, dict) else data)):
        print(number)
