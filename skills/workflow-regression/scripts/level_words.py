#!/usr/bin/env python3
"""One set of level words, L0, L1 and L2 (goal v110-lvl-retire-old-words-2): what the goal_levels setting means, on a levelled table and
on one that is not. An old word is read, never silently: a levelled table prints one line; another value is refused there."""
import os
import sys

OLD = {"land": "L1", "nightly": "L2"}  # the old words, translated on a levelled table: the level that selects at least the same rows (TD2334)
LEVELS = ("L0", "L1", "L2")
PLAIN = {"L0": "land", "L1": "nightly", "L2": "nightly"}  # a table that is not levelled runs the level as its old word


def goal_target(value, levelled):
    """The target a goal lane plans from for the goal_levels value `value` (None when unset): L0, L1 or L2 on a levelled table,
    land or nightly on one that is not. Prints the old-word line or the warning; a bad value on a levelled table is refused."""
    if value is None:
        return "land"  # not set: the setting's default, run as it always was
    if levelled:
        if value in OLD:
            print('SETTINGS (GOAL_LEVELS_OLD): goal_levels "%s" in .loop/config.json is read as %s. Fix: set "goal_levels": "%s" and commit it.' % (value, OLD[value], OLD[value]))
            return OLD[value]
        if value in LEVELS:
            return value
        print('REFUSED (GOAL_LEVELS_BAD): goal_levels is %s in .loop/config.json; the values are L0, L1 and L2. Fix: set one there and commit it. Nothing was run.' % repr(str(value))[:42], file=sys.stderr)
        sys.exit(2)
    if value in PLAIN:
        return PLAIN[value]
    if value not in ("land", "nightly"):
        print('SETTINGS (GOAL_LEVELS_BAD): goal_levels is %s in .loop/config.json and runs as land. Fix: set "land" or "nightly", or L0 or L1.' % repr(str(value))[:42])
        return "land"
    return value


# -- drafts (R5, plan D3)
PLACEHOLDER = "echo write a test"  # regression.py's draft(): a command that checks nothing
READY_WORD = {"L0": "land", "L1": "land", "L2": "nightly"}  # the table's own word for a readied draft: land rows run at L1, nightly at L2


def need_stage(root, args):
    """add --level draft names the level the row will have on a levelled table; without it nothing is written."""
    from levels import State
    if args.level == "draft" and not args.test_level and State(root).levelled():
        sys.exit("REFUSED (LEVELS_NO_STAGE): a draft needs the level it will have. Fix: regression.py add %s --level draft --test-level L1 "
                 "--command '...' (L0, L1 or L2). Nothing was written." % args.id)


def ready(root, args):
    """`level ID --ready`: clear the draft state and give the table the level's own word. A draft with no real command is refused."""
    import levels_cli
    from levels import TABLE, text_of
    state = levels_cli.State(root)
    row = state.by_id.get(args.id)
    if not row:
        levels_cli.stop("LEVELS_NO_ROW", "no row %s" % args.id)
    if row["level"] != "draft":
        levels_cli.stop("LEVELS_NOT_DRAFT", "%s is not a draft. Fix: nothing to do" % args.id)
    if row["command"].strip() in ("", PLACEHOLDER):
        levels_cli.stop("LEVELS_NO_REAL_COMMAND", "%s has no real command yet. Fix: regression.py add %s --level draft --test-level <L> "
                        "--command '<a real command>', then run --ready again" % (args.id, args.id))
    word = {}

    def change(now):
        if now.by_id.get(args.id) != row:
            levels_cli.stop("LEVELS_CHANGED", "the row changed meanwhile. Fix: rerun the command")
        entries = now.entries()
        got = entries[args.id]
        word["new"] = READY_WORD[got["level"]]
        got.update(old=word["new"])
        lines = []
        for line in text_of(root, TABLE).split("\n"):
            cells = line.split("\t")
            if cells[0] == args.id and len(cells) > 1:
                cells[1] = word["new"]
            lines.append("\t".join(cells))
        now.table_text = "\n".join(lines)
        levels_cli.keep(now, entries)
        return {args.id}
    levels_cli.update(root, change)
    done = levels_cli.State(root).entries()[args.id]
    print("READY %s: level %s, the table's word %s, state blank (it runs from now on)" % (args.id, done["level"], word["new"]))
    return 0


