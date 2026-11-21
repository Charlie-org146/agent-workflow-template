#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/layers.py skills/workflow-monitoring/scripts/operate.py skills/workflow-monitoring/scripts/graph.py
"""OPS-1 machine log (TD430): the machine STATUS counts live workers, not leftover records, and its file is never over a minute old
while an operation session runs.

live: 2 workers hold a busy pool entry and spoke a minute ago; 7 more pool entries are busy but their goals have been silent for hours,
and one goal reads running with no pool entry and no pid: the status lists 2 workers and the one-line count says 2.
heartbeat: operate.py's wait loop, on a fake clock, rewrites the status file at least every 30 seconds, so `at` is never over 60 s old.
Each has a negative control: a stale-blind build counts 9 and a loop with no heartbeat leaves the file old."""
import atexit
import contextlib
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
SENTINEL = "host-probe"
DROP_PREFIXES = ("CLAUDE", "ANTHROPIC", "LOOP_")
DROP_NAMES = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
              "GIT_CONFIG_GLOBAL", "GIT_CONFIG_COUNT", "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE", "GIT_TEMPLATE_DIR", "XDG_CONFIG_HOME", "PYTHONSTARTUP")
DROP_PREFIXES = DROP_PREFIXES + ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
REAL_HOME = os.path.realpath(os.path.expanduser("~"))  # before the throwaway HOME replaces it: cleanup() must never remove it


def scrubbed(env):
    """A copy of env without any host session, loop setting or git location variable (the names the subject scripts read are all LOOP_*, CLAUDE* or HOME-derived)."""
    return {k: v for k, v in env.items() if not k.startswith(DROP_PREFIXES) and k not in DROP_NAMES}


# hermetic: no host session id or loop setting, and a throwaway HOME, so the owner's session never reaches the wait loop's operation-session
# claim (operate.cmd_run -> cmd_claim -> board.followed reads the cwd's repo and ~/.workflow-loop) and the real .git/loop/operation.id is never written
for name in [k for k in list(os.environ) if k.startswith(DROP_PREFIXES) or k in DROP_NAMES]:
    os.environ.pop(name, None)
THROWAWAY = tempfile.mkdtemp(prefix="machine-log-home-")  # cleanup() removes only this
HOME = os.path.join(THROWAWAY, "home")
os.makedirs(HOME)
os.environ.update(HOME=HOME, USERPROFILE=HOME, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)  # every module below reads HOME at import: the swap stays above those imports


def real_id_path():
    """Path of the checkout's own .git/loop/operation.id, or None when git discovery fails (the guard then reports a FAIL, never "absent")."""
    done = subprocess.run(["git", "-C", here, "rev-parse", "--git-common-dir"], capture_output=True, text=True, env=dict(os.environ))
    out = done.stdout.strip()
    if done.returncode != 0 or not out:
        return None
    return os.path.join(os.path.abspath(os.path.join(here, out)), "loop", "operation.id")


def real_id_hash():
    """Hash of the checkout's operation id file; never its contents. "unverified:..." is a FAIL, only a missing file at a discovered path is "absent"."""
    path = real_id_path()
    if path is None:
        return "unverified:discovery"
    if not os.path.lexists(path):
        return "absent"
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return "unverified:unreadable"


def sentinel_in_real_id(path):
    """Whether the sentinel is a line of an operation id file (one id per line, the format govern_hook.operation_ids reads); only a boolean,
    False for an absent or unreadable file or no path."""
    try:
        with open(path) as handle:
            return SENTINEL in {line.strip() for line in handle}
    except (OSError, TypeError):
        return False


REAL_BEFORE = real_id_hash()


def cleanup():
    """Remove the one directory this toy created, only when it lies under the real temp directory and is neither HOME nor the cwd."""
    try:
        target = os.path.realpath(THROWAWAY)
        temp = os.path.realpath(tempfile.gettempdir())
        if target.startswith(temp + os.sep) and target not in (REAL_HOME, os.path.realpath(os.getcwd())):
            shutil.rmtree(target, ignore_errors=True)
    except OSError:
        pass


atexit.register(cleanup)

scripts = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
import graph  # noqa: E402
import layers  # noqa: E402

fails = 0
HELD = []


def check(ok, text, hold=False):
    """hold: print this PASS line only after every other check has passed, so the row that greps it cannot go green on a partial run (the row also requires exit status 0)."""
    global fails
    fails += 0 if ok else 1
    if hold:
        HELD.append((ok, text))
        return
    print(("PASS: " if ok else "FAIL: ") + text)


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
    check(live_workers(status) == ["live1", "live2"], "2 live worker sessions and 7 stale busy records: the status lists 2 workers (%s)" % live_workers(status), hold=True)
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


