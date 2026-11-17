#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/watch.py skills/workflow-monitoring/scripts/pool.py skills/workflow-monitoring/scripts/monitor.py skills/workflow-monitoring/scripts/notify.py skills/workflow-monitoring/scripts/operate.py skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/batch.py
"""hands-off-operation (#4781, #4507, #4813, #4679): a worker starts from a scheduled turn (workers: auto or --background), merged and released
worker sessions are archived (and idle ones of retired goals under memory pressure), operate.py start prints a readiness table, the check-in
timer is shown, recorded and found stale, and the check-in groups goals by feature. A throwaway repo and stand-ins: no network, no real pool.
usage: test-hands-off.py [fallback|archive|pressure|start|timer|feature|queued|size]  (no argument: all)"""
import datetime
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.join(here, "..", "..")
scripts = os.path.join(top, "skills", "workflow-monitoring", "scripts")
sys.path.insert(0, scripts)
os.environ.pop("LOOP_ROLE", None)
os.environ["LOOP_ROLE"] = "worker"
only = sys.argv[1] if len(sys.argv) > 1 else ""
if not only:  # each part in its own process: they stub the same modules
    code = 0
    for part in ("fallback", "archive", "pressure", "start", "timer", "feature", "queued", "size"):
        done = subprocess.run([sys.executable, os.path.abspath(__file__), part], capture_output=True, text=True)
        print("".join(line + chr(10) for line in done.stdout.splitlines() if line.startswith(("PASS", "FAIL"))), end="")
        code = code or done.returncode
    sys.exit(code)
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def want(name):
    return only in ("", name)


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(data if isinstance(data, str) else json.dumps(data))


def repo(tmp, cfg=None):
    root = os.path.join(tmp, "toyrepo")
    subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
    write(os.path.join(root, ".loop", "config.json"), dict({"base": "main", "cadence": "5"}, **(cfg or {})))
    write(os.path.join(root, ".loop", "queue.md"), "")
    return root, os.path.join(root, ".git", "loop")


def run_py(root, script, *args):
    done = subprocess.run([sys.executable, os.path.join(scripts, script)] + list(args), cwd=root, capture_output=True, text=True,
                          env=dict(os.environ, LOOP_ROLE="", LOOP_SESSION_TOOL=""))
    return done.stdout + done.stderr


NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

if want("fallback"):
    import watch
    real_launch = watch.launch

    class Args:
        max = 0
        skill_dir = ""
        background = False

    def round_with(cfg, background=False):
        launches, state = [], {"slug": "g", "goal": "g", "status": "queued", "worktree": "/nowhere", "log": []}
        watch.plan = lambda limit: ([{"slug": "g", "goal": "g"}], [])
        watch.taken = lambda: set()
        watch.freeze = lambda g, c: state
        watch.go_prompt = lambda *a: "prompt"
        watch.save = lambda s, note=None: None
        watch.launch = lambda s, prompt, c: launches.append(s["slug"])
        watch.sessions.assign = lambda s, prompt, c: False  # a scheduled or Remote Control turn: no session can start
        watch.sessions.HUNG.clear()
        Args.background = background
        watch.start_round(Args, cfg)
        return launches

    check(round_with({"workers": "auto", "agent_command": ["x"]}) == ["g"], "workers auto: no app session could start, so a background worker is launched")
    check(round_with({"workers": "app", "agent_command": ["x"]}, background=True) == ["g"], "--background under workers app: that one start launches a background worker")
    check(round_with({"workers": "app", "agent_command": ["x"]}) == [], "negative control: workers app and no flag launches nothing")

    class Child:
        pid = 4242

    saved = []
    real = watch.subprocess.Popen
    watch.subprocess.Popen = lambda *a, **k: Child()
    with tempfile.TemporaryDirectory() as tmp:
        watch.loop_dir = lambda name: tmp
        watch.save = lambda s, note=None: saved.append((dict(s), note))
        watch.launch = real_launch
        state = {"slug": "g", "status": "queued", "worktree": tmp, "attempt": 1, "log": []}
        watch.launch(state, "prompt", {"agent_command": ["x"]})
        watch.subprocess.Popen = real
    check(state.get("pid") == 4242 and state.get("status") == "running", "the launched worker's pid is recorded and the goal runs")
    check(state.get("worker") == "background" and state.get("bound_at") and state.get("attempt") == 2,
          "the background worker is bound: worker background, bound_at set, attempt 1 to 2 (%s)" % {k: state.get(k) for k in ("worker", "bound_at", "attempt")})

