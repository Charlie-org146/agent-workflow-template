"""the lane finish, status and wait"""
import os
import re
import signal
import sys
import time


def finalize(base, held, name):
    """An ended lane's result, once: the first caller claims the rc."""
    out, last = base + ".txt", base + ".last"
    with open(base + ".lock", "w") as lock:
        _s.fcntl.flock(lock, _s.fcntl.LOCK_EX)
        ended = _s.mtime(held["rc"])
        try:
            os.replace(held["rc"], held["rc"] + ".claimed")
            os.utime(held["rc"] + ".claimed")
        except FileNotFoundError:
            done = _s.read_json(last) or {}
            if done.get("attempt") == held["attempt"] and done.get("state") in _s.TERMINAL:
                return ("pass" if done["state"] == "pass" else "fail"), done.get("line", ""), done.get("ids", [])
            if _s.fresh(held):
                return "running", "RUNNING: the lane is being finished by another caller; run this same command again", []
            if not os.path.exists(held["rc"] + ".claimed"):
                _s.stop(base, held)
                return _s.death(base, out)
            os.utime(held["rc"] + ".claimed")
    rc = int((open(held["rc"] + ".claimed").read().strip() or "1"))
    num = -rc if rc < 0 else rc - 128 if 128 < rc < 160 else 0  # a signal ended it
    if num in set(signal.valid_signals()):
        _s.stop(base, held)
        return _s.death(base, out, signal.Signals(num).name)
    _s.rm_tmp(held)
    text = open(out).read() if os.path.exists(out) else ""
    began, now = _s.mtime(held["rc"] + ".started"), time.time()
    notes = open(held["rc"] + ".note").read().strip() if os.path.exists(held["rc"] + ".note") else ""
    ids = re.findall(r"^(?:FAIL|UNPROVEN) ([^\s:]+)", text, re.M)
    kind = (re.findall(r"^(REUSED|AFFECTED|FULL(?: \([^)]*\))?)", text, re.M) or ["FULL"])[0]
    ran, reused = len(re.findall(r"^(?:PASS|FAIL|KNOWN) ", text, re.M)), re.findall(r"\((\d+) reused\)", text)
    took = (ended or now) - (began or held["started"])
    line = "LANE %s %s %d/%d in %ds" % (name, kind, ran, ran + int((reused or [0])[0]), took)
    cfg = _s.read_json(os.path.join(_s.rev("--show-toplevel"), ".loop", "config.json")) or {}
    plan, wait, part = _s.lanekit.timing(held, held["rc"])
    line += _s.lanekit.budget_note(text, base, name)
    killed = re.findall(r"^KILLED (\S+): signal (\S+) \(pid (\d+)\)", text, re.M)
    if killed:
        line += "; " + ", ".join("%s killed by %s (pid %s)" % k for k in killed)
    if began and began - held["started"] >= 1:
        line += " (queued %ds)" % (began - held["started"])
    cannot = re.findall(r"^(?:NOTRUN|SKIPPED|ENV) (\S+)", text, re.M)
    if cannot and not rc:
        line += "; %d pass; %d not runnable here (%s)" % (ran + int((reused or [0])[0]), len(cannot), ", ".join(cannot[:5]))
    line += _s.lanekit.before_rows(held, plan, wait) + _s.lanekit.rows_line(text, ran, out)
    status, made = "fail", _s.generated(cfg)
    after = [p for p in _s.dirty() if p not in made]
    if rc == _s.lanekit.EXIT_STALE:
        _s.stop(base, held)
        _s.set_last(base + ".last", held["attempt"], state="ended", rc=rc, note=notes, ended=now)
        return "running", "%s\nRUNNING: the lane restarts on the new plan; run this same command again" % notes, []
    if not began and "markers" in held and rc not in (0, _s.lanekit.EXIT_PREP):
        line += "\nthe lane never reported its start (a test_record wrapper may strip _LOOP_LANE_* variables)"
    if after:
        line += "\nLANE_DIRTY at end: a row left %s. Fix: make it clean up; %s." % (", ".join(after[:10]), _s.NOTHING)
        ids = []
    elif rc == _s.lanekit.EXIT_PREP:
        line += "\n" + _s.lanekit.cut_line(name, held, plan, wait, part)
        _s.lanekit.prep_hit(base, name, held, plan, wait, part)
    elif rc == 124:
        line += "\n" + _s.lanekit.timeout_line(text, _s.deadline(held)[1], held)
    elif rc == _s.lanekit.EXIT_ENV:
        line += "\n" + _s.lanekit.env_line(notes)
    elif rc == _s.lanekit.EXIT_WAIT:
        line += "\nLANE_BUG: the lane's child stopped waiting for a slot (exit 4), which a lane never does; %s." % _s.NOTHING
    elif rc and _s.fit.off_rows(text):
        line += _s.fit.off_line(text)
    elif rc:
        line += "\nLANE_FAIL %s (log %s). Reproduce one: python3 %s run <id>; %s." % (
            ", ".join(ids) or "exit %d" % rc, out, _s.lane_argv()[1], _s.NOTHING)
    elif held.get("ids") and re.search(r"\bLEFT [1-9]", text):
        line += "\nLANE_LEFT: the lane narrowed to %s left rows unrun, so it records no pass. Fix: run this same command " \
            "again; rows that passed are reused; %s." % (held["ids"], _s.NOTHING)
    else:
        status = "pass"
        with open(base + ".ok", "w") as handle:
            handle.write(ok_text(held))
    _s.set_last(base + ".last", held["attempt"], state=status, rc=rc, line=line, ids=ids, note=notes, ended=now,
             prep_s=held.get("prep_s") or 0, plan_s=plan, wait_s=wait)
    _s.stop(base, held)
    return status, line, ids


