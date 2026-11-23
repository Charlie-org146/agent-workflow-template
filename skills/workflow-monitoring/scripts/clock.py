#!/usr/bin/env python3
"""DEL-17: a time limit per step and change size (reports, never stops a step), lead time per step and goal as compact
cards, missed steps with their cause, the ETA basis's history, and a few helpers the board scripts moved here.

The setting `step_report_limits` is text, `[doc:|code:]name=minutes` entries joined by commas (`build=45,code:tests=30`);
name is a step of steps.STEPS, `PR checks`, `push to main` or a check (health, docs check, board), matched ignoring case
and space, hyphen or underscore; minutes are 1 to 1440, or `off` / `0` for no limit. Order: the size's entry, the bare
entry, the owner's named default (DEFAULTS), else the measured usual (median of the last 20 finished goals, named for
the machine it was read on). A card carries what it was read from and its clock time (CHK-1). clock decides and writes
nothing; the step-end writer of the steps goal logs the line `missed (was <N>m, limit <L>m): <cause>` clock.missed returns."""
import datetime
import importlib
import json
import math
import os
import re
import statistics
import time
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")  # no prompt ever blocks a git or gh call

CHECKS = ("health", "docs check", "board")
EXTRA = ("PR checks", "push to main", "queue to main", "pr to queue")
# The owner's named values (o755, o748): (name, size) in minutes; size None is both. Nothing else is named.
DEFAULTS = {("quick checks", None): 1, ("tests", None): 5, ("merge", None): 5, ("PR checks", "doc"): 5, ("PR checks", "code"): 30,
            ("push to main", "doc"): 3, ("push to main", "code"): 35,
            ("queue to main", None): 10, ("pr to queue", None): 1}  # DEL-27.4 (queue to main) and DEL-27.1 (a PR opens) (o742)
DOC = re.compile(r"^(docs|tests?|dev/toy)/|\.md$|(^|/)test[-_.]|[-_.]test\.")  # release.auto_need's pattern (release.py)
LINE = re.compile(r"\bmissed \(was (\d+)m, limit (\d+)m\): (.*)$")
CTX = {}


def steps():
    """The step names of the one list (steps.py of the steps goal), or () while it is not installed."""
    try:
        return tuple(one_list().STEPS)
    except ImportError:
        return ()


def one_list():
    """steps.py of the steps goal, from workflow-delivery's scripts folder (by path, like board_lines' fit.py)."""
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workflow-delivery", "scripts")
    sys.path.append(here) if here not in sys.path else None
    return importlib.import_module("steps")


def safe(show):
    """A display function that never breaks the board or the check-in: any failure is one CLOCK_ERROR line."""
    def run(*args, **kw):
        try:
            return show(*args, **kw)
        except Exception as error:  # noqa: BLE001 (the board must render whatever the records hold)
            if os.environ.get("LOOP_DEBUG"):
                import traceback
                traceback.print_exc()
            return ["clock unavailable (CLOCK_ERROR: %s); LOOP_DEBUG=1 prints the trace" % type(error).__name__]
    return run


def norm(name):
    return re.sub(r"[ _-]+", " ", str(name).strip().lower())


def names():
    return {norm(n): n for n in steps() + EXTRA + CHECKS}


def parse(text):
    """{(size, name): minutes or None for off}; ValueError names the entry that is wrong."""
    found, known = {}, names()
    for raw in str(text or "").split(","):
        entry = raw.strip()
        if not entry:
            if str(text or "").strip():
                raise ValueError("an empty entry in step_report_limits")
            continue
        key, _, value = entry.rpartition("=")
        size, _, name = key.rpartition(":")
        size, name, value = size.strip().lower(), norm(name), value.strip().lower()
        if size not in ("", "doc", "code") or name not in known or not (value == "off" or re.fullmatch(r"\d{1,4}", value)):
            raise ValueError("step_report_limits entry %r is not [doc:|code:]<name>=<minutes>; names: %s; minutes 1 to 1440 or off"
                             % (one(entry, 60), ", ".join(known.values())))
        minutes = None if value in ("off", "0") else int(value)
        if minutes is not None and not 1 <= minutes <= 1440:
            raise ValueError("step_report_limits entry %r: minutes must be 1 to 1440 or off" % one(entry, 60))
        if (size or None, known[name]) in found:
            raise ValueError("step_report_limits names %r twice" % known[name])
        found[(size or None, known[name])] = minutes
    return found


