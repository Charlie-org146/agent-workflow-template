#!/usr/bin/env python3
"""The goal limits (GRD-2): max_active_goals, plan_pause_percent and min_free_memory_gb decide whether a new goal starts.
pool.py usage PERCENT records the plan usage; watch.py and checkin.py read the rest. A limit set to 0 is off."""
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graph  # noqa: E402
import sessions as se  # noqa: E402


def number(cfg, key, default):
    """A whole number setting; unset gives the default, 0 turns the limit off, anything unreadable gives the default."""
    value = cfg.get(key, default)
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else default


def active_limit(cfg):
    """Goals live at once: the smaller of `parallel` and `max_active_goals` (default 20); 0 means no limit."""
    caps = [n for n in (graph.parallel_of(cfg), number(cfg, "max_active_goals", 20)) if n]
    return min(caps) if caps else 0


def plan_usage():
    """The account's weekly plan usage in percent, as the operation session recorded it (`pool.py usage N`) in the last 12 hours, else None."""
    try:
        held = se.read(os.path.join(se.base(), "plan-usage.json"), {})
        age = time.time() - graph.parse_at(held["at"]).timestamp()
        return float(held["percent"]) if 0 <= age < 43200 else None
    except (KeyError, TypeError, ValueError, AttributeError, OSError):
        return None


def plan_pause(cfg):
    """Why no new goal starts, or '': weekly plan usage above plan_pause_percent (default 80, 0 turns it off). Unread usage never pauses."""
    limit, used = number(cfg, "plan_pause_percent", 80), plan_usage()
    return "plan usage %g%% is above plan_pause_percent %d%%; no new goal starts until it falls (PLAN_PAUSE)" % (used, limit) if limit and used is not None and used > limit else ""


def memory_hold(cfg):
    """Why no new goal starts, or '': free memory (workflow-regression's memory.free_gb, loaded by path) below min_free_memory_gb (default 4, 0 is off)."""
    need = cfg.get("min_free_memory_gb", 4)
    if isinstance(need, bool) or not isinstance(need, (int, float)) or need <= 0:
        return ""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("memory", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-regression", "scripts", "memory.py"))
        memory = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(memory)
        free = memory.free_gb()
    except Exception:
        return ""
    return "free memory %.1f GB is below min_free_memory_gb %g; no new goal starts (LOW_MEMORY)" % (free, need) if free is not None and free < need else ""


def memory_waits(root_loop, hours=1):
    """The lane waits for memory logged by the last `hours` (<git common dir>/loop/memory-waits.log), newest last."""
    try:
        with open(os.path.join(root_loop, "memory-waits.log")) as handle:
            lines = handle.read().splitlines()
    except OSError:
        return []
    cut = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 3600 * hours))
    return [line for line in lines if line[:20] >= cut]


def cmd_usage(args, cfg):
    se.write(os.path.join(se.base(), "plan-usage.json"), {"percent": args.percent, "at": graph.iso(datetime.datetime.now(datetime.timezone.utc))})
    print("PLAN USAGE %g%% recorded: %s" % (args.percent, plan_pause(cfg) or "no pause"))
    return 0