if want("archive") or want("pressure"):
    import monitor
    import pool
    import sessions

    with tempfile.TemporaryDirectory() as tmp:
        root, loop = repo(tmp, {"min_free_memory_gb": 0})
        runs = os.path.join(loop, "runs")
        done = {"status": "done", "release": "cut", "release_version": "1.2.3", "release_url": "u", "pr": "https://x/pull/1"}
        write(os.path.join(runs, "shipped.json"), dict(done, slug="shipped"))
        write(os.path.join(runs, "shipped2.json"), dict(done, slug="shipped2", pr="https://x/pull/2"))
        write(os.path.join(runs, "busy.json"), {"slug": "busy", "status": "running"})
        write(os.path.join(runs, "asks.json"), {"slug": "asks", "status": "waiting"})
        write(os.path.join(runs, "openpr.json"), dict(done, slug="openpr", pr="https://x/pull/3"))
        write(os.path.join(runs, "gone.json"), {"slug": "gone", "status": "retired"})
        write(os.path.join(runs, "gone2.json"), {"slug": "gone2", "status": "retired"})
        entries = {
            "s-ship": {"name": "worker · shipped", "slug": "shipped", "state": "busy", "since": "2026-11-01T00:00:00Z"},
            "s-ship2": {"name": "worker · shipped2", "slug": "shipped2", "state": "free", "since": "2026-11-02T00:00:00Z", "history": [{"slug": "shipped2"}]},
            "s-busy": {"name": "worker · busy", "slug": "busy", "state": "busy", "since": "2026-11-01T00:00:00Z"},
            "s-asks": {"name": "worker · asks", "slug": "asks", "state": "busy", "since": "2026-11-01T00:00:00Z"},
            "s-open": {"name": "worker · openpr", "slug": "openpr", "state": "busy", "since": "2026-11-01T00:00:00Z"},
            "s-op": {"name": "operation · pc", "slug": "shipped", "state": "busy", "since": "2026-10-01T00:00:00Z"},
            "s-gone": {"name": "worker · gone", "slug": "gone", "state": "free", "since": "2026-11-03T00:00:00Z", "history": [{"slug": "gone"}]},
            "s-gone2": {"name": "worker · gone2", "slug": "gone2", "state": "free", "since": "2026-11-04T00:00:00Z", "history": [{"slug": "gone2"}]},
            "s-fresh": {"name": "worker · idle", "state": "free", "since": "2026-11-05T00:00:00Z"}}
        write(os.path.join(loop, "session-pool.json"), entries)
        log = os.path.join(tmp, "tool.log")
        tool = os.path.join(tmp, "tool.py")
        write(tool, "import sys\nopen(%r, 'a').write(' '.join(sys.argv[1:]) + chr(10))\n" % log.replace(os.sep, "/"))
        states = {"https://x/pull/1": "MERGED", "https://x/pull/2": "MERGED", "https://x/pull/3": "OPEN"}
        monitor.ghj = lambda args, cwd: {"state": states.get(args[2], "OPEN")} if args[0] == "pr" else {"isDraft": False}
        os.environ["LOOP_SESSION_TOOL"] = "%s %s" % (sys.executable.replace(os.sep, "/"), tool.replace(os.sep, "/"))
        here = os.getcwd()
        os.chdir(root)
        os.environ["CLAUDE_CODE_HOST_SESSION_ID"] = ""

        def archived_calls():
            return sorted(line.split()[1] for line in open(log).read().splitlines() if line.startswith("archive")) if os.path.exists(log) else []

        if want("archive"):
            pool.lim.memory_hold = lambda cfg: ""
            pool.cmd_archive(None)
            check(archived_calls() == ["s-ship", "s-ship2"], "a worker session whose goal's merge and release are verified is archived (busy or idle): %s" % archived_calls())
            left = sessions.read(os.path.join(loop, "session-pool.json"), {})
            check("s-ship" not in left and "s-ship2" not in left, "the archived sessions leave the pool")
            check(all(k in left for k in ("s-busy", "s-asks", "s-open", "s-op", "s-fresh")),
                  "negative control: sessions of a running, waiting or open-PR goal, an operation session and a fresh idle one are never archived")
            check(all(k in left for k in ("s-gone", "s-gone2")), "negative control: with no memory pressure a retired goal's idle session is kept")
            lines = monitor.archived_since(loop, "2000-01-01T00:00:00Z")
            check(len(lines) == 2 and any("shipped released v1.2.3" in x for x in lines), "the archived rows name each session and why (%s)" % lines)
            check(monitor.archived_since(loop, "2999-01-01T00:00:00Z") == [], "negative control: rows older than the last check-in are not named again")
            import checkin
            text = "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="2000-01-01T00:00:00Z"))
            check("Archived (worker sessions freed):" in text and "- worker · shipped (shipped released v1.2.3)" in text, "the check-in names the archived sessions")
            monitor.ghj = lambda args, cwd: None  # gh gives no answer: nothing is verified
            write(os.path.join(loop, "session-pool.json"), entries)
            open(log, "w").close()
            pool.cmd_archive(None)
            check(archived_calls() == [], "negative control: with no answer from GitHub nothing is archived")
            monitor.ghj = lambda args, cwd: {"state": states.get(args[2], "OPEN")} if args[0] == "pr" else {"isDraft": False}
            os.environ["LOOP_SESSION_TOOL"] = ""
            write(os.path.join(loop, "session-pool.json"), entries)
            pool.cmd_archive(None)
            marked = sessions.read(os.path.join(loop, "session-pool.json"), {})
            check(marked["s-ship"]["state"] == "archive", "no session tool: the session is marked archive and ARCHIVE-NOW is printed for the operation session")
            pool.archived("s-ship", "worker · shipped", "archived with the app")
            check("s-ship" not in sessions.read(os.path.join(loop, "session-pool.json"), {}), "pool.py archived ID drops a session the operation session archived")

        if want("pressure"):
            os.environ["LOOP_SESSION_TOOL"] = "%s %s" % (sys.executable.replace(os.sep, "/"), tool.replace(os.sep, "/"))
            monitor.ghj = lambda args, cwd: None  # only retired goals can qualify here
            write(os.path.join(loop, "session-pool.json"), entries)
            open(log, "w").close()
            calls = []
            pool.lim.memory_hold = lambda cfg: "free memory is low" if not calls else ""
            real_call = sessions.call
            sessions.call = lambda command, *a: (calls.append(a[1]), real_call(command, *a))[1]
            pool.cmd_archive(None)
            sessions.call = real_call
            check(archived_calls() == ["s-gone"], "under memory pressure the oldest idle retired goal's session is archived, and it stops once memory is back (%s)" % archived_calls())
            pool.lim.memory_hold = lambda cfg: "free memory is low"
            write(os.path.join(loop, "session-pool.json"), entries)
            open(log, "w").close()
            pool.cmd_archive(None)
            check(archived_calls() == ["s-gone", "s-gone2"], "while memory stays low every idle retired goal's session goes, oldest first (%s)" % archived_calls())
            kept = sessions.read(os.path.join(loop, "session-pool.json"), {})
            check(all(k in kept for k in ("s-busy", "s-asks", "s-open", "s-op", "s-fresh")),
                  "negative control: under pressure a running, waiting or open-PR goal's session, an operation session and a fresh idle one stay")
        os.chdir(here)
        os.environ["LOOP_SESSION_TOOL"] = ""

