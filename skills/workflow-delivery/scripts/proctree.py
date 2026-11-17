"""Stop a whole process tree, and ask about a pid, on every platform.

usage: import proctree   then proctree.kill(pid, signal.SIGTERM) for a child started with start_new_session=True,
proctree.probe(pid) where os.kill(pid, 0) was (ProcessLookupError when gone), proctree.pstart(pid) for the process's
start time (a reused pid reads differently), and proctree.alive(pid) on Windows.

POSIX: kill is os.killpg, so the child's whole session goes; pstart is ps. Windows has no process group a signal
reaches (and os.kill(pid, 0) there sends Ctrl+C, os.getuid and ps do not exist), so kill runs taskkill /T /F, which stops
the child and every process it started, and alive and pstart ask the process itself. Either kill is quiet when gone.
Also here, so each skill holds one identical copy: alive_since, tmp_for and rm_tmp (lane.py), FLOW, TEMPLATE and flow_set (goal.py),
and outcap, outcap_free and Capped (the 2,000-character output cap goal.py, flow.py and sessions.py install, GRD-15).
"""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zlib

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


if __name__ == "__main__":
    print(__doc__.strip())
