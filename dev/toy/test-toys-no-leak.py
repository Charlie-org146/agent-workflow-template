#!/usr/bin/env python3
# windows: ok
# reads: dev/toy/reap.sh dev/toy/homeguard.py skills/workflow-delivery/scripts/lanekit.py
"""REG-1, issue 4555: no toy changes the real ~/.workflow-loop. The CI runner's four LEAK rows (worker-runs-release, pr-body-no-checks,
defect-owed, suite-time-recorded) each ran lane code under the runner's real HOME and added lanes/port-0 or lanes/counter.lock there.
The harness (reap.sh) now points LOOP_LANES_DIR at a temp lane pool unless a toy names its own, so lane code in any toy leaves a
fresh home untouched. The proof is a fresh home judged in full (TOY_GUARD_STRICT, so lanes/ and schedule/ count too), the home a
CI runner has on its first toy:

1. A toy that takes a lane port lease (lanekit's pool, as port_base does) leaves a fresh ~/.workflow-loop empty.
2. Control: the same toy aimed at that folder's lanes/ on purpose is caught as a LEAK, so the check can fail."""
import os
import subprocess
import sys
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
failed = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


LEASE = '''python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.join(os.environ["ROOT"], "skills", "workflow-delivery", "scripts"))
import lanekit
pool = lanekit.lanes_dir()
lanekit.check(pool)
os.close(lanekit._open(os.path.join(pool, "port-0")))
os.close(lanekit._open(os.path.join(pool, "counter.lock")))
PY
'''


def files(top):
    return [os.path.join(h, n) for h, _d, ns in os.walk(top) for n in ns] if os.path.isdir(top) else []


with tempfile.TemporaryDirectory() as tmp:
    def toy(name, home, extra):
        os.makedirs(home, exist_ok=True)
        path = os.path.join(tmp, name)
        with open(path, "w", newline="\n") as handle:
            handle.write('#!/bin/bash\n# windows: ok\nhere="%s"\n. "$here/dev/toy/reap.sh"\n%s' % (root.replace("\\", "/"), LEASE))
        env = dict(os.environ, HOME=home, USERPROFILE=home, ROOT=root, TOY_REAL_WL=os.path.join(home, ".workflow-loop"), TOY_GUARD_STRICT="1")
        env.pop("LOOP_LANES_DIR", None)
        env.update(extra)
        done = subprocess.run(["bash", path], capture_output=True, text=True, env=env)
        return done.returncode, done.stderr + done.stdout

    fresh = os.path.join(tmp, "fresh")
    code, said = toy("lease.sh", fresh, {})
    check(code == 0 and "LEAK" not in said and not files(os.path.join(fresh, ".workflow-loop")),
          "a toy that takes a lane lease leaves a fresh ~/.workflow-loop empty (exit %d: %s)" % (code, said.strip()[:160]))
    aimed = os.path.join(tmp, "aimed")
    code, said = toy("aimed.sh", aimed, {"LOOP_LANES_DIR": os.path.join(aimed, ".workflow-loop", "lanes")})
    check(code != 0 and "LEAK" in said and "lanes/port-0" in said, "control: a toy aimed at the real lanes/ is caught (exit %d: %s)" % (code, said.strip()[:160]))

sys.exit(1 if failed else 0)
