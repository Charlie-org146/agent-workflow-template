#!/usr/bin/env python3
# windows: skip
# reads: skills/workflow-monitoring/scripts/pool.py skills/workflow-monitoring/scripts/mend.py skills/workflow-health/scripts/rules.py
"""pool-reconcile (TD489): `pool.py reconcile` drops the local_ pool ids the app no longer has, from {"at": ISO, "ids": [...]} (or a bare
list) that the operation session writes from list_sessions with archived sessions included, and changes nothing else; health shows the
ghost count as one row. A pool of 3 live (one archived) and 5 ghost local_ ids plus 3 ids that are not app sessions: the 5 go, the
archived one and the 3 others stay (reported as not checked), every other file is byte-identical, an empty or missing list is refused,
and health says 0 or 5."""
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
    live = ["local_s1", "local_s2", "local_s3"]
    ghosts = ["local_g1", "local_g2", "local_g3", "local_g4", "local_g5"]
    others = ["bg-1", "board-artifact-page", "f08b0780abc"]
    pool = {sid: {"name": "worker · " + sid, "state": "free"} for sid in live + others}
    pool["local_s3"]["state"] = "archive"  # archived in the app: it can still be woken, so it counts as live
    pool.update({sid: {"name": "worker · " + sid, "state": "busy", "slug": "goal-" + sid[6:]} for sid in ghosts})
    pool_path = os.path.join(loop, "session-pool.json")
    json.dump(pool, open(pool_path, "w"))
    with open(os.path.join(loop, "runs", "goal-g1.json"), "w") as handle:
        json.dump({"slug": "goal-g1", "status": "running"}, handle)
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_CODE_HOST_SESSION_ID", "LOOP_ROLE")}

    def reconcile(*argv):
        return subprocess.run([sys.executable, pool_py, "reconcile", *argv], cwd=tmp, capture_output=True, text=True, env=env, timeout=60)

    health = lambda: [r for r in rules.idle_sessions(tmp) if r["subject"] == "ghosts"]  # noqa: E731
    check(health() == [], "health prints no ghost row until the operation session has written a list")
    json.dump({"at": "2026-11-20T21:00:00Z", "ids": live + ["local_extra-not-in-pool"]}, open(os.path.join(loop, "app-sessions.json"), "w"))
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
    check(done.returncode == 0 and sorted(after) == sorted(live + others) and done.stdout.count("GHOST ") == 5 and "RECONCILED: 5 ghost ids left the pool, 6 stay, 3 not checked" in done.stdout,
          "the 5 ghosts leave the pool and the 3 live ids stay: %s" % done.stdout.strip().splitlines()[-1])
    check("local_s3" in after and after["local_s3"]["state"] == "archive", "an archived app session in the list is never dropped")
    check(all(sid in after for sid in others) and "GHOST bg-1" not in done.stdout, "ids that are not app sessions (bg-, board-artifact-page, a bare hash) are reported as not checked and never dropped")
    now = digest(tmp, {".git/loop/session-pool.json"})
    check({k: v for k, v in now.items() if not k.endswith(".lock")} == before, "nothing outside the pool file changed (no run record, no other file; its lock aside): %s" % sorted(set(now) ^ set(before)))
    shown = health()
    check(len(shown) == 1 and shown[0]["state"] == "PASS" and "0 pool ids" in shown[0]["detail"], "health then shows 0 ghosts: %s" % [r["detail"] for r in shown])
    json.dump(live, open(os.path.join(tmp, "bare.json"), "w"))
    check(reconcile("--app-list", os.path.join(tmp, "bare.json")).returncode == 0 and sorted(json.load(open(pool_path))) == sorted(live + others), "a bare list works and a second run changes nothing")
sys.exit(1 if failed else 0)
