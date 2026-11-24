#!/usr/bin/env python3
"""ASZ-1.3: the owner's size line and the board's size line. `sizeline.py set SLUG SIZE --owner-record ID` raises a goal's size
(up only, with the owner's words, never under a safety class; sizing.override does the work); `sizeline.py show SLUG` prints
`SIZE <size> (<reason>) checks: ...` and `owner: <id>` when an owner line changed it. line(run) is the one-line form the board
uses (board_tasks.py); alone() lists goals that belong to no task brief. The delivery modules are loaded by path when a command
runs, so the script runs alone (--help) with nothing but its own folder."""
import importlib
import os
import sys

DELIVERY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts")
USAGE = "usage: sizeline.py show SLUG | sizeline.py set SLUG small|medium|large --owner-record ID"


def line(run, width=70):
    """The goal's size line, '' when it has no stored size; the reason is cut to one line (the full text is in show)."""
    sized = (run or {}).get("sized")
    if not sized:
        return ""
    why = " ".join(str(sized.get("reason", "")).split())
    checks = ", ".join("%s %s" % (c, v["form"]) for c, v in sized.get("checks", {}).items() if c in ("plan-review", "red-team", "review"))
    owner = (sized.get("owner") or {}).get("record")
    return "SIZE %s (%s) checks: %s%s" % (sized["size"], why if len(why) <= width else why[:width - 3] + "...", checks, "; owner: " + owner if owner else "")


def tail(run):
    return " | " + line(run) if line(run) else ""


def alone(runs, attached):
    """Lines for goals that no task brief lists."""
    return ["- %s: %s" % (r["slug"], line(r)) for r in runs if line(r) and r["slug"] not in attached]


def main(argv):
    if argv[:1] not in (["show"], ["set"]):
        print(USAGE)
        return 0 if argv[:1] in (["-h"], ["--help"]) else 1
    args, record = argv[1:], ""
    if "--owner-record" in args[:-1]:
        at = args.index("--owner-record")
        record, args = args[at + 1], args[:at] + args[at + 2:]
    rest = args
    if len(rest) != (1 if argv[0] == "show" else 2):
        print(USAGE)
        return 1
    sys.path.insert(0, DELIVERY)
    try:
        goal, sizing = importlib.import_module("goal"), importlib.import_module("sizing")
    except ImportError:
        print("REFUSED: sizeline needs workflow-delivery beside it. Fix: install it (SIZING_NO_DELIVERY)")
        return 2
    slug = rest[0]
    state = goal.load(slug)
    sized = state.get("sized")
    if argv[0] == "show":
        print(line(state, 10 ** 6) if sized else "NOT SIZED: run sizing.py size " + slug)
        return 0
    try:
        if record and sized:
            goal.fit.monitor("auto", True).eta_record(goal, record, slug, "a size change")
        old = (sized or {}).get("size")
        had = {a["check"] for a in (sized or {}).get("added") or []}
        new = sizing.override(state, rest[1], record)
        goal.guards.add_set(goal.state_dir(), slug, "size_owner", {"record": record, "from": old, "to": rest[1]},
                            "size raised %s to %s (record %s)" % (old, rest[1], record))
    except sizing.Refusal as err:
        sizing.stop(err)
    print("SIZE %s -> %s (record %s); added: %s" % (old, new["size"], record, ", ".join(a["check"] for a in new["added"] if a["check"] not in had) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
