#!/usr/bin/env python3
"""The one write path of the levels files: safe two-file writes and their repair, the checks a writer passes, the owner
record a lowering needs, and each row's entry. levels.py holds the formats and the refusals."""
import json
import os
import sys

import slots
from levels import (CODE, COLS, GIVEN, HEAD, LEVELS, RANK, RECORD, RHEAD, RISKS, TABLE, TAGS, State, covered_level, duplicates, excuse,
                    file_of, fingerprint, floor, needs, sha, text_of, tokens, validate)
from levels_gate import covers_subject, excepted_lines, goal_slug, interrupted, ledger, lowered, mark_path, report


def owner_check(root, records, subject, what):
    """The owner record that lets `what` happen to `subject`, or refuse. Any given record that covers it serves."""
    rows = ledger(root)
    for record in records or []:
        if rows and covers_subject(root, rows, record, subject):
            return record
    sys.exit("REFUSED (LEVELS_NEEDS_OWNER): %s needs --owner-record ID, an owner record on this machine that covers %s "
             "or this branch's goal; nothing was written. Fix: ask the operation session, which records the owner's "
             "words with sessions.py owner-words TEXT --ids %s. Never reuse another record or invent an id" % (
                 what, subject, subject))


KEYED = ("regression-limits.tsv", "regression-known.tsv", "regression-red.tsv")  # keyed by row id, renamed with it


def disk(root, name):
    text = text_of(root, name)
    return "-" if text is None else sha(text)


