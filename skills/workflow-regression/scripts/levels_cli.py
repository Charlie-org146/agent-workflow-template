#!/usr/bin/env python3
"""regression.py's `level`, `levels` and `relevel` commands, and add's level flags (skills/loop-files.md)."""
import argparse
import json
import os
import re
import sys

import completion
import level_words
import levels_read
import slots
from levels import (CODE, LEVELS, RISKS, TABLE, TAGS, Problem, State, excuse, file_of, fingerprint, l0_total,
                    sha, text_of, tokens)
from levels_gate import SHOWN, mark_path, problems, report
from levels_write import KEYED, complete, derive, owner_check, reasoned, set_line, update

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,60}$")


def stop(code, why):
    sys.exit("REFUSED (%s): %s; nothing was written" % (code, why))


def need_levelled(state):
    if not state.levelled():
        stop("LEVELS_NOT_LEVELLED", "this table is not levelled. Fix: %srelevel first" % CODE)


def keep(state, entries):
    state.record = [(0, e) for e in entries.values()]


def lines_edit(text, old, new=None, column=0):
    """The file's text with the line whose cell is `old` renamed to `new`, or dropped; comments stay."""
    out = []
    for line in (text or "").split("\n"):
        cells = line.split("\t")
        if line and line[0] != "#" and len(cells) > column and cells[column] == old:
            if new is None:
                continue
            cells[column] = new
            line = "\t".join(cells)
        out.append(line)
    return "\n".join(out)


def risk_lines(text, old, new=None):
    out = []
    for line in (text or "").split("\n"):
        cells = line.split("\t")
        if len(cells) > 1 and cells[0] in ("row", "given") and cells[1] == old:
            if new is None:
                continue
            line = "\t".join([cells[0], new] + cells[2:])
        out.append(line)
    return "\n".join(out)


def other_files(root, old, new=None):
    return [(name, lines_edit(text_of(root, name), old, new)) for name in KEYED if text_of(root, name) is not None]


def rename(root, key, new):
    """Move the row and everything keyed by its id in one update (or only the entry, when the row was renamed by hand)."""
    if not ID.match(new):
        stop("LEVELS_BAD_RENAME", "%r is not a row id" % new)

    def change(state):
        entries = state.entries()
        here = key in state.by_id
        if here and new in state.by_id:
            stop("LEVELS_BAD_RENAME", "%s and %s are both rows" % (key, new))
        if new in entries or not here and (key not in entries or new not in state.by_id):
            stop("LEVELS_BAD_RENAME", "%s must be a row or an entry, and %s must not have an entry (an entry whose row "
                 "was renamed by hand takes the row's present id)" % (key, new))
        if here:
            state.table_text = lines_edit(text_of(root, TABLE), key, new)
        moved = {}
        for name, entry in entries.items():
            entry["covers"] = ",".join(new if k == key else k for k in entry["covers"].split(",")) if entry["covers"] else ""
            if name == key:
                entry["id"] = new
            moved[entry["id"]] = entry
        keep(state, moved)
        state.risk_text = risk_lines(state.risk_text, key, new)
        state.extra = other_files(root, key, new)
        return {new}
    update(root, change)
    print("RENAMED %s to %s" % (key, new))
    return 0


def remove(root, key, records):
    def change(state):
        entries = state.entries()
        if key not in state.by_id and key not in entries and key not in state.risks["row"]:
            stop("LEVELS_BAD_REMOVE", "no row or entry %s" % key)
        users = sorted(k for k, e in entries.items() if k != key and key in e["covers"].split(","))
        if users:
            stop("LEVELS_BAD_COVERS", "%s proves %s. Fix: give them other covers first" % (key, ", ".join(users)))
        entry = entries.pop(key, None)
        listed = [kind for kind in ("row", "given") if key in state.risks[kind]]
        tagged = listed or (entry or {}).get("risk") in ("security", "private")
        record = owner_check(root, records, key, "removing the tagged row %s" % key) if tagged else None
        if key in state.by_id:
            state.table_text = lines_edit(text_of(root, TABLE), key)
        keep(state, entries)
        state.risk_text = risk_lines(state.risk_text, key)
        if record:
            for mark in ["entry:" + key] + ["%s:%s" % (kind, key) for kind in listed]:
                set_line(state, "removed", mark, "none", "removed with owner:" + record)
        state.extra = other_files(root, key)
        return set()
    update(root, change)
    print("REMOVED %s" % key)
    return 0


