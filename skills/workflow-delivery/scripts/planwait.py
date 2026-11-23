#!/usr/bin/env python3
"""DEL-22.3: a finished plan reply is not handed on while the level's reviews are still running. flow.py calls hold() through fit.plan_hold; it is a
module of its own so flow.py stays small. A review that failed, or a wait past the reviews' own limit, is NOT held: the plan goes ahead and says so."""
import contextlib
import io
import os
import time


def done(args, runs, reply, job):
    """True when a hand-off could happen in this call: a headless plan step with a job (its planner may end at any moment, even mid-wait, so the check cannot
    depend on its process: no pid, nothing to reuse), or a session reply with its STEP line inside the attempt that asked for it."""
    if os.path.exists(job):
        return True
    try:
        if not os.path.exists(reply[:-4] + ".asked"):
            return False
        with open(reply) as handle:
            return any(line.strip().upper().startswith(("STEP:", "STEP :")) for line in handle)
    except OSError:
        return False


def waiting(slug):
    import planstamps
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = planstamps.ready(slug, 0)
    return out.getvalue().strip() if code == 0 and out.getvalue().startswith("WAITING") else ""


def hold(args, runs, reply, job):
    """True (after printing RUNNING) when a hand-off could happen but the reviews are still WAITING inside their limit. With a job it waits here, up to the
    call's own --wait, for the reviews; reviews only move toward READY, so a call that finds them READY may hand on whenever its planner ends."""
    if args.step != "plan" or not done(args, runs, reply, job):
        return False
    end = time.time() + (args.wait if os.path.exists(job) else 0)
    left = waiting(args.slug)
    while left and time.time() < end:
        time.sleep(min(2, max(end - time.time(), 0.1)))
        left = waiting(args.slug)
    if left:
        print("RUNNING: the plan's reviews are still running (%s). Not handed on yet: run this same command again." % left)
        return True
    return False
