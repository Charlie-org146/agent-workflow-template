#!/usr/bin/env python3
"""DEL-19's one step list, the step log and the cause list, in one file every skill reads (shared/steps.py in a pack).

STEPS is the list; LEGACY maps the labels the run records already hold. transition() is the one function that keeps a record's
step clock and its start/end log lines; goal.save calls it, and commit() is the shared writer for the other record writers.
entries() reads the persisted lines back as exactly eight rows. Stdlib only; nothing here imports another script."""
import datetime
import json
import os
import re
import subprocess
try:
    import fcntl
except ImportError:  # Windows: lanekit.py's own shim, loaded the way scan() loads private.py
    import sys
    for _dir in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflow-delivery", "scripts"),
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "workflow-delivery", "scripts")):
        if os.path.exists(os.path.join(_dir, "lanekit.py")):
            sys.path.insert(0, os.path.normpath(_dir))
            break
    import importlib
    fcntl = importlib.import_module("lanekit").fcntl

STEPS = ("freeze", "plan", "build", "quick checks", "tests", "merge", "after the merge", "release")
LEGACY = {"idea": "freeze", "plan": "plan", "build": "build", "checks": "quick checks", "review": "tests", "qa": "tests",
          "ship": "tests", "pr": "merge", "release": "release"}
END = re.compile(r"^(\S+) end (.+?): (\d+)m active, tokens (.+?), (.*)$")
START = re.compile(r"^(\S+) (?:start|began) (.+)$")
POST = ("after the merge", "release")  # run after the pull request merged: the record is done, the clock still runs
CODE = re.compile(r"\(([A-Z][A-Z0-9_]{2,})\)\s*$")
KEY = re.compile(r"^(%s):([A-Z][A-Z0-9_]{2,}|failed)$" % "|".join(re.escape(n) for n in STEPS))


def name_of(label):
    return LEGACY.get(label, label)


def label(text):
    """A record's label as the board shows it: the old label kept, the DEL-19 name beside it when they differ."""
    return text if name_of(text) == text else "%s (%s)" % (text, name_of(text))


def valid(label):
    return label in STEPS or label in LEGACY or label in (None, "", "-")


def check(old, new):
    """Refuse a step label that is not on the list and differs from the saved one (an old record never blocks other saves)."""
    if new != old and not valid(new):
        raise SystemExit("REFUSED: %r is not a step. Fix: use one of %s (SC_STEP)." % (new, ", ".join(STEPS)))


def when(text):
    return datetime.datetime.strptime(text[:19], "%Y-%m-%dT%H:%M:%S")


def spent(state):
    held = state.get("tokens")
    if not isinstance(held, dict):
        return None
    total = 0
    for value in held.values():
        total += sum(int(value.get(k) or 0) for k in ("input", "cache_write", "output", "reported")) if isinstance(value, dict) \
            else (value if isinstance(value, int) and not isinstance(value, bool) else 0)
    return total


def eff(state):
    """The step the clock follows: a done goal still on the label release, before any release was pushed, is waiting in merge; one left unreleased has no step."""
    label = state.get("step")
    if label == "release" and state.get("status") == "done" and not state.get("release_pushed") and state.get("release") != "cut":
        return None if state.get("release") == "leave" else "pr"  # left unreleased: the merge is over and nothing runs after it
    return label


