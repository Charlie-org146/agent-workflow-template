#!/usr/bin/env python3
"""The task list (DEL-23): the briefs in .loop/tasks with their state, and the lines that show them on the live board and
in the check-in. parse_at, age, quoted and blocks are moved here whole from live_board.py and checkin.py to keep each
script under its size line."""
import datetime
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_lines  # noqa: E402
import board_page  # noqa: E402
import board_status as bs  # noqa: E402
import graph  # noqa: E402

FLOW, current = bs.FLOW, bs.current



X = r"\x00-\x1f\x7f-\x9f\u2028\u2029\u202a-\u202e\u2066-\u2069"


def task_rows(root):  # DEL-23: one row per brief in .loop/tasks; a bad brief is named, never hidden
    rows = []
    for f in sorted(glob.glob(os.path.join(glob.escape(root), ".loop", "tasks", "*.md"))):
        slug = os.path.basename(f)[:-3]
        try:
            text, err = open(f, encoding="utf-8").read(), ""
        except (OSError, ValueError):
            text, err = "", "brief unreadable: check its permissions"
        kv = {m[1].lower(): m[2].strip() for m in re.finditer(r"^- +(feature|release|goals|needs|replaced by|source) *: *(.*)$", text, re.M | re.I)}
        w = lambda k: re.findall("[^%s, |]{1,60}" % X, kv.get(k, ""))
        name = re.sub("[%s|]" % X, " ", text.split("\n")[0].lstrip("# "))[:100].strip()
        miss = [k for k in ("feature", "release", "source") if not kv.get(k)]
        rows.append(dict(slug=slug, name=name or slug, goals=w("goals"), needs=w("needs"), by=kv.get("replaced by", ""),
                         note=err or f"incomplete brief: add its {', '.join(miss)} line" * bool(miss or not name)))
    return rows


def tasks(root, runs, gone=()):  # DEL-23: the briefs with state (replaced > done > running > waiting > queued)
    by, rows = {r["slug"]: r for r in runs}, task_rows(root)
    ids = {t["slug"]: t for t in rows}
    end = lambda s: s in gone or graph.merged(by.get(s))
    st = lambda s: by[s].get("status")
    live = lambda s: s in by and not end(s) and st(s) != "queued"

    def hop(s):
        for _ in range(5): s = ids.get(s, {}).get("by") or s
        return s

    for t in rows:
        g = t["goals"]
        t["state"] = "replaced" if t["by"] else "done" if g and all(map(end, g)) else "running" if any(live(s) and st(s) not in ("waiting", "failed", "stopped") for s in g) else "waiting" if any(map(live, g)) else "queued"
    cut = board_lines.cycled([dict(slug=t["slug"], depends=[hop(s) for s in t["needs"]]) for t in rows])
    for t in rows:
        bad = [ids[s]["name"] if s in ids else s + " (no brief)" for s in map(hop, t["needs"]) if s not in ids or ids[s]["state"] != "done"]
        if t["state"] == "queued" and (bad or t["slug"] in cut):
            t["state"], t["note"] = "waiting", t["note"] + "; " * bool(t["note"]) + ("cycle" * (t["slug"] in cut) or "needs " + ", ".join(bad))
        t["done"] = sum(map(end, t["goals"]))
        t["goals"] = [(s, end(s), by[s] if live(s) else None) for s in t["goals"]]
    return rows


def task_lines(root, runs, at, gone=()):  # DEL-23: each task by name with state, goals finished and ETA, then its goals and their step
    import moved_mon
    try:
        out = ["", "Tasks"]
        for t in tasks(root, runs, gone):
            live = [r for _, _, r in t["goals"] if r]
            left = [bs.left_time(r, runs, at, root) for r in live]
            eta = "-" if not live else "awaiting merge" if all(r.get("status") == "done" for r in live) else "?" if None in left else board_page.span(max(left))
            out.append(f"- {t['name']}: {t['state']}{t['note'] and ' (%s)' % t['note']}, {sum(f for _, f, _ in t['goals'])} of {len(t['goals'])} goals finished, ETA {eta}")
            out += ["    %s %s" % (s, "finished" if f else "not started" if not r else "awaiting merge" if r.get("status") == "done" else moved_mon.shown(r, FLOW[current(r)])[0]) for s, f, r in t["goals"]]
    except Exception as e:  # never stop the check-in or the board
        return ["", "Tasks", "- tasks unavailable: " + type(e).__name__]
    return out if len(out) > 2 else []


def parse_at(text):
    """A recorded time as an aware UTC datetime (naive counts as UTC), or None when it is missing or bad."""
    try:
        found = datetime.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None
    return found if found.tzinfo else found.replace(tzinfo=datetime.timezone.utc)


def age(text, at):
    """How long ago a recorded time was: Nm under an hour, Nh under two days, else Nd; '' when the time is unknown."""
    then = parse_at(text)
    if not then or not at:
        return ""
    minutes = max(0, int((at - then).total_seconds() // 60))
    return "%dm" % minutes if minutes < 60 else "%dh" % (minutes // 60) if minutes < 48 * 60 else "%dd" % (minutes // 1440)


def quoted(words):
    return " / ".join('"%s"' % w for w in words)


def blocks(section):
    found, name = {"": []}, ""
    for line in section.splitlines():
        head = re.match(r"^\s*==\s*(.+?)\s*==\s*$", line)
        name = head.group(1) if head else name
        found.setdefault(name, []).append("" if head else line)
    return {key: re.sub(r"-\s*\n\s*", "-", "\n".join(rows)) for key, rows in found.items()}
