#!/usr/bin/env python3
"""TSK-1: the schedule command line. Run from a repo (or a worker's worktree):
  schedule.py show                                   the queue in schedule order, each goal marked task or fix, with the reasons
  schedule.py order SLUG [SLUG ...] --by RECORD      the owner line: these goals first (the operation session only); --clear removes it
  schedule.py workaround add KEY --fix SLUG --applies A,B --kind tool|dependency --feature PAGE --found REF [--owner-record ID] [--live] "words"
  schedule.py workaround use KEY --goal SLUG | fail KEY --goal SLUG --reason TEXT | close KEY --reason TEXT | reconcile KEY [--live] | list
Exit 0 done, 2 refused, 3 the schedule could not be read in full (every board prints why). A GitHub write is only a preview without --live.
Codes: SCHED-E01 worker refused, E02 not the worker's own goal, E03 bad arguments, E04 lock held, E05 secret-shaped words, E06 outside
text refused, E07 issue not confirmed, E08 not the owner's record, E09 duplicate key or unknown record, E10-E14 unreadable input, E15 stored words face a safety check, E99 unexpected."""
import argparse
import datetime
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auto  # noqa: E402
import schedule_load as sl  # noqa: E402
import schedule_state as ss  # noqa: E402

KINDS = ("tool", "dependency")


def top():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise ss.Refused("SCHED-E03", "not inside a git repository", "run it from the repo")
    return out


def owner_record(root, record, slugs):
    """Design H: the record must be one of the owner's words in owner-words.tsv (five columns) whose covered ids include every goal ordered
    (or order:*); a made-up id, a malformed row and a record about other goals all refuse before anything is written."""
    row = next((r for r in auto.owner_rows(root) if r[0] == record), None)
    covers = set(row[4].split(",")) if row else set()
    if not row or not covers - {""}:
        raise ss.Refused("SCHED-E08", "%s is not a record of the owner's words" % (sl.clean(record, 30) or "no record"), "record them (sessions.py owner-words TEXT --ids GOALS), then pass --by ID")
    gap = [x for x in slugs if x not in covers and "order:*" not in covers]
    if gap:
        raise ss.Refused("SCHED-E08", "record %s covers %s, not %s" % (sl.clean(record, 30), sl.clean(",".join(sorted(covers)), 60), sl.clean(gap[0], 30)), "record the owner's words for the goals ordered (sessions.py owner-words TEXT --ids GOALS)")


def show(root):
    result = sl.load(root)
    lines = list(result["banner"])
    if result["release"]:
        lines.append("release: %s (source: brief)" % result["release"])
    for n, g in enumerate(result["goals"], 1):
        lines.append("  %d. %s" % (n, " | ".join([g["slug"]] + g["marks"] + ["waits for: " + (", ".join(g["depends"]) or "-")])))
    lines += ["note: " + note for note in result["notes"]]
    why = sl.outside(root, "\n".join(lines), strict=False)  # queue words (a dependency name) pass the screen like the boards
    print(*(lines if not why else ["output hidden: " + why]), sep="\n")
    for item, cause in result["incomplete"]:
        print("%s: %s unreadable (%s)" % (sl.CODES[item], item, sl.shown(root, cause)), file=sys.stderr)
    return 3 if result["incomplete"] else 0


def need_complete(root, verb):
    """A mutation never runs on an unreadable input: exit 3 with the input's code (order --clear is the repair and skips this)."""
    bad = sl.load(root)["incomplete"]
    if bad:
        raise ss.Refused(sl.CODES[bad[0][0]], "%s needs every input readable, and %s is not (%s)" % (verb, bad[0][0], sl.clean(bad[0][1], 60)), sl.REPAIR[bad[0][0]])


def order(root, args):
    ss.guard_worker("order")
    paths = sl.paths(root)
    if args.clear:
        ss.clear_order(paths)
        print("order cleared")
        return 0
    need_complete(root, "order")
    queued = [g["slug"] for g in sl.load(root)["goals"]]
    bad = [s for s in args.slugs if s not in queued]
    owner_record(root, args.by, args.slugs)
    if not args.slugs or bad:
        raise ss.Refused("SCHED-E03", "unknown goal %s" % (sl.clean(bad[0], 40) if bad else "(none given)"), "queued goals: " + ", ".join(queued))
    ss.set_order(paths, args.slugs, args.by)
    print("order set: %s (%s)" % (", ".join(args.slugs), args.by))
    return 0