def not_run(rows):
    """Every run, whatever it picks, names each draft row of the whole table once; a draft is never run."""
    for key in sorted(k for k, r in rows.items() if r["level"] == "draft"):
        print("not run: draft " + key)


def draft_line(key):
    return ("DRAFT %s: not run, and its requirement is not enforced, until it is ready. Fix: regression.py add %s --level draft "
            "--test-level L1 --command '<a real command>', then regression.py level %s --ready" % (key, key, key))


# -- covered rows (R8, plan D4)
def cover_unmet(root, row, rows, run):
    """Why a covered row is not met, or '': one of its covers is missing, a draft, or fails at HEAD. `run(row)` is True when the row passes."""
    from levels import State
    import completion
    if not completion.armed(root):
        return ""  # R10: what runs changes only where the pull request run is armed
    entry = State(root).entries().get(row["id"]) or {}
    for key in [k for k in (entry.get("covers") or "").split(",") if k]:
        if key not in rows or rows[key]["level"] == "draft":
            return "cover %s is %s" % (key, "not a row" if key not in rows else "a draft")
        if rows[key]["level"] != "covered" and not run(rows[key]):
            return "cover %s fails" % key
    return ""


from l2 import ORDER, rank  # noqa: E402,F401  the one worst-state order, worst first (the summary job reads the same text)


def worst(states):
    """The worst of a list of cover states by ORDER (an unknown state is worst); PASS only when nothing else is there."""
    return min(states, key=rank, default="PASS")


def cover_results(root, run_rows, rows):
    """{covered row id: (state + commit, date, flag)} for the Runs column: the worst of its covers, bound to a commit. Covers that ran at
    different commits, or have no commit recorded (an older record), count as no result; a page never says bare green."""
    import completion
    from levels import State
    if not completion.armed(root):
        return {}
    ran = {r[0]: (r + [""] * 6)[:6] for r in run_rows}
    known = {r[0] for r in tsv_of(root, "regression-known.tsv")}
    out = {}
    for key, entry in State(root).entries().items():
        if rows.get(key, {}) and rows[key][1] != "covered":
            continue
        covers = [k for k in (entry.get("covers") or "").split(",") if k]
        if not covers:
            out[key] = ("excepted", "", "")
            continue
        states, commits, days = [], set(), []
        for cover in covers:
            record = ran.get(cover)
            if cover in rows and rows[cover][1] == "draft":
                states.append("draft")
            elif not record or not record[5]:
                states.append("no result")
            elif record[1] == "FAIL":
                states.append("KNOWN" if cover in known else "FAIL")
            elif record[1] == "SKIPPED":
                states.append("SKIPPED")
            elif record[4]:
                states.append("FLAKY")
            else:
                states.append("PASS")
            record and record[5] and (commits.add(record[5]), days.append(record[2]))
        state = worst(states)
        state = "no result" if state == "PASS" and len(commits) != 1 else state
        out[key] = ("no result recorded", "", "") if state == "no result" else (
            "%s %s" % (state, sorted(commits)[0] if len(commits) == 1 else ", ".join(sorted(commits))), max(days) if days else "", "")
    return out


def tsv_of(root, name):
    try:
        with open(os.path.join(root, ".loop", name), encoding="utf-8") as handle:
            return [l.rstrip("\n").split("\t") for l in handle if l.strip() and l[0] != "#"]
    except OSError:
        return []


def pr_target(root, cfg):
    """The level the pull request check runs: L1 once the table is armed (ci_levels no longer steers it), else ci_levels or nightly."""
    import completion
    return "L1" if completion.armed(root) else str(cfg.get("ci_levels") or "nightly")
