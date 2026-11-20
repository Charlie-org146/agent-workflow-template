#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-monitoring/scripts/pool.py skills/workflow-monitoring/scripts/mend.py skills/workflow-health/scripts/rules.py
"""pool-reconcile (TD489): `pool.py reconcile` drops the pool ids the app no longer has, from a list of live ids the operation
session writes, and changes nothing else; health shows the ghost count as one row. A pool of 3 live and 5 ghost ids: the 5 go, the 3 stay,
every other file is byte-identical, an empty or missing list is refused and changes nothing, and health says 0 or 5."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
pool_py = os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts", "pool.py")
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-health", "scripts"))
sys.dont_write_bytecode = True
import rules  # noqa: E402

failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


def digest(folder, skip):
    out = {}
    for base, _, names in os.walk(folder):
        for name in names:
            path = os.path.join(base, name)
            if os.path.relpath(path, folder) not in skip and ".git/objects" not in path and ".git/index" not in path:
                out[os.path.relpath(path, folder)] = hashlib.sha1(open(path, "rb").read()).hexdigest()
    return out


with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
    loop = os.path.join(tmp, ".git", "loop")
    os.makedirs(os.path.join(loop, "runs"))
    live = ["s1", "s2", "s3"]
    ghosts = ["g1", "g2", "g3", "g4", "g5"]
    pool = {sid: {"name": "worker · " + sid, "state": "free"} for sid in live}
    pool.update({sid: {"name": "worker · " + sid, "state": "busy", "slug": "goal-" + sid} for sid in ghosts})
    pool_path = os.path.join(loop, "session-pool.json")
    json.dump(pool, open(pool_path, "w"))
    with open(os.path.join(loop, "runs", "goal-g1.json"), "w") as handle:
        json.dump({"slug": "goal-g1", "status": "running"}, handle)
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_CODE_HOST_SESSION_ID", "LOOP_ROLE")}

    def reconcile(*argv):
        return subprocess.run([sys.executable, pool_py, "reconcile", *argv], cwd=tmp, capture_output=True, text=True, env=env, timeout=60)

    health = lambda: [r for r in rules.idle_sessions(tmp) if r["subject"] == "ghosts"]  # noqa: E731
    check(health() == [], "health prints no ghost row until the operation session has written a list")
    json.dump(live + ["extra-live-not-in-pool"], open(os.path.join(loop, "app-sessions.json"), "w"))
    shown = health()
    check(len(shown) == 1 and shown[0]["state"] == "WARN" and "5 pool ids" in shown[0]["detail"], "health shows 5 ghosts as one row: %s" % [r["detail"] for r in shown])
    before = digest(tmp, {".git/loop/session-pool.json"})
    refused = reconcile("--app-list", os.path.join(tmp, "nowhere.json"))
    check(refused.returncode != 0 and "REFUSED" in refused.stderr + refused.stdout and json.load(open(pool_path)) == pool, "a missing list is refused and the pool is unchanged")
    json.dump([], open(os.path.join(tmp, "empty.json"), "w"))
    before = digest(tmp, {".git/loop/session-pool.json"})
    refused = reconcile("--app-list", os.path.join(tmp, "empty.json"))
    check(refused.returncode != 0 and json.load(open(pool_path)) == pool, "an empty list is refused: it would wipe the pool")
    done = reconcile()
    after = json.load(open(pool_path))
    check(done.returncode == 0 and sorted(after) == live and done.stdout.count("GHOST ") == 5 and "RECONCILED: 5 ghost ids left the pool, 3 stay" in done.stdout,
          "the 5 ghosts leave the pool and the 3 live ids stay: %s" % done.stdout.strip().splitlines()[-1])
    now = digest(tmp, {".git/loop/session-pool.json"})
    check({k: v for k, v in now.items() if not k.endswith(".lock")} == before, "nothing outside the pool file changed (no run record, no other file; its lock aside): %s" % sorted(set(now) ^ set(before)))
    shown = health()
    check(len(shown) == 1 and shown[0]["state"] == "PASS" and "0 pool ids" in shown[0]["detail"], "health then shows 0 ghosts: %s" % [r["detail"] for r in shown])
    check(reconcile().returncode == 0 and sorted(json.load(open(pool_path))) == live, "a second run changes nothing")
sys.exit(1 if failed else 0)
