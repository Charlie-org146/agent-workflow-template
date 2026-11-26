#!/usr/bin/env python3
"""Row levels and risk tags (LVL-1). skills/loop-files.md has the file formats, the rules and every code.

regression.py calls levels_gate.check_read() before a reading command; every table write goes through
levels_write.py; the `level`, `levels` and `relevel` commands are in levels_cli.py, the re-levelling in levels_read.py. A table is levelled when the record
file exists or the table holds the row `lvl-armed`; any other table is read and written as before.
"""
import difflib
import hashlib
import os
import re
import subprocess

TABLE, RECORD, RISKS = "regression.tsv", "regression-relevel.tsv", "regression-risk.tsv"
COLS = ("id", "old", "level", "risk", "covers", "seconds", "cmdhash", "reason")
HEAD = "# " + "\t".join(COLS) + "\n"
RHEAD = "# kind\tkey\ttag\twhy\n"
LEVELS, OLD, TAGS = ("L0", "L1", "L2"), ("land", "nightly", "draft", "covered"), ("security", "private", "none")
RANK = {"": 0, "none": 0, "security": 1, "private": 2}
KINDS = ("requirement", "row", "label", "removed", "off")
REASON = re.compile(r"^(default|covers|limits-file|time:\d+(\.\d+)?|risk:(security|private)|excepted:[A-Za-z0-9]+|"
                    r"owner:[A-Za-z0-9._-]+|src:[0-9a-f]{10})$")
L0_MS, MARKER, SHOWN = 45000, "lvl-armed", 20
OPERATION = "operation, in a pull request, when the row is already on the base; otherwise this branch's author"
# A covered row with no proving row, tied to its id, goal and command; the last cell says what excuses it.
EXCUSED = {
    "done-pkg-secret-print-3": ("v110-pkg-secret-print:3", "45a9528d23d780a8b80c0d7427543e159f391589", "TD2022",
                                "operation decision TD2022, not an owner record"),
    "done-gap-wave1-small-4": ("gap-wave1-small:4", "42801ac5c3919e607a19e59c38f2d500f24af1c1", "o988",
                               "owner record o988"),
}
CODE = "python3 <workflow-regression>/scripts/regression.py "


