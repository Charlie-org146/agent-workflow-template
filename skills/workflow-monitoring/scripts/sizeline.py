#!/usr/bin/env python3
"""ASZ-1.3: the owner's size line and the board's size line. `sizeline.py set SLUG SIZE --owner-record ID` raises a goal's size
(up only, with the owner's words, never under a safety class; sizing.override does the work); `sizeline.py show SLUG` prints
`SIZE <size> (<reason>) checks: ...` and `owner: <id>` when an owner line changed it. line(run) is the one-line form the board
uses (board_tasks.py); alone() lists goals that belong to no task brief."""
import argparse
import os
import sys

DELIVERY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts")


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
    sys.path.insert(0, DELIVERY)
    import goal
    import sizing
    ap = argparse.ArgumentParser(prog="sizeline.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show").add_argument("slug")
    item = sub.add_parser("set")
    item.add_argument("slug")
    item.add_argument("size")
    item.add_argument("--owner-record", default="")
    args = ap.parse_args(argv)
    state = goal.load(args.slug)
    sized = state.get("sized")
    if args.cmd == "show":
        print(line(dict(state, sized=dict(sized, reason=sized["reason"])), 10 ** 6) if sized else "NOT SIZED: run sizing.py size " + args.slug)
        return 0
    try:
        if args.owner_record and sized:
            import fit
            fit.monitor("auto", True).eta_record(goal, args.owner_record, args.slug, "a size change")
        old = (sized or {}).get("size")
        had = {a["check"] for a in (sized or {}).get("added") or []}
        new = sizing.override(state, args.size, args.owner_record)
        goal.guards.add_set(goal.state_dir(), args.slug, "size_owner", {"record": args.owner_record, "from": old, "to": args.size},
                            "size raised %s to %s (record %s)" % (old, args.size, args.owner_record))
    except sizing.Refusal as err:
        sizing.stop(err)
    print("SIZE %s -> %s (record %s); added: %s" % (old, new["size"], args.owner_record,
                                                    ", ".join(a["check"] for a in new["added"] if a["check"] not in had) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