def one(text, size):
    """One printable line of at most size characters."""
    return "".join(ch for ch in str(text) if ch.isprintable())[:size]


def limits(cfg):
    """(parsed settings, the bad-entry message or "") from a config dict; a bad value gives no settings."""
    try:
        return parse((cfg or {}).get("step_report_limits", "")), ""
    except ValueError as error:
        return {}, str(error)


def limit(cfg, step, size="code", usual=None):
    """(minutes, source): source is "setting", "named" or "usual"; (None, "off") when switched off, (None, "awaiting history")
    when no value is named and fewer than 3 goals have finished."""
    set_, _ = limits(cfg)
    for key in ((size, step), (None, step)):
        if key in set_:
            return (set_[key], "setting") if set_[key] else (None, "off")
    for key in ((step, size), (step, None)):
        if key in DEFAULTS:
            return DEFAULTS[key], "named"
    mine = (usual or {}).get(step)
    return (mine, "usual") if mine else (None, "awaiting history")


def unset(cfg, usual=None):
    """The names with no limit yet, and how many were switched off by choice: ([names], n)."""
    gone, off = [], 0
    for name in names().values():
        for size in ("doc", "code"):
            got = limit(cfg, name, size, usual)
            if got[1] == "off":
                off += 1
            elif got[0] is None and name not in gone:
                gone.append(name)
    return gone, off


def size(run):
    """doc when every touch outside .loop/ of the goal's recorded touches matches release.auto_need's pattern, else code."""
    touches = [t for t in (run.get("touches") or []) if not str(t).startswith(".loop")]
    return "doc" if touches and all(DOC.search(str(t).rstrip("/") + "/") or DOC.search(str(t)) for t in touches) else "code"


def minutes_of(entries):
    """{step: minutes}, a step done twice summing its attempts."""
    out = {}
    for e in entries:
        out[e["step"]] = out.get(e["step"], 0) + int(e.get("minutes") or 0)
    return out