def run_loop(beating, host=""):
    ages, passes, printed, ids, seen, second_ids = [], [0], io.StringIO(), [], False, []
    start = os.getcwd()
    registry = os.path.join(HOME, ".workflow-loop", "repos")
    with tempfile.TemporaryDirectory() as tmp:
        common = fixture(tmp)
        subprocess.run(["git", "init", "-q", "-b", "main", "--template="], cwd=tmp, capture_output=True, env=dict(os.environ))  # a real repository: discovery from here stops at the fixture even when TMPDIR sits inside another repository
        os.chdir(tmp)  # the claim follows the cwd's repo: it must be the fixture, never the checkout this runs from
        second = os.path.join(tmp, "second")
        if host:
            os.environ["CLAUDE_SESSION_ID"] = host
            # followed-repository discovery: a disposable registry in the throwaway HOME names a second disposable repository
            os.makedirs(second)
            subprocess.run(["git", "init", "-q", "-b", "main", "--template="], cwd=second, capture_output=True, env=dict(os.environ))
            os.makedirs(os.path.dirname(registry), exist_ok=True)
            with open(registry, "w") as handle:
                handle.write(second + "\n")
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
            os.chdir(start)
            os.environ.pop("CLAUDE_SESSION_ID", None)
            try:
                ids = open(os.path.join(common, "loop", "operation.id")).read().split()
            except OSError:
                pass
            seen = sentinel_in_real_id(os.path.join(common, "loop", "operation.id"))  # before the temporary directory goes
            try:
                second_ids = open(os.path.join(second, ".git", "loop", "operation.id")).read().split()
            except OSError:
                pass
            if os.path.exists(registry):
                os.remove(registry)
            operate.time, layers.time, operate.one_pass, operate.signature, layers.role, operate.git, operate.CFG, layers.beat, layers.machines.me = real
    return ages, printed.getvalue(), ids, seen, second_ids


good, said, ids, _, _ = run_loop(True)
check(said == "", "the heartbeat adds no check-in output or board message: the wait loop printed nothing between passes (%r)" % said[:40])
check(good and max(good) <= 60, "with an operation session running, the status file is never over 60 s old on a fake clock (oldest %.0f s over %d polls)" % (max(good or [0]), len(good)), hold=True)
bad, _, _, _, _ = run_loop(False)
check(bad and max(bad) > 60, "negative control: a wait loop that never rewrites the file leaves it over 60 s old (oldest %.0f s)" % max(bad or [0]))
check(ids == [], "hermetic: no session id reaches the wait loop, so it claims nothing (%r)" % ids)
_, leaked, ids, sentinel_fixture, second_ids = run_loop(True, host=SENTINEL)
check("CLAIMED operation session host-probe" in leaked and ids == [SENTINEL],
      "negative control: a host session id left in the environment makes the wait loop claim, and the claim lands only in the fixture (%r)" % ids)
check(sentinel_fixture is True, "negative control: the sentinel check sees the sentinel in the fixture's operation id file")
check(second_ids == [SENTINEL], "followed-repository discovery: with a disposable registry in the throwaway HOME the claim lands in the second disposable repository too (%r)" % second_ids)

# one canary per scrubbed family in the parent environment: a child of the scrubbed environment prints only booleans and sees none of them
canaries = ("CLAUDE_TOY_CANARY", "ANTHROPIC_TOY_CANARY", "LOOP_TOY_CANARY", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG_GLOBAL", "GIT_TEMPLATE_DIR", "XDG_CONFIG_HOME", "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE", "GIT_CONFIG_KEY_0", "PYTHONSTARTUP")
probe = "import os; print(any(os.environ.get(k) == 'canary' for k in %r))" % (canaries,)
with_canaries = dict(os.environ, **{name: "canary" for name in canaries})
clean = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, env=scrubbed(with_canaries)).stdout.strip()
raw = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, env=with_canaries).stdout.strip()
check(clean == "False", "no canary variable of a scrubbed family reaches a child of the scrubbed environment")
check(raw == "True", "negative control: the same child without the scrub does see the canaries")

after = real_id_hash()
check(not REAL_BEFORE.startswith("unverified") and after == REAL_BEFORE,
      "hermetic: the checkout's own .git/loop/operation.id is byte-identical before and after this toy (before %s, after %s; sentinel in the real file: %s)"
      % (REAL_BEFORE[:8], after[:8], sentinel_in_real_id(real_id_path())))
check(sentinel_in_real_id(real_id_path()) is False, "hermetic: the sentinel is not a line of the checkout's own operation id file")

# cleanup: only the directory this toy made, asserted gone before the tally
throwaway_dir, home_dir = THROWAWAY, HOME
os.chdir(tempfile.gettempdir())
cleanup()
check(not os.path.lexists(home_dir) and not os.path.lexists(throwaway_dir), "cleanup: the throwaway HOME and its directory are gone")

# the two PASS lines the regression row greps print last, and only when every check passed
for ok, text in HELD:
    print(("PASS: " if ok and not fails else "FAIL: ") + text + ("" if not fails else " (held until every check passed)"))
sys.exit(1 if fails else 0)