def ok_text(held):
    """What a passing lane's .ok holds: HEAD, then the ids of a lane narrowed to them."""
    return (held["head"] + " " + (held.get("ids") or "")).strip()


def claim_ids(runs, slug):
    """The standing cover claim's local ids, sorted and comma-joined; "" with no claim."""
    import cover
    return ",".join(sorted((cover.load(runs, slug).get("claim") or {}).get("local") or []))


def ok_head(runs, slug, path):
    """A lane .ok's HEAD; a narrowed lane's .ok counts only while the cover claim lists exactly its ids."""
    try:
        head, *ids = open(path).read().split()
    except (OSError, ValueError):
        return ""
    return head if not ids or ids == [claim_ids(runs, slug)] else ""


def lane_status(runs, slug, name):
    """(state, line): running, pass, fail or none; finalizes, never spawns."""
    head = _s.rev("HEAD")
    base, held = _s.job_of(runs, slug, name)
    if held and held.get("head") == head:
        if _s.live(held):
            return "running", _s.running_line(held)
        if _s.ended(held):
            status, line, _ = finalize(base, held, name)
            return status, line
        if time.time() - held["started"] > 30 and not _s.alive(held["pid"], held.get("pstart", "")):
            _s.stop(base, held)
            return "fail", _s.lanekit.died(base + ".txt")
    for other in _s.NAMES:
        sib, job = _s.job_of(runs, slug, other)
        if other != name and job and job.get("head") == head:
            if _s.live(job):
                return "running", _s.running_line(job, other)
            if _s.ended(job):
                got = finalize(sib, job, other)
                if got[0] != "pass":
                    return got[:2]
    if not _s.dirty() and (src := _s.lanekit.passed(runs, slug, head, name)):
        return "pass", _s.answer(runs, slug, src, name)
    done = _s.read_json(base + ".last") or {}
    if done.get("head") == head and done.get("state") in _s.TERMINAL:
        return done["state"], done.get("line", "")
    return "none", "NO LANE: none ran on %s; start one with role.py lane %s %s" % (head[:12], slug, name)


def wait_for(runs, slug, name, timeout=None):
    """role.py lane-wait: block while HEAD's lane runs; exit 0 pass, 1 fail, 2 timeout, 3 none."""
    until = time.time() + timeout if timeout else None
    while True:
        state, line = lane_status(runs, slug, name)
        if state != "running":
            print(line, file=sys.stdout if state in ("pass", "none") else sys.stderr)
            return {"pass": 0, "fail": 1, "none": 3}[state]
        if until and time.time() > until:
            print("LANE_WAIT_TIMEOUT: the %s lane of %s still %s after %ds; it keeps running. Fix: run role.py lane-wait "
                  "%s %s again" % (name, slug, "waiting" if line.startswith("WAITING") else "running", timeout, slug, name),
                  file=sys.stderr)
            return 2
        time.sleep(_s.lanekit.POLL)


import lane as _s  # noqa: E402
