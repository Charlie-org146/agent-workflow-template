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

HEALTH = os.path.join(HERE, "..", "..", "workflow-health", "scripts")
DELIVERY = os.path.join(HERE, "..", "..", "workflow-delivery", "scripts")
SECRET = re.compile(r"(gh[pousr]_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{12,}|xox[abp]-[A-Za-z0-9-]{10,}|github_pat_[A-Za-z0-9_]{20,}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.|(?i:bearer\s+[A-Za-z0-9._~+/-]{16,})|-----BEGIN [A-Z ]*KEY|"
                    r"(?i:(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S{6,}))")
def outside(root, *texts, strict=True):
    """None when the texts may leave this machine, else the reason (a class, never the text). strict: only a clean private-name scan
    passes (an issue, a printed stored word); a display path (board, show) also passes when no name list exists to match."""
    for text in texts:
        if SECRET.search(text or ""):
            return "secret-shaped value (class: credential)"
    sys.path.insert(0, DELIVERY)
    try:
        got = importlib.import_module("private").scan(root, None, texts={"text-%d" % i: t for i, t in enumerate(texts)})
    except Exception as err:  # a scan that cannot run keeps the text local
        return "the private-name scan could not run (%s)" % type(err).__name__
    if got["state"] == "clean" or not strict and got["state"] in ("none", "off"):
        return None
    return "private-name scan: " + got["state"]




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


def guard_worker(verb, goals=None):
    """GRD-4: under LOOP_ROLE=worker, add, use and order are the operation's (goals is None). fail, close and reconcile reach only a record
    whose goals are exactly this worker's own goal: `goals` is the record's applies list (and the --goal target, for fail)."""
    if os.environ.get("LOOP_ROLE") != "worker":
        return
    if goals is None:
        raise Refused("SCHED-E01", "a worker may not run `%s`: it changes what the operation schedules" % verb, "run it from the operation session")
    me = own_goal()
    if not me or not goals or any(x != me for x in goals):
        raise Refused("SCHED-E02", "`%s` reaches only a record that is about this worker's own goal alone" % verb, "ask the operation session to run it")


class Lock:
    """A lock file holding its owner's token; five seconds of waiting, then a refusal with no write. A lock over a minute old whose owner is
    gone (or that holds no pid) is broken by renaming it away, which only one waiter can win; release removes only our own lock."""
    def __init__(self, paths, wait=5.0):
        self.path, self.wait, self.token = paths["lock"], wait, "%d.%s" % (os.getpid(), os.urandom(4).hex())

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        end = time.time() + self.wait
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, self.token.encode())
                os.close(fd)
                return self
            except FileExistsError:
                if self.stale():
                    old = "%s.%s.old" % (self.path, self.token)
                    try:
                        os.rename(self.path, old)
                        if os.path.getmtime(old) < time.time() - 60 or not open(old).read().strip():
                            os.unlink(old)
                            print("note: broke a stale schedule lock (its owner is gone)", file=sys.stderr)
                        else:  # we renamed a live lock another waiter had just made: put it back
                            os.link(old, self.path)
                            os.unlink(old)
                    except OSError:
                        pass
                    continue
                if time.time() > end:
                    raise Refused("SCHED-E04", "the schedule lock is held by another command", "wait and rerun; nothing was written")
                time.sleep(0.05)

    def stale(self):
        try:
            if time.time() - os.path.getmtime(self.path) <= 60:
                return False
            pid = int(open(self.path).read().strip().split(".")[0] or 0)
        except (OSError, ValueError):
            return True
        if pid <= 0:
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        except OSError:
            return False
        return False

    def __exit__(self, *exc):
        try:
            if open(self.path).read() == self.token:
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


def say(root, text):
    """Print text for a session only after outside() cleared it; otherwise print the refusal reason, never the text."""
    why = outside(root, text)
    print(text if why is None else "kept local, not shown: %s" % why)
    return why is None


def title(key, fix):
    return "Workaround %s (fix %s)" % (key, fix)