def sha(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def git(root, *args):
    done = subprocess.run(["git"] + list(args), cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return done.stdout if done.returncode == 0 else None


def file_of(root, name):
    return os.path.join(root, ".loop", name)


def text_of(root, name):
    """The file's text, None when it is absent; an unreadable file reads as a conflict marker, so it is refused."""
    try:
        with open(file_of(root, name), encoding="utf-8", newline="") as handle:
            return handle.read().replace("\r\n", "\n")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError):
        return "<<<<<<< unreadable\n"


def lines_of(text):
    return [(n, line) for n, line in enumerate((text or "").split("\n"), 1) if line.strip() and line[0] != "#"]


class Problem:
    def __init__(self, code, row, what, fix, who="this branch's author", name=TABLE, line=0, missing=False):
        self.code, self.row, self.what, self.fix, self.who = code, row, what, fix, who
        self.name, self.line, self.missing = name, line, missing

    def key(self):
        return self.code, self.row

    def __str__(self):
        return "%s %s (.loop/%s%s): %s. Fix: %s. Who: %s" % (
            self.code, self.row or "-", self.name, ":%d" % self.line if self.line else "", self.what, self.fix, self.who)


def bad_file(name, line, what, row=""):
    return Problem("LEVELS_BAD_FILE", row, what, "repair that line by hand, then " + CODE + "levels --check",
                   name=name, line=line)


def parse_table(text):
    """Every row line as (line number, row), duplicates kept."""
    out, bad = [], []
    for n, line in lines_of(text):
        if line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            bad.append(bad_file(TABLE, n, "a conflict marker or an unreadable file"))
            continue
        cells = (line.split("\t") + [""] * 8)[:8]
        out.append((n, dict(zip(("id", "level", "command", "goal", "seen_red", "description", "category", "link"), cells))))
    return out, bad


def parse_record(text):
    out, bad = [], []
    for n, line in lines_of(text):
        cells = line.split("\t")
        if len(cells) != len(COLS) or line.startswith(("<<<<<<<", "=======", ">>>>>>>")):
            bad.append(bad_file(RECORD, n, "the line doesn't have %d tab-separated cells" % len(COLS)))
            continue
        entry = dict(zip(COLS, cells))
        if entry["seconds"] and not re.fullmatch(r"\d+(\.\d+)?", entry["seconds"]):
            bad.append(bad_file(RECORD, n, "seconds is not a number", entry["id"]))
            entry["seconds"] = ""
        out.append((n, entry))
    return out, bad


def parse_risks(text):
    """The risk data, and its problems: absent, empty or any bad line refuses a levelled table."""
    got = {k: {} for k in KINDS}
    why = [] if lines_of(text) else ["the file is missing or empty"]
    for n, line in lines_of(text):
        cells = line.split("\t")
        if len(cells) != 4 or cells[0] not in KINDS or cells[2] not in TAGS or not cells[1] or not cells[3]:
            why.append("line %d is not `kind, key, tag, why` with a known kind and tag" % n)
        elif cells[0] in ("removed", "off") and not re.search(r"owner:[A-Za-z0-9._-]+", cells[3]):
            why.append("line %d needs owner:<record id> in its why cell" % n)
        else:
            got[cells[0]][cells[1]] = (cells[2], cells[3])
    fix = "restore the file or repair the named line"
    return got, [Problem("LEVELS_BAD_RISK_DATA", "", w, fix, name=RISKS) for w in why[:3]]


def needs(risks, row_id, goal):
    """(tag, why) a row must carry: the Principle 6 requirement its goal cell or id names, or its listed line."""
    found = []
    for name, (tag, _) in risks["requirement"].items():
        if name != "-":
            prefix, _, number = name.partition("-")
            at = re.compile(r"(?<![a-z0-9])%s-?%s(?![0-9a-z])" % (re.escape(prefix), re.escape(number)), re.I)
            if at.search(row_id) or at.search(goal):
                found.append((tag, "requirement " + name))
    if row_id in risks["row"]:
        found.append((risks["row"][row_id][0], "a listed row"))
    return max(found, key=lambda f: RANK[f[0]], default=("none", ""))


def fingerprint(row):
    return sha("\t".join((row["category"] or "criterion", row["link"], row["goal"])))[:10]


def tokens(entry):
    return [t for t in entry["reason"].split(",") if t]


def excuse(row):
    got = EXCUSED.get(row["id"])
    return got if got and row["level"] == "covered" and row["goal"] == got[0] and sha(row["command"]) == got[1] else None


def covered_level(entry, levels_by_id):
    found = [levels_by_id[k] for k in entry["covers"].split(",") if levels_by_id.get(k) in LEVELS]
    best = max(found, default="L1")
    return "L1" if entry["risk"] in ("security", "private") and best == "L0" else best


def ms(seconds):
    return int(round(float(seconds or 0) * 1000))


def l0_total(state):
    rows = state.by_id
    return sum(ms(e["seconds"]) for e in state.entries().values()
               if e["level"] == "L0" and e["id"] in rows and rows[e["id"]]["level"] != "covered")


class State:
    """One reading of the table, the record and the risk data."""

    def __init__(self, root, table=None, record=None, risks=None):
        self.root = root
        self.table, bad_table = parse_table(text_of(root, TABLE) if table is None else table)
        record = text_of(root, RECORD) if record is None else record
        self.has_record = record is not None
        self.record, bad_record = parse_record(record)
        self.risk_text = text_of(root, RISKS) if risks is None else risks
        self.risks, self.bad_risks = parse_risks(self.risk_text)
        self.bad = bad_table + bad_record
        self.by_id = {}
        for _, row in self.table:
            self.by_id.setdefault(row["id"], row)

    def entries(self):
        got = {}
        for _, entry in self.record:
            got.setdefault(entry["id"], entry)
        return got

    def levelled(self):
        return self.has_record or MARKER in self.by_id


def duplicates(state):
    out = []
    for name, lines in ((TABLE, state.table), (RECORD, state.record)):
        seen = {}
        for n, item in lines:
            if item["id"] in seen:
                same = name == RECORD and item == seen[item["id"]]
                p = Problem("LEVELS_DUPLICATE", item["id"], "the id is there twice", "keep one line by hand" if not same else
                            "the next tool write drops the identical copy, or delete it", name=name, line=n)
                p.identical = same
                out.append(p)
            seen.setdefault(item["id"], item)
    return out


def no_entry(row):
    fix = (CODE + "level %s --covers <ids>" if row["level"] == "covered" else
           CODE + "relevel (reads the linked issue's labels)" if row["category"] == "defect" else CODE + "levels --fill")
    return Problem("LEVELS_NO_ENTRY", row["id"], "the row has no record entry with a level of L0, L1 or L2",
                   fix % row["id"] if "%s" in fix else fix, OPERATION, RECORD, missing=True)


def check_entry(state, n, row, entry, levels_by_id):
    out, key = [], row["id"]

    def say(code, what, fix):
        out.append(Problem(code, key, what, fix, name=RECORD, line=n))
    edit = CODE + "level %s " % key
    if entry["level"] not in LEVELS:
        say("LEVELS_BAD_LEVEL", "the level %r is not L0, L1 or L2" % entry["level"], edit + "--test-level L1")
    tag, why = needs(state.risks, key, row["goal"])
    if tag != "none" and entry["risk"] in ("", "none"):
        say("LEVELS_NO_RISK", "the row guards a Principle 6 requirement (%s) and has no risk tag" % why,
            edit + "--risk " + tag)
    elif entry["risk"] not in TAGS:
        say("LEVELS_BAD_FILE", "the risk %r is not security, private or none" % entry["risk"], edit + "--risk <tag>")
    if entry["old"] not in OLD or not tokens(entry) or not all(REASON.match(t) for t in tokens(entry)):
        say("LEVELS_BAD_FILE", "the old word or the reason is blank or not a known one", "repair the entry by hand")
    covers = [k for k in entry["covers"].split(",") if k]
    level = entry["level"]
    if row["level"] == "covered":
        level = covered_level(entry, levels_by_id)
        if entry["seconds"] or entry["cmdhash"]:
            say("LEVELS_BAD_FILE", "a covered row carries no seconds or command hash", "empty both cells")
        if not (excuse(row) and not covers):
            wrong = [k for k in covers if k == key or k not in state.by_id or state.by_id[k]["level"] == "covered"]
            if not covers or wrong:
                say("LEVELS_BAD_COVERS", "the covers list is empty" if not covers else
                    "it names itself, an unknown row or a covered row: " + ", ".join(wrong), edit + "--covers <ids>")
            elif entry["risk"] in ("security", "private"):
                bare = [k for k in covers if state.entries().get(k, {}).get("risk") in (None, "", "none")]
                if bare:
                    say("LEVELS_BAD_COVERS", "a tagged covered row's covers must be tagged: " + ", ".join(bare),
                        CODE + "level <cover id> --risk " + entry["risk"])
    elif covers:
        say("LEVELS_BAD_FILE", "only a covered row has a covers list", "empty the covers cell")
    if entry["risk"] in ("security", "private") and level in ("L0", "L2"):
        say("LEVELS_RISK_LEVEL", "a %s row is L1, not %s" % (entry["risk"], level), edit + "--test-level L1")
    if entry["level"] == "L0" and row["level"] != "covered" and (
            ms(entry["seconds"]) <= 0 or entry["cmdhash"] != sha(row["command"])):
        say("LEVELS_L0_TIME", "an L0 entry needs a positive time measured for the row's present command",
            edit + "--test-level L0 --retime, or " + edit + "--test-level L1")
    if row["category"] == "defect" and "src:" + fingerprint(row) not in tokens(entry):
        say("LEVELS_STALE_RISK", "the defect link, goal or category changed since the risk was read", edit + "--refresh")
    return out


def validate(state):
    """Every problem of a levelled table, in table order."""
    if not state.has_record:
        return state.bad + [Problem("LEVELS_NO_RECORD", "", "the table is levelled (it holds lvl-armed) but has no record",
                                    "restore .loop/%s from git, or %srelevel" % (RECORD, CODE), name=RECORD)]
    out = state.bad + state.bad_risks + duplicates(state)
    entries, numbers = state.entries(), {}
    for n, entry in state.record:
        numbers.setdefault(entry["id"], n)
    levels_by_id = {k: e["level"] for k, e in entries.items()}
    for n, row in state.table:
        if row["level"] not in OLD:
            out.append(Problem("LEVELS_BAD_OLD_WORD", row["id"], "the level cell %r is not land, nightly, draft or "
                               "covered; the row's own level, L0, L1 or L2, is in .loop/%s" % (row["level"], RECORD),
                               CODE + "add %s again with --level and the old word" % row["id"], line=n))
        if row["id"] not in entries:
            out.append(no_entry(row))
        else:
            out += check_entry(state, numbers[row["id"]], row, entries[row["id"]], levels_by_id)
    lost = [k for k in state.by_id if k not in entries]
    for key in [k for k in entries if k not in state.by_id]:
        near = difflib.get_close_matches(key, lost, 1)
        fix = (CODE + "level %s --rename %s, if the row was renamed" % (key, near[0]) if near else
               CODE + "level %s --remove, when the row is gone" % key)
        out.append(Problem("LEVELS_ORPHAN", key, "the entry's row is not in the table", fix, OPERATION, RECORD, numbers[key]))
    for key in state.risks["row"]:
        if key not in state.by_id:
            out.append(Problem("LEVELS_ORPHAN", key, "a risk-data row line names no table row",
                               CODE + "level %s --rename <new id>, or --remove with --owner-record" % key, name=RISKS))
    total = l0_total(state)
    if total > L0_MS:
        out.append(Problem("LEVELS_L0_OVER", "", "the L0 rows add up to %.1f seconds, over 45" % (total / 1000.0),
                           CODE + "level <id> --test-level L1 for enough of them", OPERATION, RECORD))
    return out