def cmd_level(root, args):
    state = State(root)
    need_levelled(state)
    if args.ready:
        return level_words.ready(root, args)
    edits = [args.test_level, args.risk, args.covers, args.retime, args.refresh]
    if args.rename or args.remove:
        if any(edits) or args.rename and args.remove:
            stop("LEVELS_BAD_FLAGS", "--rename and --remove go alone")
        return rename(root, args.id, args.rename) if args.rename else remove(root, args.id, args.owner_record)
    row, entry = state.by_id.get(args.id), state.entries().get(args.id)
    if not row:
        stop("LEVELS_NO_ROW", "no row %s" % args.id)
    level_words.draft_guard(row, args)
    if not any(edits):
        print("LEVEL %s: %s" % (args.id, "no entry" if not entry else ", ".join(
            "%s %s" % (k, entry[k]) for k in ("old", "level", "risk", "covers", "seconds", "reason") if entry[k])))
        report([p for p in problems(state) if p.row == args.id], sys.stdout)
        return 0
    seconds = None
    if args.test_level == "L0" and not args.retime:
        stop("LEVELS_L0_TIME", "only a measurement puts a row at L0. Fix: %slevel %s --test-level L0 --retime" % (
            CODE, args.id))
    if args.retime:
        if args.test_level not in (None, "L0"):
            stop("LEVELS_BAD_FLAGS", "--retime measures for L0")
        for measured in (False, True):
            why = levels_read.l0_reason(root, state, row, entry, seconds if measured else None)
            if why:
                stop("LEVELS_L0_TIME", "%s may not be L0: %s. Fix: %slevel %s --test-level L1" % (
                    args.id, why, CODE, args.id))
            if not measured:
                seconds = levels_read.measured_run(root, row)
    opts = {"risk": args.risk, "covers": args.covers, "owner": args.owner_record}
    stale = row["category"] == "defect" and "src:" + fingerprint(row) not in tokens(entry or {"reason": ""})
    if args.refresh or stale and args.risk:  # a changed link is read again before a typed tag is taken
        if row["category"] != "defect":
            stop("LEVELS_BAD_FLAGS", "--refresh reads a defect row's link again")
        own = levels_read.read_input(file_of(root, "regression-relevel-input.tsv"))[1].get(args.id, ())
        try:
            opts["evidence"] = levels_read.evidence(root, state.risks, row["link"], own)
        except levels_read.Unread as error:
            if not args.risk:
                stop("LEVELS_NEEDS_RISK", "the link can't be read (%s). Fix: retry with network and gh sign-in, or "
                     "give --risk (none or a lowering needs --owner-record)" % error)

    def change(now):
        if now.by_id.get(args.id) != row:
            stop("LEVELS_CHANGED", "the row changed meanwhile. Fix: rerun the command")
        entries = now.entries()
        got = entries.get(args.id)
        if args.risk or args.covers or args.refresh or not got:
            got = derive(now, row, row, got, opts)
        if args.test_level and not args.retime:
            got.update(level=args.test_level, seconds="", cmdhash="")
            reasoned(got, drop=("time", "limits-file"))
        if args.retime:
            got.update(level="L0", seconds="%.1f" % seconds, cmdhash=sha(row["command"]))
            reasoned(got, "time:%.1f" % seconds, drop=("limits-file",))
        entries[args.id] = got
        keep(now, entries)
        return {args.id}
    update(root, change)
    done = State(root).entries()[args.id]
    print("LEVEL %s %s, risk %s (%s)" % (args.id, done["level"], done["risk"], done["reason"]))
    return 0


def fill(root):
    """Add the missing entries of non-defect rows, offline; never L0."""
    need_levelled(State(root))
    left = []

    def change(state):
        entries, limits, done = state.entries(), completion.limits(root), set()
        for _, row in state.table:
            key = row["id"]
            if key in entries:
                continue
            if row["category"] == "defect":
                left.append("%s: a defect row. Fix: %srelevel (reads its labels)" % (key, CODE))
            elif row["level"] == "covered" and not excuse(row):
                left.append("%s: covered with no list. Fix: %slevel %s --covers ID[,ID...]" % (key, CODE, key))
            else:
                entry = derive(state, row, None, None, {})
                if row["level"] == "nightly" and entry["risk"] == "none" and limits.get(key) == "nightly":
                    entry["level"] = "L2"
                    reasoned(entry, "limits-file")
                entries[key] = entry
                done.add(key)
        keep(state, entries)
        print("FILLED %d entries%s" % (len(done), ": " + ", ".join(sorted(done)[:20]) if done else ""))
        return done
    update(root, change)
    if left:
        print("NOT FILLED %d:\n  %s" % (len(left), "\n  ".join(left[:SHOWN])))
    return 2 if left else 0


