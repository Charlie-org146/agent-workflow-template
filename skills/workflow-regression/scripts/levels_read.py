#!/usr/bin/env python3
"""The one-time re-levelling, the reading of defect labels and which rows may run in L0 (skills/loop-files.md)."""
import os
import re
import signal
import subprocess
import sys
import tempfile
import time

import actions
import completion
from levels import L0_MS, RANK, State, excuse, file_of, fingerprint, ms, needs, sha, tokens
from levels_write import derive, entry_for, pin, reasoned, update, writer_gate
from row_reach import references

CALL_SECONDS, ALL_SECONDS, ROW_LIMIT, UNDER = 20, 300, 300, 5
URL = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/(?:issues|pull)/(\d+)/?(?:#[\w-]*)?$")
CLASSES = (("401", "not signed in to gh"), ("gh auth login", "not signed in to gh"), ("rate limit", "rate limited"),
           ("429", "rate limited"), ("403", "no access"), ("404", "not found"))
# A command, or a script it runs (followed three deep), that holds one of these is not L0: it may use the network or
# build a toy repository. A script that can't be followed makes the row ineligible too.
NETWORK = ("curl ", "wget ", "http://", "https://", "urllib", "import requests", "requests.", "import socket",
           "socket.socket", "ssh ", "gh api", "gh pr", "gh issue", "gh repo", "gh run", "gh release", "gh auth",
           '"gh"', "'gh'", "git fetch", "git push", "git pull", "git clone", "ls-remote", "pip install", "npm ", "npx ")
TOY = ("git init", "worktree add", "toyrepo", "toy_repo", "toylib", "mkrepo", "make_repo", "init_repo", "new_repo",
       '"init"', "'init'")
OPAQUE = (re.compile(r"\beval\b"), re.compile(r"\b(importlib|runpy)\b|(?<!def )(?<![\w.])__[a-z]+__\s*\("),
          re.compile(r"\b(?:python3?|bash|sh|source)\s+(?:-\w+\s+)*\"?\$\{?(?!here\b)\w+"))
IMPORT = re.compile(r"^\s*(?:from\s+([A-Za-z_]\w*)|import\s+([\w, ]+))", re.M)
DEEP = 3


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return None


def column(root, name):
    return {line.split("\t")[0] for line in (read(file_of(root, name)) or "").split("\n") if line and line[0] != "#"}


# -- defect links and their labels

def links(cell):
    """Every address a link cell holds: finding:SLUG, a full issue or pull request URL, a bare or #N number, other."""
    out = []
    for part in re.split(r"[\s;,]+", cell.strip()):
        if not part:
            continue
        marked = re.match(r"^\[[^\]]*\]\((.+)\)$", part)
        part = marked.group(1) if marked else part
        url = URL.match(part)
        if part.startswith("finding:"):
            out.append(("finding", part[8:]))
        elif url and url.group(1) not in (".", "..") and url.group(2) not in (".", ".."):
            out.append(("url", url.groups()))
        elif re.fullmatch(r"#?\d+", part):
            out.append(("number", part.lstrip("#")))
        else:
            out.append(("other", part))
    return out


class Unread(Exception):
    pass


def labels(root, address, seen, deadline):
    """The label names of one issue or pull request, read once; one retry. The caller never prints or stores them."""
    if address in seen:
        return seen[address]
    why = "timeout"
    for _ in range(2):
        left = min(CALL_SECONDS, deadline - time.time())
        if left <= 0:
            break
        try:
            done = subprocess.run(["gh", "api", "repos/%s/%s/issues/%s" % address, "--jq", ".labels[].name"], cwd=root,
                                  capture_output=True, text=True, timeout=left, errors="replace")
        except FileNotFoundError:
            why = "no gh tool"
            break
        except subprocess.TimeoutExpired:
            why = "timeout"
            continue
        if done.returncode == 0:
            seen[address] = done.stdout.split("\n")
            return seen[address]
        text = done.stderr.lower()
        why = next((name for mark, name in CLASSES if mark in text), "unreadable answer")
        if why in ("not found", "no access", "not signed in to gh"):
            break
    raise Unread(why)


def evidence(root, risks, cell, own=(), seen=None, deadline=None):
    """The strongest tag the link cell's labels give. A finding reads nothing. Raises Unread naming why, by position."""
    seen = {} if seen is None else seen
    deadline = deadline or time.time() + ALL_SECONDS
    found, got = links(cell), "none"
    if not found:
        raise Unread("the link cell is empty")
    for i, (kind, value) in enumerate(found, 1):
        if kind == "finding":
            continue
        if kind == "number" and value in own:
            kind, value = "url", ("{owner}", "{repo}", value)
        if kind != "url":
            raise Unread("link %d of %d is a bare number or another form" % (i, len(found)))
        try:
            names = labels(root, tuple(value), seen, deadline)
        except Unread as error:
            raise Unread("link %d of %d: %s" % (i, len(found), error))
        for word, (tag, _) in risks["label"].items():
            if any(word.lower() in name.lower() for name in names) and RANK[tag] > RANK[got]:
                got = tag
    return got


def add_options(root, args):
    """What `add` hands the writer; a changed defect link is read here, before the lock (unchanged: not read again)."""
    opts = {"id": args.id, "level": args.test_level, "risk": args.risk, "covers": args.covers,
            "owner": args.owner_record, "evidence_asked": args.owner_record}
    state = State(root)
    if args.category == "defect" and state.levelled() and not state.bad_risks:
        row = {"category": "defect", "link": args.link.strip(), "goal": args.goal.strip()}
        entry = state.entries().get(args.id)
        if not entry or "src:" + fingerprint(row) not in tokens(entry):
            try:
                if any(kind == "number" for kind, _ in links(row["link"])):
                    raise Unread("a bare or #N number is read only by relevel")
                opts["evidence"] = evidence(root, state.risks, row["link"])
            except Unread as error:
                print("LABELS not read: %s" % error, file=sys.stderr)
    return opts


# -- which rows may run in L0

def scripts_of(root, rel, text, memo):
    """The repo scripts a text names, and the repo modules a Python script imports."""
    found = set(references(root, text, os.path.dirname(rel), wide=False, memo=memo)[0])
    if rel.endswith(".py"):
        if "folders" not in memo:
            memo["folders"] = ["dev/toy"] + sorted("skills/%s/scripts" % name for name in os.listdir(
                os.path.join(root, "skills")) if os.path.isdir(os.path.join(root, "skills", name, "scripts"))) \
                if os.path.isdir(os.path.join(root, "skills")) else ["dev/toy"]
        names = {n.split()[0] for a, b in IMPORT.findall(text) for n in ([a] if a else b.split(",")) if n.strip()}
        for name in names:
            here = os.path.join(os.path.dirname(rel), name + ".py")
            paths = [here] if os.path.isfile(os.path.join(root, here)) else [
                os.path.join(folder, name + ".py") for folder in memo["folders"]]
            found |= {p for p in paths if os.path.isfile(os.path.join(root, p))}
    return {p for p in found if p != rel and p.endswith((".py", ".sh"))}


def ineligible(root, command, cache=None):
    """Why a command may not run in L0, or '': a network or toy-repository word, or a script it can't follow."""
    cache = {} if cache is None else cache
    todo, done, memo = [("", command, 0)], set(), cache.setdefault("kinds", {})
    while todo:
        rel, text, depth = todo.pop()
        where = rel or "the command"
        for words, what in ((NETWORK, "network"), (TOY, "toy repository")):
            word = next((w for w in words if w in text), "")
            if word:
                return "%s word %r in %s" % (what, word, where)
        if any(p.search(text) for p in OPAQUE):
            return "a call that can't be followed in " + where
        for path in sorted(scripts_of(root, rel, text, memo)):
            if path in done:
                continue
            done.add(path)
            body = read(os.path.join(root, path))
            if body is None:
                return "%s names %s, which can't be followed" % (where, path)
            if depth + 1 > DEEP:
                return "scripts go deeper than %d at %s" % (DEEP, path)
            todo.append((path, body, depth + 1))
    return ""


def untimed(root):
    """Rows whose recorded time proves nothing: skipped on the timing runner, or known red."""
    return column(root, "regression-skips.tsv") | column(root, "regression-known.tsv")


def measured_run(root, row):
    """`level ID --retime`: run the committed command in a throwaway clone with its own HOME; seconds, on exit 0 only."""
    limit = completion.limit(root, row["id"], ROW_LIMIT)
    with tempfile.TemporaryDirectory(prefix="levels-retime-") as temp:
        tree, home = os.path.join(temp, "tree"), os.path.join(temp, "home")
        os.mkdir(home)
        if subprocess.run(["git", "clone", "-q", "--no-hardlinks", root, tree], capture_output=True).returncode:
            sys.exit("REFUSED (LEVELS_L0_TIME): the throwaway clone failed; nothing was written")
        began = time.time()
        with open(os.path.join(temp, "out"), "wb") as out:
            child = subprocess.Popen(["sh", "-c", row["command"]], cwd=tree, stdout=out, stderr=out,
                                     stdin=subprocess.DEVNULL, env=dict(actions.row_env(), HOME=home),
                                     start_new_session=True)
            try:
                code = child.wait(timeout=limit)
            except subprocess.TimeoutExpired:
                code = None
            finally:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except (OSError, AttributeError):
                    child.kill() if child.poll() is None else None
        seconds = time.time() - began
    if code != 0:
        sys.exit("REFUSED (LEVELS_L0_TIME): the row %s; only a passing run is a measurement, nothing was written" % (
            "ran past %d s" % limit if code is None else "exited %d" % code))
    return max(round(seconds, 1), 0.1)


def l0_reason(root, state, row, entry, seconds):
    """Why a measured, passing row still may not be L0, or ''."""
    if row["id"] in untimed(root):
        return "it is on the skip or known-red list"
    if (entry or {}).get("risk") in ("security", "private") or needs(state.risks, row["id"], row["goal"])[0] != "none":
        return "a tagged row is L1"
    if row["level"] == "covered":
        return "a covered row takes its covers' level"
    if seconds is not None and seconds >= UNDER:
        return "it took %.1f s, not under %d" % (seconds, UNDER)
    return ineligible(root, row["command"])


# -- the re-levelling

def read_input(path):
    """id TAB (a,b,c | own N[,N]) per line: covered rows' lists and defect rows' own-repository numbers."""
    covers, own, bad = {}, {}, []
    for n, line in enumerate((read(path) or "").split("\n"), 1):
        if not line.strip() or line[0] == "#":
            continue
        cells = line.split("\t")
        if len(cells) != 2:
            bad.append("%s line %d is not `id TAB value`" % (os.path.basename(path), n))
        elif cells[1].startswith("own "):
            own[cells[0]] = tuple(v.strip().lstrip("#") for v in cells[1][4:].split(","))
        else:
            covers[cells[0]] = ",".join(v.strip() for v in cells[1].split(",") if v.strip())
    return covers, own, bad


def read_times(path):
    out = {}
    for line in (read(path) or "").split("\n"):
        cells = line.split("\t")
        if len(cells) >= 2 and re.fullmatch(r"\d+(\.\d+)?", cells[1]) and float(cells[1]) > 0:
            out[cells[0]] = float(cells[1])
    return out


def pr_limit(root):
    found = re.findall(r"--timeout (\d+)", read(os.path.join(root, ".github", "workflows", "regression-pr.yml")) or "")
    return int(max(found, key=int)) if found else None


def risk_for(args):
    out = {}
    for item in args.risk_for or []:
        row, _, tag = item.partition("=")
        if tag not in ("security", "private", "none"):
            sys.exit("REFUSED: --risk-for takes ROW=security|private|none; nothing was written")
        out[row] = tag
    return out


class Plan:
    """What relevel will write, worked out before the lock: nothing partial is ever written."""

    def __init__(self, root, args):
        self.root, self.args = root, args
        self.state = State(root)
        self.first = not self.state.has_record
        self.times_file = args.times or os.path.join(root, ".github", "workflows", "row-times.tsv")
        self.input_file = args.input or file_of(root, "regression-relevel-input.tsv")
        self.times, self.limit = read_times(self.times_file), args.row_limit or pr_limit(root)
        self.covers, self.own, wrong = read_input(self.input_file)
        missing = ["risk data .loop/regression-risk.tsv (at least `requirement<TAB>-<TAB>none<TAB>why`): " + p.what
                   for p in self.state.bad_risks]
        if not self.times:
            missing.append("measured times: no `id TAB seconds` lines in %s (--times FILE)" % self.times_file)
        if not self.limit:
            missing.append("the per-row limit: the pull-request workflow gives no --timeout (--row-limit N)")
        if args.input and read(args.input) is None:
            missing.append("the input file %s" % args.input)
        if missing or wrong:
            sys.exit("REFUSED: relevel needs these first; nothing was written:\n  " + "\n  ".join(missing + wrong))
        writer_gate(self.state, True)
        have = self.state.entries()
        self.rows = [row for _, row in self.state.table if row["id"] not in have]
        self.seen, self.given = {}, risk_for(args)
        self.defects()

    def defects(self):
        """Each missing defect row's link class, all failures listed at once."""
        self.found, failed, deadline = {}, [], time.time() + ALL_SECONDS
        for row in self.rows:
            if row["category"] != "defect":
                continue
            try:
                self.found[row["id"]] = evidence(self.root, self.state.risks, row["link"],
                                                 self.own.get(row["id"], ()), self.seen, deadline)
            except Unread as error:
                if row["id"] not in self.given:
                    failed.append("%s: %s" % (row["id"], error))
        self.failed = failed

    def entries(self):
        """New entries for the missing rows, and the report lines."""
        state, root, limits = self.state, self.root, completion.limits(self.root)
        out, excluded, candidates, blocked = {}, {}, [], list(self.failed)
        skip, cache = untimed(root), {}

        def count(why, row=""):
            excluded.setdefault(why, []).append(row)
        for row in self.rows:
            key, old = row["id"], row["level"]
            entry = entry_for(row)
            seconds = None if key in skip else self.times.get(key)
            opts = {"evidence": self.found.get(key), "owner": self.args.owner_record}
            if old == "covered":
                opts["covers"] = self.covers.get(key, "")
                if not opts["covers"] and not excuse(row):
                    blocked.append("%s: a covered row with no covers line in the input file" % key)
                    continue
            if row["category"] == "defect":
                if key in self.given:
                    opts["risk"] = self.given[key]
                elif opts["evidence"] is None:
                    continue
            elif key in self.given:
                opts["risk"] = self.given[key]
            entry = derive(state, row, None, None, opts)
            tagged = entry["risk"] != "none"
            if old == "nightly" and not tagged:
                limit = completion.limit(root, key, self.limit)
                if limits.get(key) == "nightly":
                    entry["level"] = "L2"
                    reasoned(entry, "limits-file")
                elif seconds is not None:
                    entry["level"] = "L2" if seconds >= limit else "L1"
                    reasoned(entry, "time:%.1f" % seconds)
            if old == "land":
                if tagged:
                    count("tagged", key)
                elif key in skip:
                    count("on the skip or known-red list", key)
                elif seconds is None:
                    count("no measured time", key)
                elif seconds >= UNDER:
                    count("%d seconds or more" % UNDER, key)
                else:
                    why = ineligible(root, row["command"], cache)
                    if why:
                        count(why.split(" in ")[0].split(" names ")[0], key + " (" + why + ")")
                    else:
                        candidates.append((seconds, key, row))
            out[key] = entry
        have = state.entries()
        total = sum(ms(e["seconds"]) for e in have.values() if e["level"] == "L0")
        for seconds, key, row in sorted(candidates):
            if not self.first:
                count("L0 is set only by the first relevel or level --retime", key)
            elif total + ms(seconds) <= L0_MS:
                total += ms(seconds)
                out[key].update(level="L0", seconds="%.1f" % seconds, cmdhash=sha(row["command"]))
                reasoned(out[key], "time:%.1f" % seconds)
            else:
                count("past the 45 second total", key)
        return out, excluded, blocked, total

    def report(self, out, excluded, total):
        by = {}
        for entry in out.values():
            by[entry["level"]] = by.get(entry["level"], 0) + 1
        print("RELEVEL rows %d, entries %s%d: %s" % (len(self.state.table), "added " if not self.first else "",
              len(out), ", ".join("%s %d" % kv for kv in sorted(by.items()))))
        print("TIMES %s sha1 %s, per-row limit %d s" % (os.path.basename(self.times_file),
              sha(read(self.times_file) or "")[:12], self.limit))
        tags = [out[k]["risk"] for k in out if self.state.by_id[k]["category"] == "defect"]
        print("DEFECT tags: security %d, private %d, none %d" % tuple(tags.count(t) for t in ("security", "private", "none")))
        for why, rows in sorted(excluded.items()):
            print("NOT L0 %d: %s" % (len(rows), why))
            if not why.startswith(("tagged", "no measured", "%d seconds" % UNDER, "past")):
                print("  " + "; ".join(rows))
        zero = sorted(k for k, e in out.items() if e["level"] == "L0")
        print("L0 %d rows, %.1f s of 45: %s" % (len(zero), total / 1000.0, ", ".join(zero) or "none"))


def cmd_relevel(root, args):
    plan = Plan(root, args)
    out, excluded, blocked, total = plan.entries()
    if blocked:
        sys.exit("REFUSED: %d row(s) can't be levelled; nothing was written:\n  %s\nFix: a full issue URL, network and "
                 "gh sign-in; or --risk-for ROW=security|private (no owner record), ROW=none with --owner-record; "
                 "covers go in the input file" % (len(blocked), "\n  ".join(blocked)))
    if args.dry_run:
        plan.report(out, excluded, total)
        print("DRY RUN: nothing was written")
        return 0
    if not out:
        print("RELEVEL: every row has an entry; nothing to fill")
        return 0

    def change(state):
        have = state.entries()
        if {k for k in out if k in have} or any(state.by_id.get(k) != plan.state.by_id[k] for k in out):
            sys.exit("REFUSED: the table changed while relevel worked it out; nothing was written. Fix: rerun it")
        for key, tag in plan.given.items():
            if key in out:
                pin(state, key, tag, "given with --risk-for")  # GIVEN
        have.update(out)
        state.record = [(0, e) for e in have.values()]
        return set(out)
    update(root, change, creating=plan.first)
    plan.report(out, excluded, total)
    return 0