def lookup(root, key, fix):
    """The number of the one issue whose title starts with this title, 0 when none, None when the lookup failed (nothing may be created then)."""
    if outside(root, title(key, fix)):
        return None
    try:
        out = subprocess.run(["gh", "issue", "list", "--state", "all", "--limit", "200", "--search", '"%s" in:title' % title(key, fix), "--json", "number,title"],
                             capture_output=True, text=True, timeout=60)
        if out.returncode:
            return None
        hits = [i["number"] for i in json.loads(out.stdout or "[]") if str(i.get("title", "")).startswith(title(key, fix)[:90])]
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return hits[0] if hits else 0


def check_fields(rec):
    """key, fix, feature, found: one plain token each (no newline can carry a second finding line into the filer)."""
    for name in ("key", "fix", "feature", "found"):
        if not sl.NAME.match(str(rec.get(name, ""))):
            raise Refused("SCHED-E03", "%s must be one plain token (letters, digits, . _ -)" % name, "see `schedule.py --help`")
    if re.search(r"[\x00-\x1f\x7f]", rec.get("words", "")):
        raise Refused("SCHED-E03", "the words may not hold a newline or control character", "write them on one line")


def screened(root, rec):
    """The full text that would leave this machine, or a refusal; checked before anything is recorded."""
    check_fields(rec)
    text = "%s [%s %s]: %s" % (title(rec["key"], rec["fix"]), rec["feature"], rec["found"], rec["words"])
    why = outside(root, text)
    if why:
        raise Refused("SCHED-E05" if why.startswith("secret") else "SCHED-E06", "the words may not leave this machine: " + why, "reword them without names or secrets; nothing was recorded")
    return text


def file_issue(root, rec, live):
    """The issue number (0 on a preview), or raises. A preview prints what would be filed and files nothing; the filer is the existing
    finding path (milestone.py leftovers), or the command in SCHEDULE_FILER for a test. The number comes from the filer's output, else from
    a lookup by title (the real filer prints none)."""
    text = screened(root, rec)
    if not live:
        print("PREVIEW (no --live, nothing filed): would file one issue titled %r on page %s" % (title(rec["key"], rec["fix"]), rec["feature"]))
        return 0
    reply = os.path.join(sl.paths(root)["folder"], "workaround.%d.txt" % os.getpid())
    with open(reply, "w") as handle:
        handle.write("FILE backlog %s: %s\n" % (rec["feature"], text))
    cmd = os.environ.get("SCHEDULE_FILER", "").split() or [sys.executable, os.path.join(HEALTH, "milestone.py")]
    out = subprocess.run(cmd + ["leftovers", reply, "--goal", rec["fix"], "--live"], capture_output=True, text=True, timeout=120).stdout
    os.path.exists(reply) and os.unlink(reply)
    if not re.search(r"^(?:FILED|SAME)\b", out, re.M) or "FAILED" in out:
        raise Refused("SCHED-E07", "the issue was not confirmed", "run `schedule.py workaround reconcile %s`" % rec["key"], "unknown")
    found = re.search(r"^(?:FILED|SAME) .*?#(\d+)", out, re.M)
    number = int(found.group(1)) if found else lookup(root, rec["key"], rec["fix"])
    if not number:
        raise Refused("SCHED-E07", "the issue was filed but its number could not be read", "run `schedule.py workaround reconcile %s`" % rec["key"], "unknown")
    return number


def revoke(paths, goals, key, fix):
    """A waiver revoked for a goal a worker already holds: the goal keeps its slot, its run record gets the wait on the fix back and a note
    (through waits_on, which the boards already show); an absent or finished run record is left alone."""
    for slug in goals:
        path = os.path.join(paths["folder"], "runs", slug + ".json")
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("status") in ("running", "waiting"):
            data["waits_on"] = list(dict.fromkeys(list(data.get("waits_on") or []) + [fix]))
            data["schedule_revoked"] = "workaround %s revoked: wait restored (fix %s pending)" % (key, fix)
            data["schedule_revoked_fixes"] = list(dict.fromkeys(list(data.get("schedule_revoked_fixes") or []) + [fix]))
            write_atomic(path, json.dumps(data, indent=2))


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
