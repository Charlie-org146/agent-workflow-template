#!/usr/bin/env python3
"""DEL-22's stamp readers, split out of planlevel.py to keep every script under 19,000 bytes: the runner's stamps for this attempt, the session reviews'
one-file-per-review stamps, the median for the 2x flag, and the scripted `ready` wait. planlevel.py is imported lazily for its helpers."""
import json
import os
import time


def pl():
    import planlevel
    return planlevel


def session_stamps(slug):
    """The session path: one small file per review, <slug>.stamp-<review>.json, each written only by that review (no shared file, so nothing races or is lost),
    and read only when its attempt is the current one. Returns {review: {"started", "ended"}}."""
    attempt, out, runs = pl().sidecar(slug).get("attempt"), {}, pl().runs_dir()
    for name in os.listdir(runs):
        if name.startswith(slug + ".stamp-") and name.endswith(".json"):
            try:
                with open(os.path.join(runs, name)) as handle:
                    row = json.load(handle)
                if row.get("attempt") == attempt and attempt is not None and isinstance(row.get("review"), str):
                    out[row["review"]] = row
            except (OSError, ValueError, AttributeError):
                continue
    return out


def stamps_for(slug):
    try:
        with open(os.path.join(pl().runs_dir(), slug + ".plan-reviews.json")) as handle:
            found = json.load(handle)
        rows = found["reviews"]
        ok = found.get("goal") == slug and found.get("attempt") == pl().sidecar(slug).get("attempt") and found.get("attempt") is not None and len(rows) <= pl().MAX_REVIEWS and all(isinstance(r.get("started"), (int, float)) and isinstance(r.get("ended"), (int, float)) and 0 <= r["ended"] - r["started"] < 1e6 for r in rows)
        return (found.get("source", "runner"), rows) if ok else ("", [])
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return "", []


def median(values):
    values = sorted(values)
    return values[len(values) // 2] if len(values) % 2 else (values[len(values) // 2 - 1] + values[len(values) // 2]) / 2


def ready(slug, wait):
    """READY once the runner's file for this attempt is there, or every review the ask named has stamped its end; else WAITING with the seconds left of
    the reviews' own limit, counted from the ask (the exit status is 3 once that limit is over). A goal with no ordered reviews is READY at once.
    `wait` polls inside this one command, 240 seconds at most."""
    end = time.time() + wait
    while True:
        held = pl().sidecar(slug)
        path = os.path.join(pl().runs_dir(), slug + ".plan.json")
        if os.path.exists(path) and not held:  # a record that is there but cannot be read is not "no reviews ordered"
            print("NOT READY (the goal's plan record cannot be read)")
            return 3
        names = held.get("names")
        try:  # a goal whose state carries a plan level was ordered reviews: a missing record, or one with no names, is not "none were ordered"
            with open(os.path.join(pl().runs_dir(), slug + ".json")) as handle:
                leveled = isinstance(json.load(handle).get("plan"), dict)
        except FileNotFoundError:
            leveled = False
        except (OSError, ValueError, AttributeError):  # a run record that is there but cannot be read: not "no reviews were ordered"
            print("NOT READY (the goal's run record cannot be read)")
            return 3
        if leveled and not names:
            print("NOT READY (this goal has a plan level but no ask recorded its reviews)")
            return 3
        if not names:  # no ask recorded, or a goal frozen before DEL-22: no reviews were ordered
            print("READY (no reviews were ordered for this goal)")
            return 0
        done = {n for n, v in session_stamps(slug).items() if v.get("ended")}
        rows = stamps_for(slug)[1]
        bad = [r.get("name") for r in rows if r.get("failed")]
        if rows and not bad:
            print("READY")
            return 0
        if bad:  # a review whose command failed is not a finished review (the plan goes ahead at full depth and says so)
            print("NOT READY (review%s failed: %s)" % ("s" if len(bad) > 1 else "", ", ".join(bad)))
            return 3
        if names and set(names) <= done:
            print("READY")
            return 0
        left = int(pl().RUNNER_LIMIT - (time.time() - (held.get("asked_at") or time.time())))
        if time.time() >= end or left <= 0:
            print("WAITING (%d seconds left of the reviews' own limit)" % max(left, 0))
            return 0 if left > 0 else 3
        time.sleep(min(5, max(end - time.time(), 0.1)))