def page_differs(root, state):
    """The risk data's requirement list against the Principles page, where the repository has that page."""
    try:
        with open(os.path.join(root, ".loop", "config.json"), encoding="utf-8") as handle:
            wiki = json.load(handle).get("wiki_dir")
    except (OSError, ValueError, AttributeError):
        wiki = None
    folder = os.path.join(root, wiki) if wiki else os.path.join(root, "docs", "wiki")
    try:
        with open(os.path.join(folder, "Principles" + ".md"), encoding="utf-8") as handle:
            part = re.split(r"(?m)^## 6\..*$", handle.read(), maxsplit=1)
    except FileNotFoundError:
        return []
    except (OSError, UnicodeError) as error:
        return [Problem("LEVELS_REQUIREMENTS", "", "the Principles page can't be read (%s), so the requirement list "
                        "can't be compared" % type(error).__name__, "make the page readable", name=RISKS)]
    if len(part) < 2:
        if not set(state.risks["requirement"]) - {"-"}:
            return []
        return [Problem("LEVELS_REQUIREMENTS", "", "the Principles page has no section 6 heading, so the requirement "
                        "list can't be compared", "restore the heading", name=RISKS)]
    named = set()
    for line in re.split(r"(?m)^## ", part[1])[0].split("\n"):
        if line.startswith("| ["):
            named |= set(re.findall(r"\b[A-Z]{2,5}-\d+\b", line[3:].split("](")[0]))
    have = {k for k in state.risks["requirement"] if k != "-"}
    if named == have:
        return []
    return [Problem("LEVELS_REQUIREMENTS", "", "the risk data's requirement list and the Principles page differ "
                    "(only on the page: %s; only in the risk data: %s)" % (
                        ", ".join(sorted(named - have)) or "none", ", ".join(sorted(have - named)) or "none"),
                    "add or remove requirement lines (a removal needs a removed line with an owner record)", name=RISKS)]


def cmd_levels(root, args):
    if args.discard:
        path = mark_path(root)

        def discard():  # under the writers' lock: a live write's mark is never removed
            if not path or not os.path.exists(path):
                print("no pending write")
            else:
                os.remove(path)
                print("DISCARDED the pending mark. Check the .loop files, then run %slevels --check" % CODE)
        slots.edit(root, TABLE, discard)
        return 0
    if args.fill:
        slots.edit(root, TABLE, lambda: complete(root))
        return fill(root)
    state = State(root)
    found = problems(state)
    if state.levelled() and state.has_record and not state.bad_risks:
        found = found + page_differs(root, state)
    if not state.levelled() and not found:
        print("not levelled")
        return 0
    if args.check:
        if not found:
            print("valid: %d rows, L0 %.1f s of 45" % (len(state.table), l0_total(state) / 1000.0))
            return 0
        for item in found[:SHOWN]:
            print("%s: %s" % ("missing entry to fill" if item.missing else "stored entry to repair", item))
        print("%d problem(s)" % len(found))
        return 2
    entries = state.entries().values()
    for name, values, field in (("levels", LEVELS, "level"), ("risk", TAGS, "risk")):
        print("%s: %s" % (name, ", ".join("%s %d" % (v, sum(e[field] == v for e in entries)) for v in values)))
    print("L0 %.1f s of 45: %s" % (l0_total(state) / 1000.0, ", ".join(sorted(
        e["id"] for e in entries if e["level"] == "L0")) or "none"))
    print("problems: %d" % len(found))
    report(found, sys.stdout)
    return 0


def old_word(text):
    if re.fullmatch(r"[Ll]\d", text):
        raise argparse.ArgumentTypeError("%s is a test level: give it with --test-level; --level takes the old words land, nightly, "
                                         "draft or covered (the levels are L0, L1 and L2)" % text)
    return text


def register(sub, top):
    def owner(parser):
        parser.add_argument("--owner-record", action="append", help="an owner record covering the row or this goal "
                            "(repeatable); needed to lower or remove a tag")
    add = sub.choices["add"]
    for action in add._actions:
        if action.dest == "level":
            action.type, action.help = old_word, "the old word; it still selects what runs"
    add.add_argument("--test-level", choices=LEVELS[1:] + LEVELS[:1], help="what the pull request's L1 run follows")
    add.add_argument("--risk", choices=TAGS)
    add.add_argument("--covers", help="a covered row: the ids of the rows that prove it")
    owner(add)
    item = sub.add_parser("level", help="show or change one row's level and risk")
    item.add_argument("id")
    item.add_argument("--test-level", choices=LEVELS)
    item.add_argument("--risk", choices=TAGS)
    item.add_argument("--covers")
    item.add_argument("--remove", action="store_true")
    item.add_argument("--ready", action="store_true")
    item.add_argument("--rename", metavar="NEW")
    item.add_argument("--retime", action="store_true", help="runs the row's committed command in a throwaway clone; L0")
    item.add_argument("--refresh", action="store_true", help="read a defect row's link labels again")
    owner(item)
    item.set_defaults(func=lambda a: cmd_level(top(), a))
    item = sub.add_parser("levels", help="list levels and problems; check, fill or discard a pending write")
    pick = item.add_mutually_exclusive_group()
    for flag in ("--check", "--fill", "--discard"):
        pick.add_argument(flag, action="store_true")
    item.set_defaults(func=lambda a: cmd_levels(top(), a))
    item = sub.add_parser("relevel", help="give every row a level and a risk tag (run once)")
    item.add_argument("--dry-run", action="store_true")
    item.add_argument("--input")
    item.add_argument("--times")
    item.add_argument("--row-limit", type=int)
    item.add_argument("--risk-for", action="append", metavar="ROW=TAG")
    owner(item)
    item.set_defaults(func=lambda a: levels_read.cmd_relevel(top(), a))
