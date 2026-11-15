#!/usr/bin/env python3
"""The merge slot (GRD-2): a goal whose pr lane has started holds it until it merges or fails, so the merge.py of a goal
that started its lane later waits for it instead of making the lane's base move. graph.pr_queue(op, runs, slug) forwards
here: hold and free (goal.py pr, merge.py), before (the earliest other holder that started first, or "")."""
import os
import time


def folder(runs):
    return os.path.join(os.path.dirname(runs), "pr-slots")


def pr_hold(runs, slug):
    """Take the slot at the lane's start (the first start time stays) and keep it fresh on each call."""
    path = os.path.join(folder(runs), slug)
    os.makedirs(folder(runs), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as handle:
            handle.write(str(time.time_ns()))
    os.utime(path)


def pr_free(runs, slug):
    try:
        os.unlink(os.path.join(folder(runs), slug))
    except OSError:
        pass


def pr_before(runs, slug):
    """The other goal that holds the slot and started its lane before slug's, else "". A holder silent for
    LOOP_MERGE_LOCK_SECONDS (1800) is dropped; a goal with no slot of its own waits for none."""
    limit, held = int(os.environ.get("LOOP_MERGE_LOCK_SECONDS") or 1800), []
    try:
        for name in os.listdir(folder(runs)):
            path = os.path.join(folder(runs), name)
            if time.time() - os.path.getmtime(path) > limit:
                os.unlink(path)
            else:
                held.append((int(open(path).read()), name))
    except (OSError, ValueError):
        pass
    mine = dict((n, j) for j, n in held).get(slug)
    return min([(j, n) for j, n in held if n != slug and j < mine] or [(0, "")])[1] if mine else ""
