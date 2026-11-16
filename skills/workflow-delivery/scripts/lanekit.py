#!/usr/bin/env python3
"""The lane's kit, imported by lane.py and goal.py; not a command. Parts:
1. Copies of the slots.py pieces lane.py uses (COPIED, flow_file ... rows_line): each must match
   workflow-regression/scripts/slots.py exactly; dev/toy/test-lane-control.sh fails on drift.
2. The one commit a lane may make before it starts (prep, generated): re-rendered Tests tables and run dates, else LANE_DIRTY;
   a refused or hung commit starts nothing (LANE_PREP_FAILED).
3. record(state, base), run by goal.py pr after its lane passes: issue states, run results, one commit, then pr_lane, pr_head
   and pr_base for merge.py's checks.
4. Step budgets: step_budget_minutes (30), test_budget_minutes (15), neither under 15; budget_hits names what a stopped step left.
5. Who may signal a lane: pstart/same, audit (runs/kills.log) and died/death (LANE_DIED).
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

import tempfile
import proctree
from proctree import pstart  # noqa: F401
try:
    import fcntl
except ImportError:
    import msvcrt
    import types

    def _flock(handle, op):
        fd = handle if isinstance(handle, int) else handle.fileno()
        here = os.lseek(fd, 0, 1)
        os.lseek(fd, 0x7FFFFFFF, 0)
        try:
            while True:
                try:
                    return msvcrt.locking(fd, msvcrt.LK_UNLCK if op & 8 else msvcrt.LK_NBLCK, 1)
                except OSError:
                    if op & 8:
                        return
                    if op & 4:
                        raise BlockingIOError("locked")
                    time.sleep(0.05)
        finally:
            os.lseek(fd, here, 0)

    fcntl = types.SimpleNamespace(LOCK_SH=1, LOCK_EX=2, LOCK_NB=4, LOCK_UN=8, flock=_flock)

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.normpath(os.path.join(HERE, "..", "..", "workflow-regression", "scripts"))
NOTHING = "the lane committed and pushed nothing"
BOOKKEEPING = (".loop/regression-runs.tsv", ".loop/goals/", ".loop/queue.md", ".loop/findings.md")
FILES = (".loop/regression-issues.tsv", ".loop/regression-runs.tsv")
EXIT_WAIT, EXIT_STALE, EXIT_ENV, POLL = 4, 5, 6, 2.0
EXIT_PREP = 125
TERMINAL = ("pass", "fail")
COPIED = ('flow_file', '_flow', 'time_limit', 'lanes_dir', 'check', '_open', 'port_base', 'last_change', 'lane_limit', 'timeout_line', 'rows_line')


def flow_file():
    return os.path.expanduser(os.environ.get("LOOP_FLOW") or "~/.workflow-loop/flow.json")


def _flow():
    try:
        data = json.load(open(flow_file()))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def time_limit(root):
    """A lane's time limit in seconds and its source: the flow file's limit, else step_limit, else 2700."""
    value = _flow().get("limit")
    if value:
        return float(value), "flow file limit"
    try:
        value = json.load(open(os.path.join(root, ".loop", "config.json"))).get("step_limit")
    except (OSError, ValueError, AttributeError):
        value = None
    return (float(value), "step_limit") if value else (2700.0, "the default")


def lanes_dir():
    return os.path.realpath(os.path.expanduser(os.environ.get("LOOP_LANES_DIR") or "~/.workflow-loop/lanes"))


def check(pool):
    """Create the pool 0700; refuse one that isn't yours or that others can write (OSError names why)."""
    os.makedirs(pool, mode=0o700, exist_ok=True)
    if os.name == "nt":
        return
    info = os.stat(pool)
    if info.st_uid != getattr(os, "getuid", lambda: 0)() or info.st_mode & 0o022:
        raise OSError("not owned by you, or writable by group or others")


def _open(path, flags=0):
    return os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | flags, 0o600)


def port_base():
    """(fd, base) for a lane's own ports (REG-8): flock the first free port-N file (N 0..99) in the pool and return
    20000 + 100 * N, held while fd stays open; (None, why) when the pool is unavailable or all 100 are held."""
    try:
        pool = lanes_dir()
        check(pool)
        for number in range(100):
            fd = _open(os.path.join(pool, "port-%d" % number))
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd, 20000 + 100 * number
            except BlockingIOError:
                os.close(fd)
    except OSError as error:
        return None, "port pool unavailable: %s" % error
    return None, "no port lease free (100 in use)"


