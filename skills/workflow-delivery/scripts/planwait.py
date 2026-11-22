#!/usr/bin/env python3
"""DEL-22.3: a finished plan reply is not handed on while the level's reviews are still running. flow.py calls hold() through fit.plan_hold; it is a
module of its own so flow.py stays small. A review that failed, or a wait past the reviews' own limit, is NOT held: the plan goes ahead and says so."""
import contextlib
import io
import json
import os


def done(args, runs, reply, job):
    """True when the plan step's reply is there to be handed on: a session reply with its STEP line, or a headless job whose process has ended."""
    if os.path.exists(job):
        try:
            with open(job) as handle:
                os.kill(int(json.load(handle)["pid"]), 0)
            return False
        except (OSError, ValueError, KeyError, TypeError):
            return os.path.exists(reply)
    try:
        if not os.path.exists(reply[:-4] + ".asked"):  # a session reply counts only inside the attempt that asked for it
            return False
        with open(reply) as handle:
            return any(line.strip().upper().startswith(("STEP:", "STEP :")) for line in handle)
    except OSError:
        return False


def hold(args, runs, reply, job):
    """True (after printing RUNNING) when the reply is ready but `ready` says WAITING: the reviews are inside their time limit and not finished."""
    if args.step != "plan" or not done(args, runs, reply, job):
        return False
    import planstamps
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = planstamps.ready(args.slug, 0)
    if code == 0 and out.getvalue().startswith("WAITING"):
        print("RUNNING: the plan's reviews are still running (%s). Not handed on yet: run this same command again." % out.getvalue().strip())
        return True
    return False
