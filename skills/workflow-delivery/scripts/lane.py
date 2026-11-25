#!/usr/bin/env python3
"""A goal's regression lane: start, poll or wait for it, and check it before a step is recorded (role.py lane, lane-wait;
lane.py lane-exec is a lane's child). A lane tests committed HEAD, never pushes, may commit the re-rendered Tests tables;
one per goal runs at a time, one on an older HEAD is stopped first. Result: <runs>/<slug>.<name>-lane.last. Messages: lanekit.py.
"""
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.normpath(os.path.join(HERE, "..", "..", "workflow-regression", "scripts"))
sys.path.insert(0, HERE)
sys.modules.setdefault("lane", sys.modules[__name__])
import lanekit  # noqa: E402
import fit  # noqa: E402
import proctree  # noqa: E402
from proctree import alive_since as alive, rm_tmp, tmp_for  # noqa: E402,F401
fcntl = lanekit.fcntl
os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")
from lanekit import NOTHING, TERMINAL, death, dirty, drop, generated, git, mtime, prep, read_json, running_line, set_last  # noqa: E402,F401

NAMES = lanekit.LANES
GRACE = 60  # seconds a claimed rc is its finisher's


flow_spec = lanekit._flow  # the flow file as a dict


def lane_checks(top, contexts):
    import importlib.util as u
    sys.path.insert(0, REG)
    spec = u.spec_from_file_location("tests", os.path.join(REG, "tests.py"))
    tests = u.module_from_spec(spec)
    spec.loader.exec_module(tests)
    return tests.lane_checks(top, contexts)

def lane_argv(seconds=0):
    return ["python3", os.path.join(REG, "regression.py"), "run", "land", "--reuse", "--tier", "goal"] + (
        ["--budget", str(int(seconds))] if seconds else [])


def cover_ids(runs, slug):
    """LOOP_COVER_IDS, honoured only while the standing cover claim lists exactly those ids; "" runs the whole lane."""
    want, got = os.environ.get("LOOP_COVER_IDS", ""), claim_ids(runs, slug)
    return got if want and sorted(want.split(",")) == got.split(",") else ""


def lane_text():
    return shlex.join(lane_argv())


def kill(pid, start="", base="", why=""):
    if not lanekit.same(pid, start):
        return
    lanekit.audit(os.path.dirname(base) or ".", os.path.basename(base), pid, why)
    proctree.kill(pid, signal.SIGTERM)


deadline = fit.deadline


def live(held):
    return not os.path.exists(held["rc"]) and time.time() < deadline(held)[0] + 60 and alive(held["pid"], held.get("pstart", ""))


def rev(*args):
    return git("rev-parse", *args).stdout.strip()


def job_of(runs, slug, name):
    base = os.path.join(runs, "%s.%s-lane" % (slug, name))
    return base, read_json(base + ".job")


def stop(base, held):
    if held and live(held):
        kill(held["pid"], held.get("pstart", ""), base, "lane stopped: head moved, another lane, or ended")
    drop(base + ".job")
    if held:
        rm_tmp(held)
        drop(*[held["rc"] + end for end in ("", ".queued", ".started", ".note", ".claimed", ".times", ".times.tmp")])


def ended(held):
    return os.path.exists(held["rc"]) or os.path.exists(held["rc"] + ".claimed")


def fresh(held):
    """A claimed rc younger than GRACE: another caller finishes it."""
    at = mtime(held["rc"] + ".claimed")
    return bool(at) and time.time() - at < GRACE


def answer(runs, slug, src, name):
    first, nl, rest = (read_json(lanekit.lane_base(runs, slug, src) + ".last") or {}).get("line", "").partition("\n")
    return first + "; reused: the %s lane passed on this head" % src * (src != name) + nl + rest