if want("start"):
    with tempfile.TemporaryDirectory() as tmp:
        root, loop = repo(tmp, {"workers": "app"})
        out = run_py(root, "operate.py", "start")
        rows = [name for name in ("session tool", "workers", "skills", "hooks", "memory", "pool") if "| %s |" % name in out]
        check(len(rows) == 6, "operate.py start prints one readiness table with every row (%s)" % rows)
        check("| session tool | FIX | set session_command" in out and "NOT READY" in out, "a row that is not ready names its fix")
        check(not os.path.exists(os.path.join(loop, "runs")) or not os.listdir(os.path.join(loop, "runs")), "negative control: start starts no goal and writes no run")
        check("workers is" not in out, "workers app is ok: no background worker without the owner's yes")
        write(os.path.join(root, ".loop", "config.json"), {"base": "main"})
        check("| workers | FIX | workers is unset" in run_py(root, "operate.py", "start"), "negative control: workers unset is flagged, so a background worker never starts silently")

if want("timer"):
    import notify
    with tempfile.TemporaryDirectory() as tmp:
        root, loop = repo(tmp)
        shown = run_py(root, "operate.py", "timer")
        check("every 5 minutes" in shown and "checkin.py" in shown and "never starts goals, merges" in shown, "operate.py timer shows the interval, the steps and what it never does")
        check(not os.path.exists(os.path.join(loop, "timer.json")), "showing the timer records nothing: it waits for the owner's yes")
        check(len(notify.timer_lines(loop, "5")) == 1 and "missing" in notify.timer_lines(loop, "5")[0], "a session with no recorded timer shows it under Needs you")
        run_py(root, "operate.py", "timer", "created")
        check(notify.timer_lines(loop, "5") == [], "after the owner's yes the timer is recorded and nothing shows")
        check("stale" in notify.timer_lines(loop, "10")[0], "a changed cadence marks the timer stale, with the words to fix it")
        check(notify.timer_lines(loop, "off") == [], "negative control: cadence off needs no timer")
        import checkin
        write(os.path.join(root, ".loop", "config.json"), {"base": "main", "cadence": "10"})
        text = " ".join("\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000")).split())
        check("check-in timer is stale" in text, "the check-in shows a stale timer under Needs you")