def last_change(pool):
    """The newest slot-file change: the queue clock (any slot taken restarts a waiting lane's span)."""
    times = [os.path.getmtime(path) for path in glob.glob(os.path.join(pool, "slot-*"))]
    return max(times) if times else 0.0


def lane_limit(held):
    """(seconds, source) of a lane's time limit."""
    return held["limit"], held.get("source", "flow file limit")


def timeout_line(text, why, held):
    """The LANE_TIMEOUT line."""
    return ("LANE_TIMEOUT: %s; the lane was killed, rows partly ran, nothing committed or pushed. Fix: run the same "
            "command again, or raise the flow file \"limit\" (else step_limit)." % why)


def budget_note(text, base, name):
    cut = re.findall(r"^BUDGET (\d+) min: .*?LEFT \d+ to the scheduled full suite: (.*)$", text, re.M)
    if not cut:
        return ""
    hit(os.path.dirname(base), os.path.basename(base)[:-len(".%s-lane" % name)], name, "test", int(cut[-1][0]), cut[-1][1])
    return "\n" + re.findall(r"^BUDGET .*$", text, re.M)[-1]


def rows_line(text, ran, log):
    """The LANE line's end (DX-12, DX-18 ROWS): the goal tier's ROWS counts, the selected rows a timeout left unfinished,
    and the lane log."""
    found = re.search(r"^ROWS: (\d+) selected (\(.*?\)), (\d+) reused; unmapped: (\d+)$", text, re.M)
    if not found:
        return "; log: %s" % log
    count, parts, reused, loose = found.groups()
    return "; rows: %s selected %s, %s reused, %d unfinished; unmapped: %s; log: %s" % (
        count, parts, reused, max(int(count) - ran, 0), loose, log)



def mtime(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def drop(*paths):
    for path in paths:
        try:
            os.remove(path)
        except (FileNotFoundError, TypeError):
            pass


def read_json(path):
    try:
        data = json.load(open(path))
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def set_last(path, attempt, **fields):
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        old = read_json(path) or {}
        if old.get("attempt") == attempt and old.get("state") in TERMINAL:
            return old
        data = dict(old if old.get("attempt") == attempt else {}, attempt=attempt, **fields)
        temp = "%s.%d.tmp" % (path, os.getpid())
        with open(temp, "w") as handle:
            json.dump(data, handle, indent=1, sort_keys=True)
        os.replace(temp, path)
        return data



def holders(pool):
    out = []
    for path in sorted(glob.glob(os.path.join(pool or "", "slot-*"))):
        label = (read_json(path) or {}).get("label")
        if label:
            out.append(str(label)[:60])
    return out


def timing(held, rc):
    data = read_json(rc + ".times") or {}
    num = lambda key: float(data[key]) if isinstance(data.get(key), (int, float)) and not isinstance(data.get(key), bool) else 0.0
    return num("plan"), num("wait"), str(data.get("cut") or "")


def before_rows(held, plan, wait):
    note = "; before rows: prep %ds, planning %ds, slot wait %ds" % (held.get("prep_s") or 0, plan, wait)
    return note + ("; LOOP_PREP_BUDGET in effect" if held.get("override") else "")


def cut_line(name, held, plan, wait, part):
    got = ", ".join(holders(held.get("pool"))) or "none"
    return ("LANE_PREP_BUDGET: the %s lane used its %s preparation budget before any row ran: %s ran long (prep %ds, "
            "planning %ds, slot wait %ds; the three share one budget); slots held by: %s; no row ran, %s beyond the prep "
            "commit. Fix: run the same command again (it replans on this HEAD); raise prep_budget_minutes only if prep or "
            "planning is the part that ran long." % (name, "%ds (LOOP_PREP_BUDGET)" % held["budget"] if held.get("override") else "%d-minute" % round(held.get("budget", 0) / 60),
                                                      part or "preparation",
                                                      held.get("prep_s") or 0, plan, wait, got, NOTHING))


def prep_hit(base, name, held, plan, wait, part):
    left = "%s ran long (prep %ds, planning %ds, slot wait %ds)" % (part or "preparation", held.get("prep_s") or 0, plan, wait)
    hit(os.path.dirname(base), os.path.basename(base)[:-len(".%s-lane" % name)], name, "prep",
               round(held.get("budget", 0) / 60), left)


def same(pid, start):
    return bool(start) and pstart(pid) == start


def audit(runs, who, pid, why):
    with open(os.path.join(runs, "kills.log"), "a") as handle:
        handle.write("%s %s -> %s (%s): %s\n" % (time.strftime("%FT%T"), who, pid, pstart(pid), why))


def died(log, sig=""):
    return "LANE_DIED: the lane ended with no exit status%s (log %s); %s" % (" (killed by %s)" % sig if sig else "", log, NOTHING)


def death(base, log, sig=""):
    return "fail", died(log, sig), []


def running_line(held, other=None):
    if other:
        return "WAITING: the %s lane of this goal is still running; run this same command again, or block with role.py " \
            "lane-wait SLUG %s" % (other, other)
    queued = held["rc"] + ".queued"
    if os.path.exists(queued):
        return "WAITING: %s; run this same command again" % open(queued).read().strip()
    if "markers" in held and not os.path.exists(held["rc"] + ".started"):
        return "RUNNING: planning the lane; run this same command again"
    return "RUNNING: the regression lane is running; run this same command again"



def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True)


