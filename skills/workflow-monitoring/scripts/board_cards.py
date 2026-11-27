#!/usr/bin/env python3
"""The board's cards (BOARD-1, 2, 3): one card per release, task and goal, and the three views over them.

Pure data in, text out: no model call, no network, no write. `cards(...)` builds them, `group_by(...)` groups them.
A goal card wraps the lines the board showed for that goal before: its mark line, its done-line bars, its ETA text and its stop cause.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto  # noqa: E402
import board_lines  # noqa: E402
import board_log  # noqa: E402
import board_status  # noqa: E402

OVER = ("done", "merged", "queued", "retired", "replaced")  # states that are never stale


def setting(cfg, key, default):
    """A positive whole number from a repo's settings, else the default."""
    try:
        value = int(str((cfg or {}).get(key, default)).strip())
    except ValueError:
        return default
    return value if value > 0 else default


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


def cards(items, runs, task_rows, batches, at, root=None, max_age=120):
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