def lane(runs, slug, name, spec, cfg, wait=90, redo=False):
    """Start or poll a lane on committed HEAD: (running|pass|fail, line, failing ids)."""
    head = rev("HEAD")
    if redo:
        jobs = [job_of(runs, slug, n) for n in NAMES]
        if any(j and live(j) for _, j in jobs):
            return "fail", "LANE_FRESH: %s has a lane running. Fix: lane-wait %s NAME, then --fresh again." % (slug, slug), []
        for b, j in jobs:
            stop(b, j)
        drop(*[b + end for b, _ in jobs for end in (".ok", ".last")])
    base, held = job_of(runs, slug, name)
    if held and held.get("head") != head:
        stop(base, held)
        held = None
    for other in NAMES:
        other_base, other_held = job_of(runs, slug, other)
        if other == name or not other_held:
            continue
        if other_held.get("head") != head:
            stop(other_base, other_held)
        elif live(other_held):
            return "running", running_line(other_held, other), []
        elif ended(other_held):
            finalize(other_base, other_held, other)
    if held and not live(held) and not ended(held) and not fresh(held) and time.time() - held["started"] > 30:
        stop(base, held)
        held = None
    if not held and not dirty() and (src := lanekit.passed(runs, slug, head, name)) and not stale(runs, slug, src):
        return "pass", answer(runs, slug, src, name), []
    if not held:
        top = rev("--show-toplevel")
        began_prep = time.time()
        line, refusal = prep(top, cfg, base + ".txt")
        if refusal:
            return "fail", refusal, []
        spent, (budget_s, override) = time.time() - began_prep, lanekit.prep_seconds(cfg)
        if spent >= budget_s:  # the Tests tables alone used the budget: no lane starts
            cut = {"budget": budget_s, "prep_s": spent, "override": override}
            lanekit.prep_hit(base, name, cut, 0, 0, "preparing the Tests tables")
            return "fail", lanekit.cut_line(name, cut, 0, 0, "preparing the Tests tables"), []
        head = rev("HEAD")
        prefix = [os.path.expanduser(part) for part in spec.get("test_record") or []]
        if prefix and not (shutil.which(prefix[0]) or os.path.isfile(prefix[0])):
            return "fail", "LANE_RECORDER: the flow file's test_record command %s isn't on this machine. Fix: install it " \
                "or remove \"test_record\" from the flow file; %s." % (prefix[0], NOTHING), []
        seconds, source = (float(spec["limit"]), "flow file limit") if spec.get("limit") else lanekit.time_limit(top)
        tests = lanekit.minutes(cfg, "test_budget_minutes") * 60
        if tests + 300 < seconds:
            seconds, source = tests + 300, "test_budget_minutes"
        tmp = tmp_for(top, slug, name)
        if not tmp:
            return "fail", "LANE_TMPDIR: %s is in a git checkout. Fix: set TMPDIR to a folder outside any repo; %s." % (tempfile.gettempdir(), NOTHING), []
        try:
            handle = os.open(base + ".job", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return "running", "RUNNING: run this same command again", []
        attempt = "%d-%d" % (os.getpid(), time.time() * 1000)
        held = {"head": head, "attempt": attempt, "started": time.time(), "limit": seconds, "source": source,
                "rc": "%s.%s.rc" % (base, attempt), "pool": lanekit.lanes_dir(), "markers": 1, "prep_s": spent,
                "prep_by": 0 if prefix else began_prep + budget_s, "budget": budget_s, "override": override,
                "ids": cover_ids(runs, slug)}
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", _LOOP_LANE_LABEL="%s/%s %s" % (os.path.basename(top), slug, name),
                   _LOOP_LANE_QUEUED=held["rc"] + ".queued", _LOOP_LANE_STARTED=held["rc"] + ".started",
                   _LOOP_LANE_NOTE=held["rc"] + ".note", _LOOP_LANE_PREP_BY=str(held["prep_by"]))
        env.pop("_LOOP_LANE_HELD", None)
        env["TMPDIR"] = held["tmp"] = tempfile.mkdtemp(prefix=os.path.basename(tmp), dir=os.path.dirname(tmp))
        argv = lane_argv(tests) + (["--ids", held["ids"]] if held["ids"] else [])
        with open(base + ".txt", "w") as log:
            if line:
                log.write(line + "\n")
            child = subprocess.Popen([sys.executable, os.path.abspath(__file__), "lane-exec", held["rc"], str(seconds),
                                      base + ".last", attempt, held["pool"], "--"] + prefix + argv, stdout=log,
                                     stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True, env=env)
        held["pid"], held["pstart"] = child.pid, lanekit.pstart(child.pid)
        os.write(handle, json.dumps(held).encode())
        os.close(handle)
        set_last(base + ".last", attempt, head=head, state="starting", started=held["started"], log=base + ".txt",
                 pool=held["pool"], rc=None, line=line or "", note="")
        if line:
            print(line)
    stop_at = time.time() + wait
    while live(held) and time.time() < stop_at:
        time.sleep(0.2)
    if live(held):
        return "running", running_line(held), []
    if not ended(held):
        stop(base, held)
        return death(base, base + ".txt")
    return finalize(base, held, name)


