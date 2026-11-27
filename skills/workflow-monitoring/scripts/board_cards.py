#!/usr/bin/env python3
"""The board's cards (BOARD-1, 2, 3): one card per release, task and goal, and the three views over them.

Pure data in, text out: no model call, no network, no write. `cards(...)` builds them, `group_by(...)` groups them.
A goal card wraps the lines the board showed for that goal before: its mark line, its done-line bars, its ETA text and its stop cause.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto  # noqa: E402
import board_lines  # noqa: E402
import board_log  # noqa: E402
import board_status  # noqa: E402

OVER = ("done", "merged", "queued", "retired", "replaced")  # states that are never stale


def setting(cfg, key, default, low=1, high=None):
    """A whole number in low..high from a repo's settings. A value that is not a number or is out of range is refused loudly:
    one line on stderr names the setting, the value and the range, and the default is used. A setting that is not there is the default."""
    if key not in (cfg or {}):
        return default
    raw = cfg[key]
    try:
        value = int(str(raw).strip())
    except ValueError:
        value = None
    if value is not None and value >= low and (high is None or value <= high):
        return value
    where = "from %d to %d" % (low, high) if high is not None else "of %d or more" % low
    sys.stderr.write("SETTING %s: %r is not a whole number %s; using the default %s\n" % (key, raw, where, default))
    return default


def stale(when, state, at, max_age):
    """Older than max_age minutes (more, not equal); no time or a finished or waiting-to-start state is never stale."""
    return bool(when and state not in OVER and (at - when).total_seconds() > max_age * 60)


def newest(times):
    times = [t for t in times if t]
    return max(times) if times else None


def goal_lines(item, run, at):
    out = [board_status.goal_line(item)] + board_lines.bars(item, at)
    if run and isinstance(run.get("eta"), dict):
        out.append("    " + auto.eta_text(run, at))
    if run and run.get("status") in ("failed", "stopped"):
        key, words, reset = board_lines.cause(run)
        out.append("    %s%s" % (words, " until " + reset if reset else ""))
    return out


def cards(items, runs, task_rows, batches, at, root=None, max_age=5):
    """items: the board's goal items; runs: run records; task_rows: board_tasks.tasks(); batches: {release: [goal slugs]}."""
    by = {r.get("slug"): r for r in runs}
    when = {s: board_log.stamp((by.get(s) or {}).get("updated")) for s in by}
    release_of = {s: name for name, slugs in batches.items() for s in slugs}
    task_of, out = {}, []
    for t in task_rows:
        if t.get("state") == "replaced":
            continue
        for g in t["goals"]:
            task_of.setdefault(g[0] if isinstance(g, tuple) else g, t["slug"])
    for item in items:
        slug, run = item["slug"], by.get(item["slug"])
        state = item.get("mark") or (run or {}).get("status") or "queued"
        out.append({"id": "goal:" + slug, "kind": "goal", "name": slug, "state": state, "eta_of": slug, "task": task_of.get(slug, "none"),
                    "release": release_of.get(slug, "no release"), "machine": item.get("machine") or (run or {}).get("machine") or "",
                    "time": when.get(slug), "stale": stale(when.get(slug), state, at, max_age), "lines": goal_lines(item, run, at)})
    for t in task_rows:
        slugs = [g[0] if isinstance(g, tuple) else g for g in t["goals"]]
        time = newest(when.get(s) for s in slugs)
        rel = next((release_of[s] for s in slugs if s in release_of), "no release")
        out.append({"id": "task:" + t["slug"], "kind": "task", "name": t["name"], "state": t["state"], "eta_of": t["slug"], "task": t["slug"],
                    "release": rel, "machine": "", "time": time, "stale": stale(time, t["state"], at, max_age),
                    "lines": ["%s: %s, %d of %d goals finished" % (t["name"], t["state"], t.get("done", 0), len(slugs))]})
    for name, slugs in batches.items():
        marks = {(next((i for i in items if i["slug"] == s), {}).get("mark") or (by.get(s) or {}).get("status") or "queued") for s in slugs}
        state = "done" if marks and marks <= {"done", "merged"} else "waiting" if "waiting" in marks else "running" if marks & {"running", "held"} else "idle"
        time = newest(when.get(s) for s in slugs)
        out.append({"id": "release:" + name, "kind": "release", "name": name, "state": state, "eta_of": name, "task": "", "release": name,
                    "machine": "", "time": time, "stale": stale(time, state, at, max_age),
                    "lines": ["release %s: %s, %d goals" % (name, state, len(slugs))]})
    return out


def group_by(found, view):
    """{group: [cards]}: by release (the release, its tasks and goals), by task (the task and its goals) or by goal (one card each)."""
    out = {}
    for c in found:
        if view == "release":
            key = c["release"]
        elif view == "task":
            key = c["task"] if c["kind"] != "release" else None
        else:
            key = c["name"] if c["kind"] == "goal" else None
        if key:
            out.setdefault(key, []).append(c)
    for key in out:  # the group's own card first, then tasks, then goals
        out[key].sort(key=lambda c: {"release": 0, "task": 1, "goal": 2}[c["kind"]])
    return out


VOLATILE = ("generated", "next_at")  # clock fields: a refresh that changed nothing else leaves the file alone (BOARD-5)


def same(path, text):
    """True when the file already holds this text, JSON compared without its clock fields."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            old = handle.read()
    except (OSError, ValueError):
        return False
    if old == text:
        return True
    try:
        keep = lambda raw: {k: v for k, v in json.loads(raw).items() if k not in VOLATILE}
        return keep(old) == keep(text)
    except (ValueError, AttributeError):
        return False


def card_list(rows, deps, at, repos, setting_of):
    """The cards for board.json, per repo (repos: board.followed()): a failure to build them never stops the board."""
    try:
        import board_tasks
        out = []
        for name, path, base in repos:
            mine = [r for r in rows if r["repo"] == name]
            items = [{"mark": r["status"], "slug": r["slug"], "left": r.get("left"), "machine": r.get("machine") or "", "bars": []} for r in mine]
            runs = [{"slug": r["slug"], "status": r["status"], "updated": r.get("last") or ""} for r in mine]
            batches = {}
            for slug in [x["slug"] for x in mine] + [d["slug"] for d in deps if d["repo"] == name]:
                batches.setdefault(board_status.release_of(path, slug), []).append(slug)
            batches.pop("no release", None)
            for c in cards(items, runs, board_tasks.tasks(path, runs), batches, at, path, setting_of(path, "board_max_age", 5)):
                c["repo"], c["time"] = name, c["time"].strftime("%Y-%m-%dT%H:%M:%SZ") if c.get("time") else ""
                out.append(c)
        return out
    except Exception as err:  # noqa: BLE001
        return [{"id": "cards:error", "kind": "error", "name": type(err).__name__}]
