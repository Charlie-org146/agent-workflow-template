#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/operate.py skills/workflow-monitoring/scripts/graph.py
"""OPS-1 machine log (TD430): the machine STATUS counts live workers, not leftover records, and its file is never over a minute old
while an operation session runs.

live: 2 workers hold a busy pool entry and spoke a minute ago; 7 more pool entries are busy but their goals have been silent for hours,
and one goal reads running with no pool entry and no pid: the status lists 2 workers and the one-line count says 2.
heartbeat: operate.py's wait loop, on a fake clock, rewrites the status file at least every 30 seconds, so `at` is never over 60 s old.
Each has a negative control: a stale-blind build counts 9 and a loop with no heartbeat leaves the file old."""
import contextlib
import datetime
import io
import json
import os
import sys
import tempfile

# hermetic: no host session id or loop setting reaches operate.py, and HOME is a throwaway so the real ~/.workflow-loop is never read
for _k in [k for k in os.environ if k.startswith(("LOOP_", "CLAUDE"))]:
    del os.environ[_k]
os.environ["HOME"] = os.environ["USERPROFILE"] = tempfile.mkdtemp(prefix="machine-log-home-")
here = os.path.dirname(os.path.abspath(__file__))
scripts = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
import graph  # noqa: E402
import layers  # noqa: E402

fails = 0


def check(ok, text):
    global fails
    print(("PASS: " if ok else "FAIL: ") + text)
    fails += 0 if ok else 1


NOW = 1_800_000_000.0


def iso(at):
    return datetime.datetime.fromtimestamp(at, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fixture(tmp):
    common = os.path.join(tmp, ".git")
    os.makedirs(os.path.join(common, "loop", "runs"))
    pool, runs = {}, {}
    for slug, spoke in [("live1", 60), ("live2", 120)] + [("stale%d" % n, 3 * 3600) for n in range(1, 8)]:
        pool["s-" + slug] = {"state": "busy", "slug": slug, "name": "worker " + slug}
        runs[slug] = {"slug": slug, "status": "running", "step": "build", "goal": slug, "updated": iso(NOW - spoke)}
    runs["ghost"] = {"slug": "ghost", "status": "running", "step": "build", "goal": "ghost", "updated": iso(NOW - 30)}
    for slug, run in runs.items():
        json.dump(run, open(os.path.join(common, "loop", "runs", slug + ".json"), "w"))
    json.dump(pool, open(os.path.join(common, "loop", "session-pool.json"), "w"))
    return common


def live_workers(status):
    return sorted(w["slug"] for w in status["workers"] if w["status"] in ("running", "waiting"))


with tempfile.TemporaryDirectory() as tmp:
    common = fixture(tmp)
    status = layers.build(common, {}, NOW)
    check(live_workers(status) == ["live1", "live2"], "2 live worker sessions and 7 stale busy records: the status lists 2 workers (%s)" % live_workers(status))
    check(layers.one_line(status, "sent", NOW).endswith("2 workers"), "the one-line count says 2 workers, not 9 or 10")
    check(any(p["slug"] == "stale" and p["reason"].startswith("8 records") and "ghost" in p["reason"] for p in status["parked"]),
          "the stale records show once under parked, with their count (8: the 7 and the one with no pool entry) and first names, so nothing vanishes")
    wide = layers.graph.silent_limit
    layers.graph.silent_limit = lambda cfg=None: 10 ** 9  # negative control: a build that ignores how long a session was silent
    blind = layers.build(common, {}, NOW)
    layers.graph.silent_limit = wide
    check(len(live_workers(blind)) == 9, "negative control: ignoring silence counts the 7 stale busy records too (%d)" % len(live_workers(blind)))
    alone = tempfile.mkdtemp(dir=tmp)
    only = fixture(alone)
    for n in range(1, 8):
        os.remove(os.path.join(only, "loop", "runs", "stale%d.json" % n))
    check(live_workers(layers.build(only, {}, NOW)) == ["live1", "live2"], "with no stale records the same 2 workers are listed")

# heartbeat: operate.py's wait loop on a fake clock
import operate  # noqa: E402


class Clock:
    def __init__(self):
        self.now = NOW

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds
        self.after()

    def __getattr__(self, name):
        return getattr(__import__("time"), name)


def run_loop(beating):
    ages, passes, printed = [], [0], io.StringIO()
    with tempfile.TemporaryDirectory() as tmp:
        common = fixture(tmp)
        path = os.path.join(common, "loop", "status", "m.json")
        clock = Clock()

        def after():
            try:
                ages.append(clock.now - json.load(open(path))["at"])
            except (OSError, ValueError, KeyError):
                ages.append(10 ** 6)
        clock.after = after
        real = (operate.time, layers.time, operate.one_pass, operate.signature, layers.role, operate.git, operate.CFG, layers.beat, layers.machines.me)

        def one_pass(top, com, args):
            passes[0] += 1
            if passes[0] > 2:
                raise SystemExit(0)
            layers.beat(com, layers.build(com, {}, clock.now))  # a pass writes the file, as send() does
            return "120", True
        operate.time = layers.time = clock
        operate.one_pass, operate.signature, layers.role = one_pass, (lambda top, com: "same"), (lambda given="": "machine")
        operate.git = lambda *args, **kw: tmp if args[:1] == ("rev-parse",) and "--show-toplevel" in args else common
        operate.CFG = lambda top: {}
        layers.machines.me = lambda: "m"
        if not beating:
            layers.beat = lambda com, status: None if clock.now > NOW else real[7](com, status)
        try:
            with contextlib.redirect_stdout(printed):
                operate.cmd_run(type("A", (), {"role": "machine", "once": False, "poll": 5.0, "board": False})())
        except SystemExit:
            pass
        finally:
            operate.time, layers.time, operate.one_pass, operate.signature, layers.role, operate.git, operate.CFG, layers.beat, layers.machines.me = real
    return ages, printed.getvalue()


good, said = run_loop(True)
check(said == "", "the heartbeat adds no check-in output or board message: the wait loop printed nothing between passes (%r)" % said[:40])
check(good and max(good) <= 60, "with an operation session running, the status file is never over 60 s old on a fake clock (oldest %.0f s over %d polls)" % (max(good or [0]), len(good)))
bad, _ = run_loop(False)
check(bad and max(bad) > 60, "negative control: a wait loop that never rewrites the file leaves it over 60 s old (oldest %.0f s)" % max(bad or [0]))
sys.exit(1 if fails else 0)
