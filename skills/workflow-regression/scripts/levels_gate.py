#!/usr/bin/env python3
"""The gate of every command that must not run on a wrong table: validation, what this branch lowered since its merge
base (with the owner records), and a write left half done."""
import json
import os
import re
import sys

import slots
from slots import fcntl
from levels import (CODE, MARKER, RANK, RECORD, RISKS, SHOWN, TABLE, Problem, State, excuse, file_of, git, parse_record,
                    text_of, validate)


def common_dir(root):
    found = git(root, "rev-parse", "--git-common-dir")
    return os.path.abspath(os.path.join(root, found.strip())) if found else None


def goal_slug(root):
    branch = (git(root, "symbolic-ref", "--quiet", "--short", "HEAD") or "").strip()
    return branch[5:] if branch.startswith("loop/") else ""


def ledger(root):
    """The owner-words rows on this machine, or None when it keeps no ledger (GitHub, a fresh clone)."""
    try:
        with open(os.path.join(common_dir(root) or "", "loop", "owner-words.tsv"), encoding="utf-8") as handle:
            rows = [line.rstrip("\n").split("\t") for line in handle if line.strip()]
    except OSError:
        return None
    return {r[0]: r[4].split(",") for r in rows if len(r) >= 5} or None


def covers_subject(root, rows, record, subject):
    got = rows.get(record, [])
    return subject in got or bool(goal_slug(root)) and goal_slug(root) in got


def base_commit(root):
    try:
        with open(os.path.join(root, ".loop", "config.json"), encoding="utf-8") as handle:
            base = json.load(handle).get("base") or "main"
    except (OSError, ValueError, AttributeError):
        base = "main"
    for ref in ("origin/" + base, base):
        found = git(root, "merge-base", "HEAD", ref)
        if found:
            return found.strip()
    return None


def lowered(state):
    """Tags, risk lines or the levelling itself that this branch removed or lowered since its merge base."""
    at = base_commit(state.root)
    old_record = at and git(state.root, "show", "%s:.loop/%s" % (at, RECORD))
    if old_record is None or old_record is False:
        return []
    was = State(state.root, git(state.root, "show", "%s:.loop/%s" % (at, TABLE)) or "", old_record,
                git(state.root, "show", "%s:.loop/%s" % (at, RISKS)) or "")
    rows, out = ledger(state.root), []

    def allowed(why, subject):
        found = re.findall(r"owner:([A-Za-z0-9._-]+)", why)
        return any(rows is None or covers_subject(state.root, rows, r, subject) for r in found)

    def say(subject, what, name):
        out.append(Problem("LEVELS_LOWERED", subject, what + " since the merge base, with no owner record that covers it",
                           "restore it, or make the change with " + CODE + "level and --owner-record", name=name))
    if not state.levelled():
        if not any(allowed(why, "levels") for _, why in state.risks["off"].values()):
            say("levels", "the record and lvl-armed were removed", RECORD)
        return out
    entries = state.entries()

    def moved(key, tag):
        command = was.by_id.get(key, {}).get("command")
        return any(e["risk"] == tag and k not in was.by_id and state.by_id.get(k, {}).get("command") == command
                   for k, e in entries.items())
    gone = state.risks["removed"]
    for key, old in was.entries().items():
        if old["risk"] not in ("security", "private"):
            continue
        new = entries.get(key)
        if new and RANK.get(new["risk"], 0) >= RANK[old["risk"]]:
            continue
        why = (new or {}).get("reason", "") + " " + gone.get("entry:" + key, ("", ""))[1]
        if not allowed(why, key) and not (not new and moved(key, old["risk"])):
            say(key, "the %s tag was removed or lowered" % old["risk"], RECORD)
    for kind in ("requirement", "row", "label"):
        for key, (tag, _) in was.risks[kind].items():
            now = state.risks[kind].get(key)
            if RANK[tag] == 0 or now and RANK[now[0]] >= RANK[tag]:
                continue
            why = gone.get("%s:%s" % (kind, key), ("", ""))[1]
            renamed = kind == "row" and any(state.by_id.get(k, {}).get("command") == was.by_id.get(key, {}).get("command")
                                            for k, v in state.risks["row"].items() if v[0] == tag and k not in was.by_id)
            if not allowed(why, key) and not renamed:
                say(key, "the risk-data %s line was removed or lowered" % kind, RISKS)
    return out


def mark_path(root):
    found = git(root, "rev-parse", "--git-dir")
    return os.path.join(os.path.abspath(os.path.join(root, found.strip())), "loop-levels-pending.json") if found else None


def interrupted(root):
    path = mark_path(root)
    return Problem("LEVELS_INTERRUPTED", "", "an earlier write stopped between files (mark: %s)" % path,
                   CODE + "levels --fill completes it", name=RECORD) if path and os.path.exists(path) else None


def problems(state):
    found = (validate(state) if state.levelled() else []) + lowered(state)
    stopped = interrupted(state.root)
    return [stopped] + [p for p in found if p.code not in ("LEVELS_ORPHAN", "LEVELS_NO_ENTRY")] if stopped else found


def report(found, stream=sys.stderr):
    for item in found[:SHOWN]:
        print(item, file=stream)
    if len(found) > SHOWN:
        print("... and %d more (%d in all)" % (len(found) - SHOWN, len(found)), file=stream)


def shared(root, read):
    """Run read() while no writer is writing; a reader that can't open the lock reads without it."""
    try:
        handle = open(slots._lock_path(root, TABLE), "a")
    except (OSError, SystemExit):
        return read()
    with handle:
        fcntl.flock(handle, getattr(fcntl, "LOCK_SH", fcntl.LOCK_EX))
        return read()


def excepted_lines(state):
    return ["EXCEPTED %s: covered with no row list, by %s" % (row["id"], excuse(row)[3])
            for _, row in state.table if excuse(row) and not state.entries().get(row["id"], {}).get("covers")]


def check_read(root):
    """The gate of every command that must not run on a wrong table: prints each problem and exits 2."""
    present = any(os.path.exists(file_of(root, n)) for n in (RECORD, RISKS)) or MARKER in (text_of(root, TABLE) or "")

    def read():
        state = State(root)
        return state, problems(state)
    if not present:
        state, found = State(root), []
        found = lowered(state)
    else:
        try:
            state, found = shared(root, read)
        except Exception as error:  # one redacted line, never a traceback with file text
            sys.exit("LEVELS_UNEXPECTED: reading the levels failed (%s); nothing was written" % type(error).__name__)
    if found:
        report(found)
        sys.exit(2)
    if state.levelled():
        for line in excepted_lines(state):
            print(line, file=sys.stderr)


def l0_ids(root):
    """Rows recorded at L0: the local cover never leaves them to GitHub."""
    return {e["id"] for _, e in parse_record(text_of(root, RECORD))[0] if e["level"] == "L0"}
