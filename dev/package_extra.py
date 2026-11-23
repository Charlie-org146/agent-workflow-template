"""Helpers moved whole out of package.py to keep it within its size line: the private leak prefixes and the process guard (the hard bound, the stop and the child run)."""
import json
import os
import shutil
import signal
import subprocess
import threading


def private_prefixes():
    """The private leak_prefixes setting (flow file, outside the repo): case-insensitive regexes the local leak hook blocks."""
    path = os.environ.get("LOOP_FLOW") or os.path.expanduser("~/.workflow-loop/flow.json")
    try:
        with open(path, encoding="utf-8") as handle:
            return [p for p in json.load(handle).get("leak_prefixes", []) if isinstance(p, str) and p]
    except (OSError, ValueError, AttributeError):
        print("NOTE: no leak_prefixes in %s; only the built-in scans ran" % path)
        return []


try:
    CHILD_SECONDS = max(1, int(os.environ.get("PACKAGE_CHILD_SECONDS") or 30))
except ValueError:
    CHILD_SECONDS = 30
waiting = {"on": "starting", "child": None, "part": None, "lone": None, "stopping": False}
STOP_SIGNALS = [getattr(signal, n) for n in ("SIGALRM", "SIGTERM", "SIGINT", "SIGHUP") if hasattr(signal, n)]


def wait_on(what):
    waiting["on"] = what


def stop(line, code):
    """Kill the running child's group, drop a half-written ZIP, print one line and exit at once."""
    if waiting["stopping"]:  # a second signal while stopping: the first one finishes the job
        return
    waiting["stopping"] = True
    child = waiting["child"]
    if child is not None:
        kill_group(child)
    for path in (waiting["part"],):
        try:
            if path:
                os.remove(path)
        except OSError:
            pass
    if waiting["lone"]:
        shutil.rmtree(waiting["lone"], ignore_errors=True)
    if line:
        os.write(1, (line + "\n").encode("utf-8", "replace"))  # never print() in a handler: it may interrupt one
    os._exit(code)


def on_timeout(seconds):
    return lambda *_: stop("TIMEOUT: package.py stopped after %d seconds waiting on %s" % (seconds, waiting["on"]), 3)


def on_signal(signum, frame):
    stop("STOPPED: package.py got signal %d while waiting on %s" % (signum, waiting["on"]), 128 + signum)


def arm(seconds):
    """The hard bound: SIGALRM where it exists, else a timer thread (Windows). Outside kills also stop the child."""
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, on_timeout(seconds))
        signal.alarm(max(1, seconds))
    else:
        timer = threading.Timer(max(1, seconds), on_timeout(seconds))
        timer.daemon = True
        timer.start()
    for name in ("SIGTERM", "SIGINT", "SIGHUP"):
        if hasattr(signal, name) and signal.getsignal(getattr(signal, name)) is not signal.SIG_IGN:  # keep nohup's ignore
            signal.signal(getattr(signal, name), on_signal)


def kill_group(proc):
    try:
        if hasattr(os, "killpg"):
            os.killpg(proc.pid, signal.SIGKILL)
        else:  # Windows: the child and its whole tree
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
    except (OSError, ProcessLookupError, subprocess.SubprocessError):
        pass


def run_alone(cmd, cwd, what):
    """Run one child with no stdin and a time limit; kill its whole process group when the limit is hit."""
    wait_on(what)
    group = ({"start_new_session": True, "preexec_fn": lambda: signal.pthread_sigmask(signal.SIG_UNBLOCK, STOP_SIGNALS)}
             if hasattr(os, "killpg") else {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)})
    # the child must not inherit the block below, or it would ignore a reaper's TERM
    mask = hasattr(signal, "pthread_sigmask")
    if mask:  # no stop signal between the child starting and its being recorded, so none escapes the bound
        signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace", **group)  # UTF-8 whatever the locale
        waiting["child"] = proc
    finally:
        if mask:
            signal.pthread_sigmask(signal.SIG_UNBLOCK, STOP_SIGNALS)
    try:
        out, err = proc.communicate(timeout=CHILD_SECONDS)
        return proc.returncode, err
    except subprocess.TimeoutExpired:
        kill_group(proc)
        try:  # a detached grandchild may still hold the pipes: do not wait on it
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            for pipe in (proc.stdout, proc.stderr):
                pipe.close()
            proc.wait(timeout=5)
        return None, ""
    finally:
        waiting["child"] = None
