#!/usr/bin/env python3
"""TSK-1: the writers of the two state files (the workaround record and the owner order), the lock, the atomic write and the checks
every outside write passes. Imported by schedule.py, not run (--help prints this). schedule_load.py is the only reader.

Nothing here files, prints or sends text outward unless it passed outside(): the secret-shaped screen and the private-name scan.
GitHub writes are previews unless the caller passes live=True (DEL-9, GRD-5)."""
import importlib
import json
import os
import re
import subprocess
import sys
import time

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")  # DEL-10
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schedule_load as sl  # noqa: E402

DELIVERY = os.path.join(HERE, "..", "..", "workflow-delivery", "scripts")
HEALTH = os.path.join(HERE, "..", "..", "workflow-health", "scripts")
SECRET = re.compile(r"(gh[pousr]_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{12,}|xox[abp]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*KEY|"
                    r"(?i:(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S{6,}))")


class Refused(Exception):
    def __init__(self, code, what, fix, effects="none"):
        super().__init__(code)
        self.code, self.what, self.fix, self.effects = code, what, fix, effects

    def line(self):
        return "REFUSED %s: %s. Fix: %s. Side effects: %s." % (self.code, self.what, self.fix, self.effects)


def own_goal():
    """The goal this worktree builds (branch loop/<slug>), or ''."""
    try:
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return branch[5:] if branch.startswith("loop/") else ""


def guard_worker(verb, record_goal=None):
    """GRD-4: under LOOP_ROLE=worker, add, use and order are the operation's. fail, close and reconcile reach only the worker's own goal's records."""
    if os.environ.get("LOOP_ROLE") != "worker":
        return
    if record_goal is None:
        raise Refused("SCHED-E01", "a worker may not run `%s`: it changes what the operation schedules" % verb, "run it from the operation session")
    if not record_goal or record_goal != own_goal():
        raise Refused("SCHED-E02", "`%s` reaches only the records of this worker's own goal" % verb, "ask the operation session to run it")


class Lock:
    """A lock file with the owner's pid; five seconds of waiting, then a refusal with no write; a lock over a minute old whose owner is gone is broken."""
    def __init__(self, paths, wait=5.0):
        self.path, self.wait = paths["lock"], wait

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        end = time.time() + self.wait
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                if self.stale():
                    try:
                        os.unlink(self.path)
                    except OSError:
                        pass
                    print("note: broke a stale schedule lock (its owner is gone)", file=sys.stderr)
                    continue
                if time.time() > end:
                    raise Refused("SCHED-E04", "the schedule lock is held by another command", "wait and rerun; nothing was written")
                time.sleep(0.05)

    def stale(self):
        try:
            old = time.time() - os.path.getmtime(self.path) > 60
            pid = int(open(self.path).read().strip() or 0)
        except (OSError, ValueError):
            return True
        if not old:
            return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except OSError:
            return False
        return False

    def __exit__(self, *exc):
        try:
            os.unlink(self.path)
        except OSError:
            pass


def write_atomic(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = "%s.%d.tmp" % (path, os.getpid())
    with open(temp, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def save_records(paths, recs):
    write_atomic(paths["workaround"], "".join(json.dumps(r, sort_keys=True) + "\n" for r in recs))


def top_of(root):
    return subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=20).stdout.strip() or root


def outside(root, *texts):
    """None when the texts may leave this machine, else the reason they may not: a secret-shaped value (class only) or a private-name hit."""
    for text in texts:
        if SECRET.search(text or ""):
            return "secret-shaped value (class: credential)"
    sys.path.insert(0, DELIVERY)
    try:
        private = importlib.import_module("private")
        got = private.scan(top_of(root), None, texts={"text-%d" % i: t for i, t in enumerate(texts)})
    except Exception as err:  # a scan that cannot run keeps the text local
        return "the private-name scan could not run (%s)" % type(err).__name__
    if got["state"] in ("hit", "broken"):
        return "private-name scan: %s" % ("a hit" if got["state"] == "hit" else "broken")
    return None


def say(root, text):
    """Print text for a session only after outside() cleared it; otherwise print the refusal reason, never the text."""
    why = outside(root, text)
    print(text if why is None else "kept local, not shown: %s" % why)
    return why is None


def title(key, fix):
    return "Workaround %s (fix %s)" % (key, fix)


def lookup(key, fix):
    """The number of the one issue with this title, 0 when none, None when the lookup failed (nothing may be created then)."""
    try:
        out = subprocess.run(["gh", "issue", "list", "--state", "all", "--limit", "200", "--search", '"%s" in:title' % title(key, fix), "--json", "number,title"],
                             capture_output=True, text=True, timeout=60)
        if out.returncode:
            return None
        hits = [i["number"] for i in json.loads(out.stdout or "[]") if i.get("title") == title(key, fix)]
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return hits[0] if hits else 0


def file_issue(root, rec, live):
    """The issue number (0 on a preview), or raises. A preview prints what would be filed and files nothing; the filer is the existing
    finding path (milestone.py leftovers), or the command in SCHEDULE_FILER for a test."""
    text = "%s: %s" % (title(rec["key"], rec["fix"]), rec["words"])
    why = outside(root, text)
    if why:
        raise Refused("SCHED-E06", "the words may not leave this machine: " + why, "reword them without names or secrets; the record stays local", "partial")
    if not live:
        print("PREVIEW (no --live, nothing filed): would file one issue titled %r on page %s" % (title(rec["key"], rec["fix"]), rec.get("feature", "?")))
        return 0
    reply = os.path.join(sl.paths(root)["folder"], "workaround.%d.txt" % os.getpid())
    with open(reply, "w") as handle:
        handle.write("FILE backlog %s: %s\n" % (rec.get("feature", ""), text))
    cmd = os.environ.get("SCHEDULE_FILER", "").split() or [sys.executable, os.path.join(HEALTH, "milestone.py")]
    out = subprocess.run(cmd + ["leftovers", reply, "--goal", rec["fix"], "--live"], capture_output=True, text=True, timeout=120).stdout
    os.path.exists(reply) and os.unlink(reply)
    found = re.search(r"^(?:FILED|SAME) .*?#(\d+)", out, re.M)
    if not found or "FAILED" in out:
        raise Refused("SCHED-E07", "the issue was not confirmed", "run `schedule.py workaround reconcile %s`" % rec["key"], "unknown")
    return int(found.group(1))


def set_order(paths, slugs, record):
    """The order file and its last-good copy, together, under the lock."""
    text = json.dumps({"record": record, "slugs": slugs}, sort_keys=True)
    with Lock(paths):
        write_atomic(paths["order"], text)
        write_atomic(paths["good"], text)


def clear_order(paths):
    """Removes both files without parsing either, so it works on a torn one."""
    with Lock(paths):
        for key in ("order", "good"):
            try:
                os.unlink(paths[key])
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    print(__doc__.strip())
