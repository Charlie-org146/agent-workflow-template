#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-delivery/scripts/guards.py skills/workflow-delivery/scripts/lane.py skills/workflow-regression/scripts/lanes_cli.py
"""lane-memory (#4385): a lane that waits for memory and gives up is the machine's fault, so it costs no counted try.

Done 1: guards.failed_try treats a MEMORY_WAIT or LANE_ENV lane line as not counted (its own cap of 10), and
        a real failure, a LANE_FAIL, and words that merely mention MEMORY_WAIT still cost a try."""
import contextlib
import io
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(root, "skills", "workflow-delivery", "scripts"))
sys.dont_write_bytecode = True
import guards  # noqa: E402
import lanekit  # noqa: E402

failed = []
NL = chr(10)


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        failed.append(text)


class Goal:
    MAX_TRIES = 3
    saved = []

    def save(self, state, note):
        self.saved.append(note)

    def config(self):
        return {}


def charged(why, state=None):
    """(tries, env waits) after a failed try with this reason."""
    state = state if state is not None else {"slug": "g", "tries": 0}
    with contextlib.redirect_stdout(io.StringIO()):
        guards.failed_try(Goal(), state, why, "build", "again")
    return state.get("tries", 0), state.get("env", 0)


LINE = "regression lane failed: MEMORY_WAIT: waited 600s for memory (3.0 GB free, min_free_memory_gb 3.5); nothing ran, no try used."
check(charged(LINE) == (0, 1), "a lane that gave up waiting for memory costs no try")
check(charged("qa failed: regression lane: LANE_ENV: 300 of 330 rows could not start") == (0, 1), "a lane made mostly of ENV rows costs no try (qa too)")
check(charged("regression lane failed: LANE_FAIL a, b (log x)") == (1, 0), "negative control: a lane with failing rows still costs a try")
check(charged("qa failed: the tests are red; see lane x: MEMORY_WAIT: not really") == (1, 0), "negative control: words that only mention MEMORY_WAIT cost a try")
state = {"slug": "g", "tries": 0, "env": 10}
check(charged(LINE, state) == (1, 10), "the eleventh wait counts, so a machine that never frees memory still stops the goal")
note = "MEMORY_WAIT: waited 600s for memory (3.0 GB free, min_free_memory_gb 3.5); nothing ran, no try used. Fix: run the same command again when memory frees"
for what, text in (("a memory wait", lanekit.env_line(note)), ("a mostly-ENV lane", lanekit.env_line(""))):
    line = "LANE pr AFFECTED 0/0 in 600s" + NL + text
    check(charged("regression lane failed: " + line.splitlines()[-1][:200]) == (0, 1), "the lane line of %s, as pr_fail turns it into the try reason, is not counted" % what)
check(lanekit.EXIT_ENV == 6 and lanekit.env_line(note) == note, "the lane reports the MEMORY_WAIT note as it was written")
sys.exit(1 if failed else 0)