def usual(runs):
    """{name: median minutes over the last 20 finished goals}, only where at least 3 goals finished: the steps from steps.entries
    (none while that list is absent) and the checks (health, docs check, board) from a run record's `check_seconds` map."""
    try:
        listing = one_list()
    except ImportError:
        listing = None
    done = [r for r in runs if isinstance(r, dict) and r.get("status") == "done"][-20:]
    seen = {}
    for r in done:
        for step, mins in (minutes_of(listing.entries(r)) if listing else {}).items():
            seen.setdefault(step, []).append(mins)
        for name, secs in (r.get("check_seconds") if isinstance(r.get("check_seconds"), dict) else {}).items():
            if name in CHECKS and isinstance(secs, (int, float)):
                seen.setdefault(name, []).append(int(secs // 60))
    return {s: int(statistics.median(v)) for s, v in seen.items() if len(v) >= 3}


def machine():
    return os.environ.get("LOOP_MACHINE_NAME") or ("mac" if sys.platform == "darwin" else "pc")


def span(minutes):
    return "%dm" % minutes if minutes < 60 else "%dh%02dm" % (minutes // 60, minutes % 60)


def missed(entry, cfg, size="code", usual=None):
    """The line `missed (was <N>m, limit <L>m): <cause>` for an entry {step, attempt, minutes, causes, waiting, budget_hits}, or None."""
    mins, _ = limit(cfg, entry["step"], size, usual)
    if not mins or int(entry.get("minutes") or 0) <= mins:
        return None
    causes = list(entry.get("causes") or []) or ([entry["waiting"]] if entry.get("waiting") else [])
    hits = entry.get("budget_hits") or []
    cause = one(causes[0] if causes else ("a budget hit: %s" % hits[0] if hits else "no cause recorded"), 120)
    return "missed (was %dm, limit %dm): %s" % (int(entry["minutes"]), mins, cause)


def loop_dir(root):
    """<git common dir>/loop of the checkout at root, or ""."""
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return os.path.join(os.path.abspath(os.path.join(root, common)), "loop") if common else ""


def context():
    """The render's config, time and measured usual; begun on first use at the checkout the process runs in."""
    if not CTX.get("root"):
        try:
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=5).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            top = ""
        CTX["diag"] = begin(top or os.getcwd())
    if CTX.get("usual") is None:
        runs = []
        folder = os.path.join(loop_dir(CTX["root"]), "runs")
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            try:
                runs.append(json.load(open(os.path.join(folder, name)))) if name.endswith(".json") else None
            except (OSError, ValueError):
                pass
        CTX["usual"] = usual(runs)
    return CTX


@safe
def begin(root, at=None):
    """Start a render: read the config at the checkout's root once; return its diagnostic lines (one if the setting is unreadable)."""
    try:
        cfg = json.load(open(os.path.join(root, ".loop", "config.json")))
    except (OSError, ValueError):
        cfg = {}
    cfg = cfg if isinstance(cfg, dict) else {}
    _, bad = limits(cfg)
    CTX.update(root=root, cfg=cfg, at=at or datetime.datetime.now(datetime.timezone.utc), usual=None, gh_end=time.monotonic() + 10)
    return ["step_report_limits unreadable (STEP_LIMITS_BAD): %s; template defaults apply. Fix: edit .loop/config.json, then run settings.py fill-repo." % bad] if bad else []


def pr_checks(run):
    """Wall minutes from the push to the last required check going green, or None (gh failed, no pull request, still running)."""
    pr = str(run.get("pr") or "")
    if not pr:
        return None
    try:
        left = CTX.setdefault("gh_end", time.monotonic() + 10) - time.monotonic()  # one 10 s allowance for every goal of a render
        if left <= 0:
            return None
        done = subprocess.run(["gh", "pr", "checks", pr, "--required", "--json", "startedAt,completedAt,state"], capture_output=True, text=True, timeout=left)
        rows = json.loads(done.stdout) if done.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    if not rows or any(r.get("state") != "SUCCESS" for r in rows):
        return None
    def when(text):
        return datetime.datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    try:
        return int((max(when(r["completedAt"]) for r in rows) - min(when(r["startedAt"]) for r in rows)).total_seconds() // 60)
    except (KeyError, ValueError):
        return None


def card(head, body, source, at):
    """A card: a header, indented lines of at most 60 columns, and what it was read from with the clock time."""
    import textwrap
    rows = [y for x in body for y in textwrap.wrap(one(x, 400), 58, subsequent_indent="  ") or [""]]
    return [one(head, 60)] + ["  " + y for y in rows] + ["  read from %s, %s" % (one(source, 36), at.astimezone().strftime("%H:%M"))]


def wrap(parts, width=58):
    lines, line = [], ""
    for part in parts:
        if line and len(line) + 2 + len(part) > width:
            lines.append(line)
            line = ""
        line += (", " if line else "") + part
    return lines + [line] if line else lines


@safe
def lead_line(run, cfg=None, now=None):
    """The lead card of one goal (see the module doc), or [] when the goal has no log or the steps list is absent."""
    if not run.get("log") or not steps():
        return []
    listing = one_list()
    ctx = context()
    cfg, at, mine = cfg if cfg is not None else ctx["cfg"], now or ctx["at"], size(run)
    entries = listing.entries(run)
    per = minutes_of(entries)
    head = "[lead] %s %s in all" % (run.get("slug", "?"), span(sum(per.values())))
    body = wrap(["%s %s" % (s, span(m)) for s, m in per.items() if m])
    logged = {}
    for text in map(str, run.get("log") or []):
        found = LINE.search(text)
        named = [s for s in per if s in text[:found.start()]] if found else []
        named and logged.setdefault(max(named, key=len), found.group(0))  # the longest name: "after the merge" is not "merge"
    for s in per:
        mine_line = logged.get(s) or missed(dict(next(e for e in entries if e["step"] == s), minutes=per[s]), cfg, mine, ctx["usual"])
        if mine_line:
            body.append("%s: %s" % (s, mine_line if s in logged else "(derived) " + mine_line))
    for s in per:
        if limit(cfg, s, mine, ctx["usual"])[1] == "usual":
            body.append("%s limit %dm (measured usual on %s)" % (s, ctx["usual"][s], machine()))
    held = re.search(r"hold=main-red:(\w+)", str(run.get("release_error") or ""))
    body += ["release held by main-red (%s); rerun merge.py once it is resolved" % held.group(1)] if held else []
    if run.get("pr"):
        got = pr_checks(run)
        body.append("PR checks %s" % (span(got) if got is not None else "unavailable"))
        late = got is not None and missed({"step": "PR checks", "minutes": got, "causes": ["the required checks took %dm" % got]}, cfg, mine)
        body += [late] if late else []
    return card(head, body, "%s.json log" % run.get("slug", "?"), at)


@safe
def lead_for(slug, at=None):
    """lead_line for a goal named by its slug (the check-in prints through board_lines.bars); the run record is read from the common dir."""
    ctx = context()
    diag, ctx["diag"] = ctx.pop("diag", []), []
    try:
        run = json.load(open(os.path.join(loop_dir(ctx["root"]), "runs", slug + ".json")))
    except (OSError, ValueError):
        return diag
    return diag + lead_line(run, None, at)


@safe
def merged_lines(runs, gone, n=5):
    """The Shipped cards: the last n merged goals, each its lead card (per-step minutes) under the header `[shipped] <slug>`; nothing when none."""
    out = []
    for r in sorted((r for r in runs if r["slug"] in gone), key=lambda r: str(r.get("updated")))[-n:][::-1]:
        lead = lead_line(r)
        out += (["[shipped] " + lead[0][len("[lead] "):]] + lead[1:]) if lead else []
    return out


def check_missed(name, seconds, cfg):
    """The line for a check that took too long (health, docs check, board), or None; the caller measured the seconds."""
    mins, _ = limit(cfg, name, "code")
    return "missed (was %dm, limit %dm)" % (int(seconds // 60), mins) if mins and seconds > mins * 60 else None


def basis_suffix(runs, at, root):
    """The history an ETA's basis rests on, from board_model's backtest: its count of scored goals and typical error."""
    import board_model as bm
    at = at or datetime.datetime.now(datetime.timezone.utc)
    try:
        m = bm.model(runs, at, root)
        if "scores" not in m:
            bm.backtest(runs, at, root)
        scores, n = m.get("scores", ({}, 0))
        if not scores:
            return ", too few finished goals (%d of %d)" % (n, bm.MIN_BACKTEST)
        return ", scored on %d past goals, typically off by a factor of %.1f (repo-wide)" % (n, math.exp(scores[bm.chosen(runs, at, root)]))
    except (ArithmeticError, ValueError, TypeError, KeyError) as error:
        return ", clock unavailable (CLOCK_ERROR: %s)" % type(error).__name__


def cache_path(root):
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return os.path.join(os.path.abspath(os.path.join(root, common)), "loop", "pr-states.json") if common else ""


if __name__ == "__main__":
    if sys.argv[1:2] == ["check"] and len(sys.argv) == 3:  # settings.py fill-repo validates the setting through this
        try:
            parse((json.load(open(sys.argv[2])) if os.path.exists(sys.argv[2]) else {}).get("step_report_limits", ""))
        except ValueError as error:
            sys.exit("REFUSED (STEP_LIMITS_BAD): %s. Fix: edit .loop/config.json and run settings.py fill-repo again. Nothing was changed. "
                     "See docs/wiki/How-to-use-Delivery.md" % error)