def find(recs, key):
    hit = [r for r in recs if r["key"] == key]
    if not hit:
        raise ss.Refused("SCHED-E09", "no workaround record %s" % sl.clean(key, 40), "keys: " + (", ".join(r["key"] for r in recs) or "none; use `workaround add`"))
    return hit[0]


def records(paths):
    recs, cause = sl.read_json_lines(paths["workaround"])
    if cause:
        raise ss.Refused("SCHED-E11", "the workaround record is " + cause, "inspect or move %s" % paths["workaround"])
    return recs


def unsafe(root, words, goal):
    """The operation's own checks (auto.py): a safety class in the words, a risky path, or an always-ask goal; '' when none applies."""
    for name, found in auto.CLASSES.items():
        if found.search(words):
            return "safety class " + name
    for pattern in auto.config(root).get("risky_paths") or []:
        try:
            if re.search(pattern, words):
                return "risky path " + pattern
        except re.error:
            continue
    return "%s is an always-ask goal" % goal if auto.always(root, goal) else ""


def add(root, args, paths):
    ss.guard_worker("workaround add")
    need_complete(root, "workaround add")
    applies = [x for x in args.applies.split(",") if x]
    rec = {"key": args.key, "fix": args.fix, "applies": applies, "kind": args.kind, "words": args.words, "feature": args.feature, "found": args.found,
           "goal": applies[0] if applies else "", "safe": any(g["slug"] == args.fix and g["safe"] for g in sl.load(root)["goals"]), "state": "pending", "attempts": 0, "issue": 0, "uses": {}, "review": datetime.date.today().isoformat(), "owner": args.owner_record}
    if not (args.kind and applies and all(sl.NAME.match(x) for x in applies)):
        raise ss.Refused("SCHED-E03", "add needs --kind, --applies, --fix, --feature and --found", "see `schedule.py --help`")
    ss.screened(root, rec)  # the secret screen and the name scan, before anything is recorded
    if not args.live:
        ss.file_issue(root, rec, False)
        print("nothing recorded (preview); add --live to record and file")
        return 0
    with ss.Lock(paths):
        recs = records(paths)
        folder = os.path.join(paths["folder"], "runs")
        known = {g["slug"] for g in sl.load(root)["goals"]} | ({n[:-5] for n in os.listdir(folder) if n.endswith(".json")} if os.path.isdir(folder) else set())
        if any(r["key"] == args.key for r in recs):
            raise ss.Refused("SCHED-E09", "workaround %s already exists" % args.key, "reuse it with `workaround use %s --goal SLUG`" % args.key)
        if args.fix not in known:
            raise ss.Refused("SCHED-E03", "--fix %s is not a queued or running goal" % sl.clean(args.fix, 40), "see `schedule.py show`")
        ss.save_records(paths, recs + [rec])
        rec["issue"] = ss.file_issue(root, rec, True)
        rec["state"] = "done"
        ss.save_records(paths, recs + [rec])
    print("recorded %s, issue #%d" % (args.key, rec["issue"]))
    return 0


