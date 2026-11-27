#!/usr/bin/env python3
"""One review (DLF-1.3): a marked goal's decisions after its start.

Imported by the delivery, monitoring and release scripts; it has no command of its own. The decisions of one goal are a
file of their own beside its run record, <slug>.decisions.jsonl, one JSON entry a line. It is only ever added to, under
its own lock, so a writer of the whole run record cannot lose an entry. A permanent stop is one of those entries.
Standard library only.
"""
import contextlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lanekit  # noqa: E402

LIVE = ("queued", "running", "waiting")


def ledger(runs, slug):
    return os.path.join(runs, slug + ".decisions.jsonl")


def refuse(text, code):
    sys.exit("REFUSED: %s (%s)" % (text, code))


@contextlib.contextmanager
def locked(runs, slug):
    with open(os.path.join(runs, slug + ".decisions.lock"), "w") as lock:
        lanekit.fcntl.flock(lock, lanekit.fcntl.LOCK_EX)
        yield


def parse(slug, text):
    """The entries of a ledger's text; a torn, unreadable or misnumbered line refuses."""
    out = []
    for number, line in enumerate(text.split("\n")[:-1], 1):
        try:
            entry = json.loads(line)
        except ValueError:
            entry = None
        if not isinstance(entry, dict) or entry.get("n") != number or not entry.get("kind"):
            refuse("%s's decisions file is unreadable at line %d. Fix: restore it from its last good copy; nothing was changed"
                   % (slug, number), "ONE_REVIEW_LEDGER")
        out.append(entry)
    if not out or not text.endswith("\n"):
        refuse("%s's decisions file ends in the middle of a line or is empty. Fix: restore it from its last good copy" % slug,
               "ONE_REVIEW_LEDGER")
    return out


def entries(runs, slug):
    try:
        with open(ledger(runs, slug), encoding="utf-8", newline="") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError):
        refuse("%s is a one-review goal and its decisions file %s can't be read. Fix: restore it beside the run record"
               % (slug, ledger(runs, slug)), "ONE_REVIEW_LEDGER")
    return parse(slug, text)


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write(handle, entry):
    handle.write(json.dumps(entry, sort_keys=True) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def create(runs, slug, by):
    """Start a marked goal's ledger; one that exists is never replaced."""
    with locked(runs, slug):
        try:
            handle = open(ledger(runs, slug), "x", encoding="utf-8", newline="")
        except FileExistsError:
            refuse("%s already has a decisions file; it is never made again" % slug, "ONE_REVIEW_LEDGER")
        with handle:
            _write(handle, {"n": 1, "kind": "mark", "at": stamp(), "by": by})


def add(runs, slug, kind, **data):
    """Add one entry and return its number."""
    with locked(runs, slug):
        number = len(entries(runs, slug)) + 1
        with open(ledger(runs, slug), "a", encoding="utf-8", newline="") as handle:
            _write(handle, dict(data, n=number, kind=kind, at=stamp()))
    return number


def marked(runs, state):
    return bool(state.get("one_review")) or os.path.exists(ledger(runs, state.get("slug") or ""))


def require(runs, state):
    """A marked goal's entries, or none for an unmarked one; a marked goal with no readable ledger refuses."""
    return entries(runs, state["slug"]) if marked(runs, state) else []


def stopped(found):
    return next((e.get("why") or "stopped" for e in found if e["kind"] == "stop"), "")


def stop(runs, slug, why, by):
    return add(runs, slug, "stop", why=why, by=by)


def hold(runs, state):
    """Called by every writer of a run record before it writes: a stopped goal never becomes queued, running or waiting."""
    why = stopped(require(runs, state)) if state.get("status") in LIVE + ("done",) else ""
    if why:
        refuse("%s was stopped for good: %s. It can't be set %s. Fix: retire it, or start a new goal"
               % (state["slug"], why, state["status"]), "ONE_REVIEW_STOPPED")


SIDE = (("decisions", "{slug}.decisions.jsonl"), ("extra", "{slug}.extra.json"), ("plan_review", "../redteam/plan-{slug}.json"))


def pack(runs, state):
    """The files that travel with a handover. A marked goal whose ledger can't be read refuses."""
    require(runs, state)
    out = {}
    for key, name in SIDE:
        path = os.path.join(runs, name.format(slug=state["slug"]))
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as handle:
                out[key] = handle.read()
    return out


def unpack(runs, state, files):
    """Put a handover's files beside the record taken here; a marked record that came without its ledger refuses, and a
    ledger already here is replaced only by one that continues it."""
    slug, files = state["slug"], files if isinstance(files, dict) else {}
    text = files.get("decisions")
    if (state.get("one_review") or os.path.exists(ledger(runs, slug))) and not isinstance(text, str):
        refuse("the handover of %s carries no decisions file, and it is a one-review goal. Fix: hand it over again from the "
               "machine that holds its record" % slug, "ONE_REVIEW_LEDGER")
    if isinstance(text, str):
        parse(slug, text)
        if os.path.exists(ledger(runs, slug)):
            with open(ledger(runs, slug), encoding="utf-8", newline="") as handle:
                if not text.startswith(handle.read()):
                    refuse("the handover of %s carries decisions that don't continue the ones kept here" % slug, "ONE_REVIEW_LEDGER")
    os.makedirs(runs, exist_ok=True)
    for key, name in SIDE:
        if isinstance(files.get(key), str):
            path = os.path.join(runs, name.format(slug=slug))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path + ".tmp", "w", encoding="utf-8", newline="") as handle:
                handle.write(files[key])
            os.replace(path + ".tmp", path)