def dirty():
    out = git("status", "--porcelain", "--no-renames", "--untracked-files=all").stdout
    return [line[3:].strip('"') for line in out.splitlines() if not line[3:].strip('"').startswith(BOOKKEEPING)]


def generated(cfg):
    return [p for p in dirty() if is_page(p, cfg) and tests_only(p)]


def is_page(path, cfg):
    return path.startswith((cfg.get("wiki_dir") or "docs/wiki").rstrip("/") + "/") and path.endswith(".md")


def tests_only(path):
    if os.path.basename(path) == "Tests.md":
        return True
    now = open(path).read() if os.path.exists(path) else None
    shown = git("show", "HEAD:" + path)
    if now is None or shown.returncode:
        return False
    return outside(now) == outside(shown.stdout) if outside(shown.stdout) is not None else now == shown.stdout


def outside(text):
    found = re.search(r"^## Tests[ \t]*$", text, re.M)
    if not found:
        return None
    rest = re.search(r"^## ", text[found.end():], re.M)
    return text[:found.start()] + (text[found.end() + rest.start():] if rest else "")


def prep(top, cfg, log):
    criteria = os.path.normpath(os.path.join(HERE, "..", "..", "workflow-docs", "scripts", "criteria.py"))
    for path in dirty():
        if not (is_page(path, cfg) and tests_only(path)):
            if is_page(path, cfg):
                return None, "LANE_DIRTY: %s has edits above its ## Tests section; commit or revert them, then run the " \
                    "same command again; %s." % (path, NOTHING)
            return None, "LANE_DIRTY at start: %s. Fix: commit or remove them; %s." % (", ".join(dirty()[:10]), NOTHING)
    if not os.path.exists(os.path.join(top, ".loop", "docs.tsv")) or not os.path.exists(criteria):
        return "", None
    done = subprocess.run([sys.executable, criteria, "render", "--tables"], cwd=top, capture_output=True, text=True, timeout=300)
    if done.returncode:
        first = (done.stderr or done.stdout).strip().splitlines()[-1:] or ["exit %d" % done.returncode]
        return None, "LANE_PREP_FAILED: criteria.py render failed: %s. Fix: run it by hand; %s." % (first[0][:200], NOTHING)
    paths = [p for p in dirty() if is_page(p, cfg)]
    if git("status", "--porcelain", "--", ".loop/regression-runs.tsv").stdout.strip():
        paths.append(".loop/regression-runs.tsv")
    if not paths:
        return "", None
    proc = subprocess.Popen(["git", "commit", "--only", "-q", "-m", "Lane: re-render the Tests tables", "--"] + paths,
                            cwd=top, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, stdin=subprocess.DEVNULL,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=60)
        why = (err or out).strip().splitlines()[-1:] if proc.returncode else None
    except subprocess.TimeoutExpired:
        proctree.kill(proc.pid)
        out, err = proc.communicate()
        lock = os.path.join(top, git("rev-parse", "--git-path", "index.lock").stdout.strip())
        if os.path.exists(lock):
            os.remove(lock)
        why = ["timed out after 60s"]
    if why is not None:
        with open(log, "a") as handle:
            handle.write("prep commit: %s\n%s\n" % (" ".join(paths), err or out or ""))
        git("reset", "-q", "--", *paths)
        return None, ("LANE_PREP_FAILED: git commit failed: %s (full output: %s); the prep paths are unstaged and left "
                      "modified, nothing committed or pushed. Fix: make the commit pass (see the log), then run role.py lane "
                      "SLUG NAME again." % ((why or ["no message"])[0][:200], log))
    return "LANE_PREP: re-rendered the Tests tables (commit %s)" % git("rev-parse", "--short", "HEAD").stdout.strip(), None



FLOOR = 15
DEFAULTS = {"step_budget_minutes": 30, "test_budget_minutes": 15, "prep_budget_minutes": 15}
LEFT = re.compile(r"^\W*BUDGET:\s*left:\s*(.+)$", re.M | re.I)