def workaround(root, args):
    paths, verb = sl.paths(root), args.verb
    if verb == "add":
        return add(root, args, paths)
    if verb == "list":
        for r in records(paths):
            print("%s | fix %s | goals %s | %s | %s%s" % (r["key"], r["fix"], ",".join(r["applies"]), r["kind"], r["state"], " | issue #%s" % r["issue"] if r.get("issue") else ""))
        return 0
    if verb == "use":
        ss.guard_worker("workaround use")
    with ss.Lock(paths):
        recs = records(paths)
        rec = find(recs, args.key)
        if verb == "fail" and args.goal not in rec["applies"]:
            raise ss.Refused("SCHED-E03", "%s does not apply to %s" % (sl.clean(rec["key"], 30), sl.clean(args.goal, 30)), "see `workaround list`")
        if verb != "use":
            ss.guard_worker("workaround " + verb, [args.goal] if verb == "fail" else rec["applies"])
        if verb == "reconcile":
            found = ss.lookup(root, rec["key"], rec["fix"])
            if found is None:
                raise ss.Refused("SCHED-E07", "the issue lookup failed", "rerun later; nothing was created", "unknown")
            if not found and args.live:
                found = ss.file_issue(root, rec, True)
            elif not found:
                print("PREVIEW: none found; --live would file one issue")
            if found and rec["state"] == "pending":  # only a pending record is completed; a closed or failed one is never revived
                rec.update(issue=found, state="done")
                ss.save_records(paths, recs)
            print("reconciled %s: %s" % (rec["key"], "issue #%d" % found if found else "none found"))
            return 0
        if verb == "use":
            if rec.get("safe") or any(g["slug"] == rec["fix"] and g["safe"] for g in sl.load(root)["goals"]):
                raise ss.Refused("SCHED-E03", "%s is a safety fix: it is never waived" % sl.clean(rec["fix"], 40), "leave the wait")
            if args.goal not in rec["applies"] or rec["kind"] != "tool" or rec["state"] != "done":
                raise ss.Refused("SCHED-E03", "%s does not apply to %s (it must be a done `tool` record for a listed goal)" % (sl.clean(rec["key"], 30), sl.clean(args.goal, 30)), "see `workaround list`")
            why = unsafe(root, rec["words"], args.goal)
            if why:
                raise ss.Refused("SCHED-E15", "the stored words face a safety check: " + why, "ask the owner through the operation; no activation was written")
            if not ss.say(root, rec["words"]):
                raise ss.Refused("SCHED-E06", "the stored words cannot be shown", "fix the record; no activation was written")
            rec["uses"][args.goal] = "active"
            ss.save_records(paths, recs)
            print("activated %s for %s" % (rec["key"], args.goal))
            return 0
        gone = [args.goal] if verb == "fail" else [g for g, v in rec["uses"].items() if v == "active"]
        if verb == "fail":
            rec["uses"][args.goal] = "failed"
        else:
            rec["state"] = "closed"
        ss.save_records(paths, recs)
        ss.revoke(paths, gone, rec["key"], rec["fix"])
    print("%s %s: the wait is restored" % (verb, rec["key"]))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog="schedule.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    item = sub.add_parser("order")
    item.add_argument("slugs", nargs="*")
    item.add_argument("--by", default="")
    item.add_argument("--clear", action="store_true")
    wk = sub.add_parser("workaround").add_subparsers(dest="verb", required=True)
    for name in ("add", "use", "fail", "close", "reconcile", "list"):
        p = wk.add_parser(name)
        if name != "list":
            p.add_argument("key")
        if name == "add":
            p.add_argument("words")
            for flag in ("--fix", "--applies", "--feature", "--found", "--owner-record"):
                p.add_argument(flag, default="")
            p.add_argument("--kind", default="", choices=("",) + KINDS)
        if name in ("use", "fail"):
            p.add_argument("--goal", required=True)
        if name in ("fail", "close"):
            p.add_argument("--reason", default="")
        if name in ("add", "reconcile"):
            p.add_argument("--live", action="store_true")
    args = ap.parse_args(argv)
    try:
        root = top()
        code = show(root) if args.cmd == "show" else order(root, args) if args.cmd == "order" else workaround(root, args)
        late = sl.load(root)["incomplete"] if code == 0 and args.cmd != "show" else []
        late and print("%s: %s unreadable; the command ran, repair: %s" % (sl.CODES[late[0][0]], late[0][0], sl.REPAIR[late[0][0]]), file=sys.stderr)
        return 3 if late else code
    except ss.Refused as err:
        print(err.line(), file=sys.stderr)
        return 3 if err.code in ("SCHED-E10", "SCHED-E11", "SCHED-E12", "SCHED-E13", "SCHED-E14") else 2
    except Exception as err:  # SCHED-E99: never a bare trace
        print("FAILED SCHED-E99: %s in %s. Side effects: unknown. Fix: rerun `schedule.py show` before retrying; nothing is retried automatically." % (type(err).__name__, args.cmd), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