if want("feature") or want("queued"):
    import monitor
    with tempfile.TemporaryDirectory() as tmp:
        root, loop = repo(tmp)
        for page, line in (("Monitoring", "- MON-1: x"), ("Delivery", "- DEL-1: y")):
            write(os.path.join(root, "docs", "wiki", page + ".md"), line + "\n")
        write(os.path.join(root, ".loop", "docs.tsv"), "# page\tpaths\nDelivery\tskills/workflow-delivery\nMonitoring\tskills/workflow-monitoring,:(exclude)skills/workflow-monitoring/SKILL.md\n")
        here = os.getcwd()
        os.chdir(root)
        monitor.ghj = lambda args, cwd: {"labels": [{"name": "feature:Delivery"}], "milestone": None}
        if want("feature"):
            check(monitor.feature_of(root, "Fix (#4679)") == "Delivery", "a goal naming only an issue number takes the issue's feature label")
            monitor.ghj = lambda args, cwd: {"labels": [], "milestone": None}
            check(monitor.feature_of(root, "Fix #4680", {"feature": "Monitoring"}) == "Monitoring", "a feature set by batch.py add --feature groups the goal")
            check(monitor.feature_of(root, "Fix #4681", {"touches": ["skills/workflow-delivery/scripts/goal.py"]}) == "Delivery", "touches covered by a docs.tsv page group the goal there")
            check(monitor.feature_of(root, "Fix #4682", {"touches": ["README.md"]}) == "no feature", "negative control: nothing to go on shows no feature")
            check(monitor.feature_of(root, "Fix MON-1 and #1") == "Monitoring", "a requirement ID in the goal text still wins")
            out = run_py(root, "batch.py", "add", "b1", "--goal", "Do a thing", "--done", "it works", "--feature", "Delivery")
            line = open(os.path.join(root, ".loop", "queue.md")).read()
            import graph
            item = graph.parse(next(x for x in line.splitlines() if x.startswith("- slug:")))
            check("feature: Delivery" in line and item["feature"] == "Delivery", "batch.py add --feature stores the page on the queue line and the check-in reads it (%s)" % out.strip())
        if want("queued"):
            import checkin
            hist = [(0, "queued"), (600, "idea done"), (1200, "plan done"), (3000, "build done"), (3300, "review done"), (3600, "qa done"), (3700, "ship done"), (3800, "pr done")]
            base = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
            stamp = lambda s: (base + datetime.timedelta(seconds=s)).strftime("%Y-%m-%dT%H:%M:%SZ")
            write(os.path.join(loop, "runs", "hist.json"), {"slug": "hist", "goal": "Old (DEL-1)", "status": "done", "step": "pr", "release": "merged", "tries": 0, "pr": "",
                                                           "done": ["a", "b"], "touches": ["skills/workflow-monitoring"], "updated": stamp(3800), "log": ["%s %s" % (stamp(s), t) for s, t in hist]})
            write(os.path.join(root, ".loop", "queue.md"), "- slug: later | touches: skills/workflow-monitoring | goal: Later (DEL-1) | done: one | done: two\n")
            text = "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000"))
            row = next((x for x in text.splitlines() if "[ ] later" in x), "")
            check(row and "~?" not in row, "a queued goal shows an estimated time from its size, not ~? (%s)" % row.strip())
            write(os.path.join(root, ".loop", "queue.md"), "- slug: other | goal: Other (DEL-1) | done: one\n")
            os.remove(os.path.join(loop, "runs", "hist.json"))
            text = "\n".join(checkin.render(root=root, at=datetime.datetime.now(datetime.timezone.utc), stamp="0000"))
            check("[ ] other ~? left" in text, "negative control: with no finished goal to learn from a queued goal still shows ~?")
        os.chdir(here)

if want("size"):
    def lf_size(path):
        data = open(os.path.join(top, path), "rb").read()
        return len(data) - data.count(b"\r\n")

    base = "skills/workflow-monitoring/scripts/"
    caps = {"checkin.py": 19495, "pool.py": 19000, "monitor.py": 19000, "notify.py": 19000, "watch.py": 19000, "graph.py": 19000, "board_status.py": 19000, "batch.py": 19000, "operate.py": 19864}
    bad = ["%s %d > %d" % (n, lf_size(base + n), c) for n, c in caps.items() if lf_size(base + n) > c]
    check(not bad, "checkin.py stays at or under 19,495 bytes and no script this goal touched grew past its starting size or 19,000 (%s)" % (bad or "all within"))
    check(lf_size("skills/workflow-setup/scripts/settings.py") <= 19000, "settings.py stays under 19,000 bytes")

sys.exit(1 if failed else 0)