def minutes(cfg, key):
    value = cfg.get(key, DEFAULTS[key])
    if isinstance(value, bool) or not isinstance(value, int) or value < FLOOR:
        sys.exit("REFUSED: %s is %r in .loop/config.json, under the %d-minute floor. Fix: set it to %d or more." % (
            key, value, FLOOR, FLOOR))
    return value


def prep_seconds(cfg):
    value = os.environ.get("LOOP_PREP_BUDGET", "")
    if value.isdigit() and int(value) > 0:
        return int(value), True
    return minutes(cfg, "prep_budget_minutes") * 60, False


def label(hit):
    return {"step": "step", "prep": "preparation"}.get(hit.get("kind"), "tests")


def seconds(cfg, key, limit=0):
    budget = minutes(cfg, key) * 60
    return min(budget, limit) if limit else budget


def left_of(text):
    found = LEFT.findall(text or "")
    return " ".join(found[-1].split())[:300] if found else ""


def hit(runs, slug, step, kind, limit, left):
    path = os.path.join(runs, slug + ".json")
    try:
        with open(path) as handle:
            state = json.load(handle)
    except (OSError, ValueError):
        return
    kept = [h for h in state.get("budget_hits") or [] if not (h.get("step") == step and h.get("kind") == kind)]
    state["budget_hits"] = kept + [{"step": step, "kind": kind, "minutes": limit, "left": left or "not stated"}]
    with tempfile.NamedTemporaryFile("w", dir=runs, delete=False, suffix=".tmp") as handle:
        json.dump(state, handle, indent=2)
    os.replace(handle.name, path)


def reached(state, step):
    return any(h.get("step") == step and h.get("kind") == "step" for h in state.get("budget_hits") or [])


def lines(state):
    return ["%s: %s hit its %s-minute budget; left: %s" % (
        state.get("slug", "?"), "%s %s" % (h.get("step"), label(h)), h.get("minutes"),
        h.get("left")) for h in state.get("budget_hits") or [] if isinstance(h, dict)]


def mend(git, files, base):
    top, tsv = git("rev-parse", "--show-toplevel").stdout.strip(), (".loop/regression.tsv", ".loop/regression-runs.tsv")
    page = lambda f: os.path.basename(f) == "Tests.md" and os.path.dirname(f).endswith("wiki")
    criteria = os.path.join(HERE, "..", "..", "workflow-docs", "scripts", "criteria.py")
    if not files or not all(f in tsv or page(f) for f in files):
        return False
    if any(page(f) for f in files) and not (os.path.exists(top + "/.loop/docs.tsv") and os.path.exists(criteria)):
        return False
    for f in files:
        s = [git("show", ":%d:%s" % (n, f)) for n in (1, 2, 3)]
        if s[1].returncode or s[2].returncode:
            return False
        if f not in tsv:
            git("checkout", "--theirs", "--", f)
            continue
        with tempfile.TemporaryDirectory() as tmp:
            for n, r in zip("abc", (s[1], s[0], s[2])):
                open(tmp + "/" + n, "w").write(r.stdout if not r.returncode else "")
            union = subprocess.run(["git", "merge-file", "-p", "--union"] + [tmp + "/" + n for n in "abc"],
                                   capture_output=True, text=True).stdout
        rows = lambda t: {l.split("\t")[0]: l for l in t.splitlines() if l and l[0] != "#"}
        b, o, t = rows(s[0].stdout if not s[0].returncode else ""), rows(s[1].stdout), rows(s[2].stdout)
        if any(k not in o or k not in t for k in b):
            return False
        out, at = [], {}
        for line in union.splitlines():
            k = line.split("\t")[0]
            if line[0:1] == "#" or not line or k not in at:
                at[k] = len(out)
                out.append(line)
            elif line != out[at[k]]:
                if f != tsv[1] or line.split("\t")[2:3] == out[at[k]].split("\t")[2:3]:
                    return False
                out[at[k]] = max(line, out[at[k]], key=lambda l: l.split("\t")[2:3])
        open(top + "/" + f, "w").write("\n".join(out) + "\n")
    if any(page(f) for f in files):
        if subprocess.run([sys.executable, criteria, "render", "--tables"], cwd=top, capture_output=True).returncode:
            return False
        git("add", "-u")
    if git("add", "--", *files).returncode or git("commit", "--no-edit", "-q").returncode:
        return False
    print("MENDED %s: rows unioned, Tests.md taken from %s and re-rendered" % (", ".join(files), base))
    return True