def lane_exec(rc, seconds, last, attempt, pool, argv):
    """A lane's child: run it, stop it past deadline() or on a signal, write .last ended, then the rc."""
    held = {"rc": rc, "limit": seconds, "started": time.time(), "pool": pool, "markers": 1,
            "prep_by": float(os.environ.get("_LOOP_LANE_PREP_BY") or 0)}
    marks = {}
    lease, port = lanekit.port_base()
    if lease is None:
        with open(rc + ".note", "a") as note:
            note.write("Note: %s; LOOP_LANE_PORT_BASE unset\n" % port)
    env = dict(os.environ)
    env.pop("LOOP_LANE_PORT_BASE", None)
    if lease is not None:
        env["LOOP_LANE_PORT_BASE"] = str(port)
    child, seen, hit = subprocess.Popen(argv, env=env), None, []
    for num in (signal.SIGTERM, getattr(signal, "SIGHUP", signal.SIGINT), signal.SIGINT):
        signal.signal(num, lambda got, _f: hit.append(got))
    try:
        while True:
            try:
                code = child.wait(timeout=1)
                break
            except subprocess.TimeoutExpired:
                pass
            state = "running" if os.path.exists(rc + ".started") else "queued" if os.path.exists(rc + ".queued") else None
            if state and state not in marks:
                marks[state] = time.time()
            if state and state != seen:
                seen = set_last(last, attempt, state=state) and state
            if hit or time.time() > deadline(held)[0]:
                cut = held["prep_by"] and not os.path.exists(rc + ".started")
                marks["cut"] = "waiting for a slot" if "queued" in marks else "planning" if cut else ""
                signal.signal(signal.SIGTERM, signal.SIG_IGN)
                proctree.kill(getattr(os, "getpgrp", lambda: child.pid)(), signal.SIGTERM)
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                code = 128 + hit[0] if hit else lanekit.EXIT_PREP if cut and not os.path.exists(rc + ".started") else 124
                break
    except Exception:
        import traceback
        print("\n".join(traceback.format_exc().splitlines()[-20:]), flush=True)
        code = 1
    set_last(last, attempt, state="ended", rc=code)
    now, queued, ran = time.time(), marks.get("queued"), marks.get("running")
    with open(rc + ".times.tmp", "w") as handle:
        json.dump({"plan": (queued or ran or now) - held["started"], "wait": (ran or now) - queued if queued else 0,
                   "cut": marks.get("cut", "")}, handle)
    os.replace(rc + ".times.tmp", rc + ".times")
    with open(rc + ".tmp", "w") as handle:
        handle.write(str(code))
    os.replace(rc + ".tmp", rc)


def main(argv):
    if argv[:1] == ["lane-exec"]:
        return lane_exec(argv[1], float(argv[2]), argv[3], argv[4], argv[5], argv[7:])
    if argv[:1] in (["lane"], ["lane-wait"]) and len(argv) >= 3 and argv[2] in NAMES:
        top = os.path.abspath(git("rev-parse", "--git-common-dir").stdout.strip())
        runs = os.path.join(top, "loop", "runs")
        if argv[0] == "lane-wait":
            timeout = float(argv[argv.index("--timeout") + 1]) if "--timeout" in argv else None
            return wait_for(runs, argv[1], argv[2], timeout)
        cfg = json.load(open(os.path.join(rev("--show-toplevel"), ".loop", "config.json")))
        status, line, _ = lane(runs, argv[1], argv[2], flow_spec(), cfg, redo="--fresh" in argv)
        print(line, file=sys.stderr if status == "fail" else sys.stdout)
        return 0 if status != "fail" else 1
    print("usage: role.py lane SLUG qa|ship|pr            start or poll a goal's regression lane\n"
          "       role.py lane-wait SLUG qa|ship|pr [--timeout S]   block until the lane for HEAD ends")
    return 0 if argv in ([], ["-h"], ["--help"]) else 2


from lane_run import claim_ids, finalize, lane_status, stale, wait_for  # noqa: E402,F401


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
