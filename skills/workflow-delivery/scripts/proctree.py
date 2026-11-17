"""Stop a whole process tree, and ask about a pid, on every platform.

usage: import proctree   then proctree.kill(pid, signal.SIGTERM) for a child started with start_new_session=True,
proctree.probe(pid) where os.kill(pid, 0) was (ProcessLookupError when gone), proctree.pstart(pid) for the process's
start time (a reused pid reads differently), and proctree.alive(pid) on Windows.

POSIX: kill is os.killpg, so the child's whole session goes; pstart is ps. Windows has no process group a signal
reaches (and os.kill(pid, 0) there sends Ctrl+C, os.getuid and ps do not exist), so kill runs taskkill /T /F, which stops
the child and every process it started, and alive and pstart ask the process itself. Either kill is quiet when gone.
Also here, so each skill holds one identical copy: alive_since, tmp_for and rm_tmp (lane.py), FLOW, TEMPLATE and flow_set (goal.py),
and outcap, outcap_free and Capped (the 2,000-character output cap goal.py, flow.py and sessions.py install, GRD-15).
Tokens measured from a session's own transcript (DEL-16): transcript, calls, measure, add (a step's tokens into a run record), live,
fresh (input + cache writes + output, the budget's unit) and total (adds cache reads). A transcript is <projects>/<folder>/<session id>.jsonl
(the id is CLAUDE_CODE_SESSION_ID; LOOP_TRANSCRIPT_DIR replaces ~/.claude/projects); a call spanning several lines counts once by message.id,
subagents are left out, and nothing raises: an unreadable transcript measures nothing. tokens[step] is a measure {input, cache_read, cache_write,
output, calls, model, peak} or an int an older step reported. And the operation session's own turns (MON-5): classify, asked, needs_layout and
op_append, which adds a row to <git common dir>/loop/op-tokens.tsv, the tokens since the last row by trigger (scheduled, peer, human, hook-retry).
"""
import atexit
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zlib
from collections import Counter

os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")  # a child that asks for a password fails instead of waiting