def transition(old, new, at):
    """Update new's step clock and append the start/end lines for the change from old to new (old is the record on disk)."""
    check(old.get("step"), new.get("step"))
    log = new.setdefault("log", [])
    clock = dict(new.get("step_clock") or old.get("step_clock") or {})
    if clock.get("since") and (old.get("status") == "running" or name_of(clock.get("step")) in POST + ("merge",)):
        clock["active_s"] = int(clock.get("active_s") or 0) + max(0, int((when(at) - when(clock["since"])).total_seconds()))
    clock["since"] = at
    step, status = eff(new), new.get("status")
    ended = ""
    if clock.get("step") and (step != clock["step"] or status in ("stopped", "failed") or status == "done" and name_of(step) != "merge"):
        used, then = spent(new), clock.get("tok0")
        token = "not reported" if used is None or then is None or used <= then else str(used - then)
        result = {"done": "done", "stopped": "stopped", "failed": "failed"}.get(status) or "moved on"
        log.append("%s end %s: %dm active, tokens %s, %s" % (at, clock["step"], int(clock.get("active_s") or 0) // 60, token, result))
        ended, clock = clock["step"], {"since": at}
    if step and (status in ("running", None) or name_of(step) in POST + ("merge",) and status == "done") and not clock.get("step") and step not in ("-", "", ended):
        if not (log and re.search(r"(?:start|began) %s$" % re.escape(step), log[-1])):
            log.append("%s began %s" % (at, step))
        clock.update(step=step, active_s=0, tok0=spent(new))
    new["step_clock"] = clock
    return bool(status in ("stopped", "failed") and add_cause(new, clock_step(old, new), new.get("finding") or new.get("release_error") or ""))


def clock_step(old, new):
    """The step a stop or failure belongs to: the step the record is on, a release not yet pushed counting as the merge."""
    label = new.get("step") or old.get("step") or "-"
    return "pr" if label == "release" and not new.get("release_pushed") and new.get("release") != "cut" else label


def entries(state):
    """Exactly eight rows, one per step: state, start, end, minutes (all attempts), tokens, result, attempts, causes."""
    rows = {name: {"step": name, "state": "not run", "start": "", "end": "", "minutes": 0, "tokens": "not reported", "result": "",
                   "attempts": 0, "attempt": 0, "causes": []} for name in STEPS}
    last = {}
    for line in state.get("log") or []:
        begin, finish = START.match(line), END.match(line)
        if finish:
            at, label, mins, tokens, result = finish.groups()
            row = rows.get(name_of(label))
            if row:
                row.update(end=at, minutes=row["minutes"] + int(mins), result=result)
                row["tokens"] = tokens if tokens != "not reported" else row["tokens"]
                row["state"] = "ran"
        elif begin and name_of(begin.group(2)) in rows:
            row = rows[name_of(begin.group(2))]
            row.update(state="open", start=row["start"] or begin.group(1), attempts=row["attempts"] + 1, attempt=row["attempts"] + 1)
    for cause in state.get("causes") or []:
        row = rows.get(name_of(cause.get("step")))
        if row:
            row["causes"].append(cause.get("key") or cause.get("text") or "")
    return [rows[name] for name in STEPS]


def merge(disk, state, was=None):
    """goal.save's per-key merge: the caller's changed keys over the disk record, its removed keys dropped, the log a union."""
    if was is None:  # nothing recorded what was loaded: the caller's keys are taken as they stand
        merged = dict(state)
    else:
        merged = dict(disk, **{k: v for k, v in state.items() if k not in was or was[k] != v})
        merged = {k: v for k, v in merged.items() if k in state or k not in was}
    have = disk.get("log") or []
    merged["log"] = have + [line for line in state.get("log") or [] if line not in have]
    return merged


def commit(path, state, at):
    """The shared writer: lock the record, merge over the disk record, run transition, write atomically; state gets the result.
    The step clock and the cause list belong to the disk record, so a stale copy never overwrites them."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            disk = json.load(open(path))
        except (OSError, ValueError):
            disk = {}
        merged = merge(disk, state)
        for key in ("step_clock", "causes"):
            if key in disk:
                merged[key] = disk[key]
        transition(disk, merged, at)
        temp = "%s.%d.tmp" % (path, os.getpid())
        with open(temp, "w") as handle:
            json.dump(merged, handle, indent=2)
        os.replace(temp, path)
    state.clear()
    state.update(merged)


def add_cause(state, step, text=""):
    """Record one structured cause {step, key}: the key is the step plus the CODE a refusal ends with, else ':failed'. No free text
    is kept. True when the key is new."""
    found = CODE.search(text or "")
    name = name_of(step)
    key = "%s:%s" % (name if name in STEPS else STEPS[0], found.group(1) if found else "failed")  # a stop before any step has run belongs to freeze
    held = state.setdefault("causes", [])
    if not KEY.match(key) or any(item.get("key") == key for item in held):
        return False
    held.append({"step": key.split(":")[0], "key": key})
    return True


def summary(state):
    """The '### Steps' block: per step minutes, tokens, failures and top cause, worst first."""
    rows = [r for r in entries(state) if r["state"] != "not run"]
    rows.sort(key=lambda r: (-r["minutes"], -len(r["causes"])))
    lines = ["### Steps", ""]
    for row in rows:
        cause = " (%s)" % row["causes"][0] if row["causes"] else ""
        lines.append("- %s: %dm, tokens %s, %s%s" % (row["step"], row["minutes"], row["tokens"], row["result"] or row["state"], cause))
    return "\n".join(lines) + "\n" if rows else "### Steps\n\n- no step is recorded\n"