def put(root, name, text):
    path = file_of(root, name)
    temp = "%s.%d.tmp" % (path, os.getpid())
    with open(temp, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    os.replace(temp, path)


def commit_files(root, files):
    """Write several .loop files as one update: a mark with each file's before and after is left until all are written."""
    files = [(name, text) for name, text in files if text is not None and disk(root, name) != sha(text)]
    path, written = mark_path(root), []
    if not files:
        return
    if len(files) > 1 and path:
        mark = {"branch": goal_slug(root), "files": [{"name": n, "before": disk(root, n), "after": sha(t), "text": t}
                                                     for n, t in files]}
        with open(path + ".tmp", "w", encoding="utf-8") as handle:
            json.dump(mark, handle)
        os.replace(path + ".tmp", path)
    try:
        for name, text in files:
            put(root, name, text)
            written.append(name)
    except BaseException as error:
        sys.exit("LEVELS_UNEXPECTED: the write failed (%s). Written: %s. Fix: %s" % (
            type(error).__name__, ", ".join(written) or "none",
            CODE + "levels --fill completes it" if written else "rerun the same command"))
    if len(files) > 1 and path:
        os.remove(path)


def complete(root):
    """Finish a left-over write, only from a state it left: each file as before it or as after it, on the same branch."""
    path = mark_path(root)
    if not path or not os.path.exists(path):
        return
    stop = "REFUSED (LEVELS_INTERRUPTED): %s; nothing was written. Fix: check %s by hand, then " + CODE + \
        "levels --discard (removes the mark %s) and " + CODE + "levels --check"
    try:
        with open(path, encoding="utf-8") as handle:
            mark = json.load(handle)
        files = [(f["name"], f["before"], f["after"], f["text"]) for f in mark["files"]]
        assert all(name in (TABLE, RECORD, RISKS) + KEYED and sha(text) == after for name, _, after, text in files)
    except (OSError, ValueError, KeyError, TypeError, AssertionError):
        sys.exit(stop % ("the pending mark can't be read", "the .loop files", path))
    changed = [name for name, before, after, _ in files if disk(root, name) not in (before, after)]
    if mark.get("branch") != goal_slug(root) or changed:
        sys.exit(stop % ("the checkout changed since the write stopped",
                         ", ".join(changed or [f[0] for f in files]), path))
    for name, before, after, text in files:
        if disk(root, name) != after:
            put(root, name, text)
    os.remove(path)
    print("COMPLETED the interrupted write of %s" % ", ".join(f[0] for f in files))


def record_text(state):
    """The record in table order, covered levels computed again, identical copies dropped."""
    entries = state.entries()
    levels_by_id = {k: e["level"] for k, e in entries.items()}
    for key, entry in entries.items():
        if state.by_id.get(key, {}).get("level") == "covered" and entry["level"] in LEVELS:
            entry["level"] = covered_level(entry, levels_by_id)
    order = [row["id"] for _, row in state.table if row["id"] in entries]
    order += [k for k in entries if k not in state.by_id]
    return HEAD + "".join("\t".join(entries[k][c] for c in COLS) + "\n" for k in dict.fromkeys(order))


def writer_gate(state, creating):
    """What no writer writes over: duplicates, bad lines, a missing record (relevel alone makes it) or bad risk data."""
    found = state.bad + [p for p in duplicates(state) if not p.identical] + state.bad_risks
    if not state.has_record and not creating:
        found.append(validate(state)[-1])
    if found:
        report(found)
        sys.exit("REFUSED: nothing was written. Fix the lines above first")


def settle(before, state, touched):
    """Refuse a change that leaves a written row wrong or adds any problem; list the problems that were there."""
    old = {p.key() for p in before}
    found = validate(state) + lowered(state)
    mine = [p for p in found if p.key() not in old or p.row in touched]
    if mine:
        report(mine)
        sys.exit("REFUSED: this change would leave the table wrong; nothing was written")
    if found:
        print("ALSO %d problem(s) this change didn't make; see %slevels --check" % (len(found), CODE))
        report(found)


def update(root, change, creating=False):
    """Under the table's lock: read all three files, let change(state) edit them (returns the ids it wrote), check, write."""
    def locked():
        if interrupted(root):
            report([interrupted(root)])
            sys.exit("REFUSED: nothing was written")
        state = State(root)
        writer_gate(state, creating)
        before = [] if creating else validate(state) + lowered(state)
        state.table_text, state.extra = None, []
        touched = change(state)
        text = record_text(state)
        after = State(root, state.table_text or text_of(root, TABLE), text, state.risk_text)
        settle(before, after, touched)
        commit_files(root, [(RECORD, text), (TABLE, state.table_text), (RISKS, state.risk_text)] + state.extra)
        for line in excepted_lines(after):
            print(line, file=sys.stderr)
    slots.edit(root, TABLE, locked)


def entry_for(row, entry=None, **new):
    """A row's entry: the old one kept, or a fresh L1 one; what the command, goal or link change means applied."""
    out = dict(entry) if entry else dict.fromkeys(COLS, "")
    if not entry:
        out.update(id=row["id"], old=row["level"], level="L1", risk="none", reason="default")
    out.update(new)
    return out


def reasoned(entry, *add, drop=()):
    keep = [t for t in tokens(entry) if t != "default" and t.split(":")[0] not in drop and t not in add]
    entry["reason"] = ",".join(keep + [a for a in add if a]) or "default"


def pin(state, row_id, tag, why):
    """A tag given by hand is also a risk-data row line, so a refill keeps it."""
    if tag in ("security", "private") and RANK[state.risks["row"].get(row_id, ("none", ""))[0]] < RANK[tag]:
        kept = [x for x in (state.risk_text or RHEAD).rstrip("\n").split("\n") if x.split("\t")[:2] != ["row", row_id]]
        state.risk_text = "\n".join(kept + ["\t".join(("row", row_id, tag, why))]) + "\n"
        state.risks["row"][row_id] = (tag, why)


def unpin(state, row_id, record):
    """Drop the row line a --risk added, with the removal and its owner record kept for the merge-base comparison."""
    if state.risks["row"].get(row_id, ("", ""))[1].startswith(GIVEN):
        kept = [x for x in (state.risk_text or RHEAD).rstrip("\n").split("\n") if x.split("\t")[:2] != ["row", row_id]]
        state.risk_text = "\n".join(kept + ["removed\trow:%s\tnone\tlowered with owner:%s" % (row_id, record)]) + "\n"
        del state.risks["row"][row_id]


def derive(state, row, old_row, entry, opts):
    """The entry after a write of `row`: level, tag, list and reason (add, sync --write and red come through here)."""
    key, fresh = row["id"], entry is None
    out = entry_for(row, entry)
    if old_row and old_row.get("command") != row["command"] and out["level"] == "L0":
        out.update(level="L1", seconds="", cmdhash="")
        reasoned(out, drop=("time",))
    if row["level"] == "covered":
        out.update(seconds="", cmdhash="")
        if opts.get("covers"):
            out["covers"] = opts["covers"]
        reasoned(out, "excepted:" + excuse(row)[2] if excuse(row) and not out["covers"] else "covers", drop=("excepted",))
        if not out["covers"] and not excuse(row):
            sys.exit("REFUSED (LEVELS_BAD_COVERS): a covered row names the rows that prove it; nothing was written. Fix: "
                     "repeat the command with --covers ID[,ID...]")
    elif out["covers"]:
        out["covers"] = ""
        reasoned(out, drop=("covers", "excepted"))
    defect = row["category"] == "defect"
    same = not fresh and (not defect or "src:" + fingerprint(row) in tokens(out))
    tag, why = needs(state.risks, key, row["goal"])
    have = out["risk"] if out["risk"] in TAGS else "none"
    seen = opts.get("evidence")  # the defect link's class, read before the lock (levels_read.evidence)
    asked = opts.get("risk")
    if defect and not same and seen is None and not asked:
        sys.exit("REFUSED (LEVELS_NEEDS_RISK): the risk of this defect link can't be read here; nothing was written. "
                 "Fix: pass full issue URLs with network and a signed-in gh, or --risk security|private (needs no "
                 "owner record), or --risk none with --owner-record ID")
    derived = max((have, tag, seen or "none"), key=lambda t: RANK[t])
    final = max((derived, asked or "none"), key=lambda t: RANK[t])
    if asked and (RANK[asked] < RANK[derived] or asked == "none" and defect and seen is None and not same):
        low, lwhy = floor(state.risks, key, row["goal"])
        if RANK[asked] < RANK[low]:
            sys.exit("REFUSED (LEVELS_NO_RISK): %s guards %s and keeps at least %s; nothing was written" % (key, lwhy, low))
        record = owner_check(state.root, opts.get("owner"), key, "setting %s to %s" % (key, asked))
        final = asked
        unpin(state, key, record)
        reasoned(out, "owner:" + record, drop=("owner", "risk"))
    out["risk"] = final
    if final != "none":
        reasoned(out, "risk:" + final, drop=("risk",))
        if asked == final:
            pin(state, key, final, GIVEN + " --risk")
        if row["level"] != "covered" and out["level"] != "L1":
            out.update(level="L1", seconds="", cmdhash="")
            reasoned(out, drop=("time", "limits-file"))
    if defect:
        reasoned(out, "src:" + fingerprint(row), drop=("src",))
    else:
        reasoned(out, drop=("src",))
    if opts.get("level"):
        if opts["level"] == "L0":
            sys.exit("REFUSED (LEVELS_L0_TIME): only a measurement puts a row at L0; nothing was written. Fix: add it "
                     "first, then %slevel %s --test-level L0 --retime" % (CODE, key))
        out.update(level=opts["level"], seconds="", cmdhash="")
        reasoned(out, drop=("time", "limits-file"))
    return out


def edit(root, reader, change, write, opts=None):
    """regression.py's one row write. `write(rows)` gives the table's text. An unlevelled table: written as before."""
    opts = opts or {}
    if not State(root).levelled():
        given = [k for k in ("level", "risk", "covers", "evidence_asked") if opts.get(k)]
        if given:
            sys.exit("REFUSED (LEVELS_NOT_LEVELLED): --test-level, --risk, --covers and --owner-record need a levelled "
                     "table; nothing was written. Fix: " + CODE + "relevel first")

        def plain():
            rows = reader(root)
            change(rows)
            os.makedirs(os.path.join(root, ".loop"), exist_ok=True)
            slots.write_table(file_of(root, TABLE), *write(rows))
        return slots.edit(root, TABLE, plain)

    def levelled(state):
        rows = reader(root)
        old = {k: dict(v) for k, v in rows.items()}
        change(rows)
        header, lines = write(rows)
        state.table_text = header + "".join(line + "\n" for line in lines)
        now = State(root, state.table_text, "", state.risk_text)
        entries, touched = state.entries(), set()
        for key, row in now.by_id.items():
            if key != opts.get("id") and key in old and all(
                    old[key][c] == row[c] for c in ("level", "command", "goal", "category", "link")):
                continue
            entries[key] = derive(state, row, old.get(key), entries.get(key), opts if key == opts.get("id") else {})
            touched.add(key)
            if key == opts.get("id"):
                print("LEVEL %s %s, risk %s (%s). Runs still follow the row's %s word." % (
                    key, entries[key]["level"], entries[key]["risk"], entries[key]["reason"], row["level"]))
        state.record = [(0, e) for e in entries.values()]
        state.table, state.by_id = now.table, now.by_id
        return touched
    update(root, levelled)