if os.name == "nt":
    import ctypes

    def _k32():
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = ctypes.c_void_p  # a HANDLE: pointer-sized, never truncated to an int
        k32.CloseHandle.argtypes = [ctypes.c_void_p]
        k32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        k32.GetProcessTimes.argtypes = [ctypes.c_void_p] + [ctypes.POINTER(ctypes.c_ulonglong)] * 4
        return k32

    def kill(pid, sig=None):
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(int(pid))], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def alive(pid):
        try:
            pid = int(pid)
        except (TypeError, ValueError):
            return False
        k32 = _k32()
        handle = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5  # access denied: it runs, as EPERM on POSIX
        code = ctypes.c_ulong()
        try:
            return bool(k32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259  # STILL_ACTIVE
        finally:
            k32.CloseHandle(handle)

    def pstart(pid):
        k32 = _k32()
        handle = k32.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return ""
        times = [ctypes.c_ulonglong() for _ in range(4)]  # creation, exit, kernel, user
        try:
            return str(times[0].value) if k32.GetProcessTimes(handle, *[ctypes.byref(t) for t in times]) else ""
        finally:
            k32.CloseHandle(handle)

    def probe(pid):
        if not alive(pid):
            raise ProcessLookupError(pid)
else:
    import signal

    def kill(pid, sig=signal.SIGKILL):
        try:
            os.killpg(pid, sig)  # posix-only branch
        except OSError:  # already gone
            pass

    def probe(pid):
        os.kill(pid, 0)  # posix-only branch

    def pstart(pid):
        return subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()


def alive_since(pid, start=""):
    """A pid that runs, is no zombie and, given a start, still began then."""
    try:
        probe(pid)
    except PermissionError:
        pass
    except (OSError, TypeError):
        return False
    if start and pstart(pid) != start:
        return False
    return os.name == "nt" or subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()[:1] != "Z"


def tmp_for(top, slug, name):
    """REG-8: prefix of the lane's temp folder, outside every checkout; "" when the system temp is in one."""
    root = here = os.path.realpath(tempfile.gettempdir())
    while not os.path.lexists(here + "/.git") and os.path.dirname(here) != here:
        here = os.path.dirname(here)
    return "" if os.path.lexists(here + "/.git") else "%s/loop-lane-%08x-%s-%s-" % (root, zlib.crc32(os.path.realpath(top).encode()), slug, name)


def rm_tmp(held):
    path = (held or {}).get("tmp") or ""
    if os.path.basename(path).startswith("loop-lane-") and not os.path.islink(path):
        shutil.rmtree(path, ignore_errors=True)


FLOW_FILE = "~/.workflow-loop/flow.json"
NO_FLOW = ("no skill flow is set. Fix: write %s naming your idea, plan, review, test and ship skills and their "
           "unattended command (loop-files.md)." % FLOW_FILE)
FLOW = ("idea", "plan", "review", "qa", "ship")
TEMPLATE = """# {goal}

- Slug: {slug}
- Touches: {touches}
- ETA: {eta}

## Done lines

Frozen. A wrong done line needs a new goal.

{done}

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
"""


def flow_set():
    try:
        spec = json.load(open(os.path.expanduser(os.environ.get("LOOP_FLOW") or FLOW_FILE)))
        steps = dict(spec.get("suite") or {}, **(spec.get("steps") or {}))
    except (OSError, ValueError, AttributeError, TypeError):
        return False
    return all(steps.get(step) for step in FLOW)


class Capped:
    """stdout that keeps a script's first half and last half of anything over the cap (GRD-15, token-diet C10)."""

    def __init__(self, real, name, limit):
        self.real, self.name, self.limit, self.parts, self.sent, self.free = real, name, limit, [], 0, False

    def write(self, text):
        if self.free:
            return self.real.write(text)
        self.parts.append(text)
        room = self.limit // 2 - self.sent
        if room > 0:
            self.real.write(text[:room])
            self.sent += min(room, len(text))
        return len(text)

    def __getattr__(self, name):
        return getattr(self.real, name)

    def finish(self):
        text = "".join(self.parts)
        if len(text) <= self.limit:
            return self.real.write(text[self.sent:])
        try:
            top = subprocess.run(["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=10).stdout.strip()
            where = os.path.join(os.path.realpath(top), "loop", "out") if top else os.path.join(tempfile.gettempdir(), "loop-out")
            os.makedirs(where, exist_ok=True)
            for old in os.listdir(where):
                if time.time() - os.path.getmtime(os.path.join(where, old)) > 2 * 86400:
                    os.remove(os.path.join(where, old))
            path = os.path.join(where, "%s-%d.txt" % (os.path.basename(self.name), time.time()))
            with open(path, "w", encoding="utf-8", errors="replace") as handle:
                handle.write(text)
        except (OSError, subprocess.SubprocessError):
            path = "(could not be kept)"
        tail = text[-(self.limit // 2):]
        self.real.write("\n[... %d characters cut; the full output is in %s ...]\n%s" % (len(text) - self.sent - len(tail), path, tail))


def outcap(name=None):
    """Cap this script's stdout at 2,000 characters (LOOP_OUTPUT_CAP=N changes it, 0 turns it off); the full text is kept under
    <git common dir>/loop/out/. Call once, first thing in main(); outcap_free() prints one block uncapped."""
    given = os.environ.get("LOOP_OUTPUT_CAP", "")
    limit = int(given) if given.isdigit() else 2000
    if limit > 0 and not isinstance(sys.stdout, Capped):
        sys.stdout = Capped(sys.stdout, name or sys.argv[0] or "script", limit)
        atexit.register(sys.stdout.finish)


def outcap_free(on):
    """outcap_free(True) then print a block that must be read whole (a step's prompt); outcap_free(False) goes back to capping."""
    if isinstance(sys.stdout, Capped):
        sys.stdout.free = on


# --- tokens measured from a session's own transcript (DEL-16): per step for a worker, per trigger for the operation session
FIELDS = ("input", "cache_read", "cache_write", "output")
ID = re.compile(r"^[A-Za-z0-9_-]{8,128}$")


def stamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))


def transcript(session=None, base=None):
    session = session or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    base = base or os.environ.get("LOOP_TRANSCRIPT_DIR") or os.path.join(os.path.expanduser("~"), ".claude", "projects")
    if not ID.match(session):
        return ""
    found = sorted(glob.glob(os.path.join(base, "*", session + ".jsonl")))
    return found[0] if found else ""


def lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for text in handle:
                try:
                    found = json.loads(text)
                except ValueError:
                    continue
                if isinstance(found, dict):
                    yield found
    except OSError:
        return


def calls(path, since="", until="", turn=None):
    """One dict per model call of the main chain with since < time <= until (ISO, to the second), oldest first. turn(user
    line) may return a label for the turn that line starts; each call carries the label of the turn it first appeared in."""
    seen, label = {}, ""
    for number, line in enumerate(lines(path)):
        if turn and line.get("type") == "user" and not line.get("isSidechain"):
            label = turn(line) or label
        message = line.get("message")
        usage = message.get("usage") if isinstance(message, dict) else None
        if line.get("type") != "assistant" or line.get("isSidechain") or not isinstance(usage, dict) or message.get("model") == "<synthetic>":
            continue
        n = lambda key: usage.get(key) if isinstance(usage.get(key), int) and not isinstance(usage.get(key), bool) else 0
        at = str(line.get("timestamp") or "")[:19]
        item = {"at": at, "model": str(message.get("model") or ""), "input": n("input_tokens"), "cache_read": n("cache_read_input_tokens"),
                "cache_write": n("cache_creation_input_tokens"), "output": n("output_tokens")}
        item["context"] = item["input"] + item["cache_read"] + item["cache_write"]
        key = message.get("id") or line.get("uuid") or "line%d" % number
        item["turn"] = seen[key]["turn"] if key in seen else label
        seen[key] = item
    since, until = since[:19], until[:19]
    return sorted((c for c in seen.values() if c["at"] and c["at"] > since and (not until or c["at"] <= until)), key=lambda c: c["at"])


def measure(path, since="", until=""):
    """The window's measure, or None when it holds no call."""
    found = calls(path, since, until)
    if not found:
        return None
    out = {key: sum(c[key] for c in found) for key in FIELDS}
    models = Counter(c["model"] for c in found if c["model"])
    return dict(out, calls=len(found), model=models.most_common(1)[0][0] if models else "", peak=max(c["context"] for c in found))


def fresh(value):
    if isinstance(value, dict):
        return sum(int(value.get(k) or 0) for k in ("input", "cache_write", "output", "reported"))
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def total(value):
    return fresh(value) + (int(value.get("cache_read") or 0) if isinstance(value, dict) else 0)


def mark_of(state):
    """Where a goal's next window starts: the last measured instant, else its first log line (its freeze)."""
    first = ((state.get("log") or [""])[0] or "")[:19]
    return str(state.get("token_at") or (first if re.match(r"^\d{4}-\d\d-\d\dT", first) else ""))


def add(state, step, given, measure_it=False, now=None):
    """Add a step's tokens: a measured window since the goal's mark when measure_it (and a transcript is found), then any
    count the step reported (an int; unknown or none adds nothing)."""
    held = state.get("tokens") if isinstance(state.get("tokens"), dict) else {}
    old = held.get(step)
    got, until = None, now or stamp()
    path = transcript() if measure_it else ""
    if path and mark_of(state):
        got = measure(path, mark_of(state), until)
        state["token_at"] = until
    reported = int(given) if str(given).isdigit() else 0
    if got:
        mine = dict(old) if isinstance(old, dict) else {"reported": old} if isinstance(old, int) and old else {}
        for key in FIELDS + ("calls",):
            mine[key] = int(mine.get(key) or 0) + got[key]
        mine.update(model=got["model"], peak=max(int(mine.get("peak") or 0), got["peak"]))
        if reported:
            mine["reported"] = int(mine.get("reported") or 0) + reported
        state["tokens"] = dict(held, **{step: mine})
    elif reported:
        if isinstance(old, dict):
            state["tokens"] = dict(held, **{step: dict(old, reported=int(old.get("reported") or 0) + reported)})
        else:
            state["tokens"] = dict(held, **{step: reported + (old if isinstance(old, int) else 0)})


def live(state):
    """Fresh tokens spent since the last mark (a goal with no mark has none yet)."""
    path = transcript() if state.get("token_at") else ""
    got = measure(path, str(state["token_at"]), stamp()) if path else None
    return fresh(got) if got else 0


# --- the operation session's own turns (MON-5, C3, C4): classify each by what started it; op_append adds a row to op-tokens.tsv
TRIGGERS = ("scheduled", "peer", "human", "hook-retry")
HEADER = "# time\tsession\tcontext\t" + "\t".join(TRIGGERS) + "\ttotal"
PEER = ("finished a turn", "Another Claude session", "<task-notification", "<cross-session-message", "side-sessions-event",
        "<ci-monitor-event", "<session-message")
ASKED = re.compile(r"check[- ]?in|where do things stand|\bstatus\b|\breport\b|dashboard|\bboard\b", re.I)

def classify(text):
    text = str(text or "").lstrip()
    if text.startswith("Stop hook feedback"):
        return "hook-retry"
    if text.startswith("Operation") and "check-in" in text[:120].lower():
        return "scheduled"
    return "peer" if any(mark in text[:400] for mark in PEER) else "human"


def asked(text):
    return classify(text) == "human" and bool(ASKED.search(str(text or "")[:300]))


def text_of(entry):
    """A user entry's own words; None for one that only carries tool results."""
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b for b in content if isinstance(b, dict)]
        if parts and all(b.get("type") == "tool_result" for b in parts):
            return None
        return " ".join(str(b.get("text") or "") for b in parts if b.get("type") == "text")
    return None


def needs_layout(entries):
    """True when the last turn that was not a hook retry is a scheduled check-in or an owner's ask for one, or can't be read."""
    for entry in reversed(entries or []):
        if entry.get("type") != "user":
            continue
        text = text_of(entry)
        if text is None or classify(text) == "hook-retry":
            continue
        return classify(text) == "scheduled" or asked(text)
    return True


def common(root):
    done = subprocess.run(["git", "-C", root, "rev-parse", "--git-common-dir"], capture_output=True, text=True, timeout=10)
    return os.path.realpath(os.path.join(root, done.stdout.strip())) if done.returncode == 0 and done.stdout.strip() else ""


def turn_label(entry):
    text = text_of(entry)
    return classify(text) if text is not None else None


def op_row(root, now=None):
    """The line to append: the operation session's tokens since its last row, by trigger; None with no transcript."""
    folder = common(root)
    try:
        with open(os.path.join(folder, "loop", "operation.id")) as handle:
            claimed = {line.strip() for line in handle if line.strip()}
    except OSError:
        claimed = set()
    ids = sorted((s for s in claimed if transcript(s)), key=lambda s: os.path.getmtime(transcript(s)))
    if not ids:
        return None
    session, table = ids[-1], os.path.join(folder, "loop", "op-tokens.tsv")
    try:
        with open(table, encoding="utf-8") as handle:
            rows = [line.split("\t") for line in handle.read().splitlines() if line and line[0] != "#"]
    except OSError:
        rows = []
    last = max((r[0] for r in rows if len(r) > 1 and r[1] == session), default="")
    found = calls(transcript(session), last, "", turn_label)
    got = {name: sum(total(c) for c in found if c["turn"] == name) for name in TRIGGERS}
    return "\t".join([now or stamp(), session, str(found[-1]["context"] if found else 0)] + [str(got[n]) for n in TRIGGERS] + [str(sum(got.values()))])


def op_append(root, now=None):
    line = op_row(root, now)
    if not line:
        return ""
    table = os.path.join(common(root), "loop", "op-tokens.tsv")
    new = not os.path.exists(table)
    with open(table, "a", encoding="utf-8", newline="\n") as handle:
        handle.write((HEADER + "\n" if new else "") + line + "\n")
    return line


if __name__ == "__main__":
    print(__doc__.strip())
