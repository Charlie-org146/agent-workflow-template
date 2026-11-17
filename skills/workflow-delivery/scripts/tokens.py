#!/usr/bin/env python3
"""Tokens measured from a session's own transcript (DEL-16): per step for a worker, per trigger for the operation session.

usage: tokens.py [--session ID] [--since ISO] [--until ISO]    print the measure of one window as JSON (a debugging aid)

A session's transcript is <projects>/<folder>/<session id>.jsonl (the id is CLAUDE_CODE_SESSION_ID; LOOP_TRANSCRIPT_DIR
replaces <projects>, which is ~/.claude/projects). Each assistant line carries message.usage; one model call can span
several lines, so a call is counted once by message.id (the last line wins). Subagent calls are in other files and are
left out. Nothing here raises: an unreadable transcript measures nothing, and a goal then reads "tokens unread".

A measure is {input, cache_read, cache_write, output, calls, model, peak}; peak is the largest context (input + cache_read +
cache_write) any one call carried. fresh() is input + cache_write + output (the token budget's unit, no cache reads);
total() adds the cache reads (the unit of the v1 baseline). tokens[step] in a run record is a measure, or an int that an
older step reported; reported counts kept beside a measure sit in its "reported" field.
"""
import argparse
import glob
import json
import os
import re
import sys
import time
from collections import Counter

FIELDS = ("input", "cache_read", "cache_write", "output")
ID = re.compile(r"^[A-Za-z0-9_-]{8,128}$")


def stamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))


def transcript(session=None, base=None):
    session = session or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    base = base or os.environ.get("LOOP_TRANSCRIPT_DIR") or os.path.join(os.path.expanduser("~"), ".claude", "projects")
    if not ID.match(session):
        return ""
    found = sorted(glob.glob(os.path.join(base, "*", session + ".jsonl")))
    return found[0] if found else ""


def lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for text in handle:
                try:
                    found = json.loads(text)
                except ValueError:
                    continue
                if isinstance(found, dict):
                    yield found
    except OSError:
        return


def calls(path, since="", until="", turn=None):
    """One dict per model call of the main chain with since < time <= until (ISO, to the second), oldest first. turn(user
    line) may return a label for the turn that line starts; each call carries the label of the turn it first appeared in."""
    seen, label = {}, ""
    for number, line in enumerate(lines(path)):
        if turn and line.get("type") == "user" and not line.get("isSidechain"):
            label = turn(line) or label
        message = line.get("message")
        usage = message.get("usage") if isinstance(message, dict) else None
        if line.get("type") != "assistant" or line.get("isSidechain") or not isinstance(usage, dict) or message.get("model") == "<synthetic>":
            continue
        n = lambda key: usage.get(key) if isinstance(usage.get(key), int) and not isinstance(usage.get(key), bool) else 0
        at = str(line.get("timestamp") or "")[:19]
        item = {"at": at, "model": str(message.get("model") or ""), "input": n("input_tokens"), "cache_read": n("cache_read_input_tokens"),
                "cache_write": n("cache_creation_input_tokens"), "output": n("output_tokens")}
        item["context"] = item["input"] + item["cache_read"] + item["cache_write"]
        key = message.get("id") or line.get("uuid") or "line%d" % number
        item["turn"] = seen[key]["turn"] if key in seen else label
        seen[key] = item
    since, until = since[:19], until[:19]
    return sorted((c for c in seen.values() if c["at"] and c["at"] > since and (not until or c["at"] <= until)), key=lambda c: c["at"])


def measure(path, since="", until=""):
    """The window's measure, or None when it holds no call."""
    found = calls(path, since, until)
    if not found:
        return None
    out = {key: sum(c[key] for c in found) for key in FIELDS}
    models = Counter(c["model"] for c in found if c["model"])
    return dict(out, calls=len(found), model=models.most_common(1)[0][0] if models else "", peak=max(c["context"] for c in found))


def fresh(value):
    if isinstance(value, dict):
        return sum(int(value.get(k) or 0) for k in ("input", "cache_write", "output", "reported"))
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def total(value):
    return fresh(value) + (int(value.get("cache_read") or 0) if isinstance(value, dict) else 0)


def mark_of(state):
    """Where a goal's next window starts: the last measured instant, else its first log line (its freeze)."""
    first = ((state.get("log") or [""])[0] or "")[:19]
    return str(state.get("token_at") or (first if re.match(r"^\d{4}-\d\d-\d\dT", first) else ""))


def add(state, step, given, measure_it=False, now=None):
    """Add a step's tokens: a measured window since the goal's mark when measure_it (and a transcript is found), then any
    count the step reported (an int; unknown or none adds nothing)."""
    held = state.get("tokens") if isinstance(state.get("tokens"), dict) else {}
    old = held.get(step)
    got, until = None, now or stamp()
    path = transcript() if measure_it else ""
    if path and mark_of(state):
        got = measure(path, mark_of(state), until)
        state["token_at"] = until
    reported = int(given) if str(given).isdigit() else 0
    if got:
        mine = dict(old) if isinstance(old, dict) else {"reported": old} if isinstance(old, int) and old else {}
        for key in FIELDS + ("calls",):
            mine[key] = int(mine.get(key) or 0) + got[key]
        mine.update(model=got["model"], peak=max(int(mine.get("peak") or 0), got["peak"]))
        if reported:
            mine["reported"] = int(mine.get("reported") or 0) + reported
        state["tokens"] = dict(held, **{step: mine})
    elif reported:
        if isinstance(old, dict):
            state["tokens"] = dict(held, **{step: dict(old, reported=int(old.get("reported") or 0) + reported)})
        else:
            state["tokens"] = dict(held, **{step: reported + (old if isinstance(old, int) else 0)})


def live(state):
    """Fresh tokens spent since the last mark (a goal with no mark has none yet)."""
    path = transcript() if state.get("token_at") else ""
    got = measure(path, str(state["token_at"]), stamp()) if path else None
    return fresh(got) if got else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session", default="")
    parser.add_argument("--since", default="")
    parser.add_argument("--until", default="")
    args = parser.parse_args()
    path = transcript(args.session or None)
    print(json.dumps(measure(path, args.since, args.until) if path else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
