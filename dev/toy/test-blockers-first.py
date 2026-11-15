#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/graph.py skills/workflow-monitoring/scripts/checkin.py skills/workflow-monitoring/scripts/reply_hook.py
"""MON-5 (blockers first): the check-in's Needs you says what each item holds up, most-blocking first, and the Stop hook
refuses a reply whose Needs you does not."""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts"))
import checkin  # noqa: E402
import graph  # noqa: E402

fails = 0


def check(ok, text):
    global fails
    print(("PASS: " if ok else "FAIL: ") + text)
    fails += 0 if ok else 1


edges = {"a": [], "b": ["a"], "c": ["b"], "d": [], "e": ["d"]}
lines, tags = graph.rank(["d asks: go?", "a asks: go?", "pool: archive session x"], edges, {"a", "d"})
check(lines[0].startswith("a asks") and "holds up a, b, c (3 goals)" in lines[0], "the item holding up the most goals is first, with its count and names")
check("on the critical path to the next release" in lines[0], "an item holding a live goal says it is on the critical path")
check(lines[1].startswith("d asks") and "(2 goals)" in lines[1], "the next item holds up its own goal and the one behind it")
check(lines[2].endswith("[blocks nothing]") and tags == {"a": 1, "d": 2}, "an item holding nothing says blocks nothing and gets no graph mark")


def reply(items):
    return "\n".join(["1 running", "", "All sessions", "| x |", "", "Dependencies", "== r ==", "", "Needs you"] + items + ["", "Coming up", "- x"])


good = reply(["1. " + lines[0], "2. " + lines[1], "3. " + lines[2]])
check(checkin.unranked(good) == [], "a ranked Needs you passes")
check(checkin.unranked(reply(["1. a asks: go?"])) != [], "an item that does not say what it holds up is refused")
check(checkin.unranked(reply(["1. x [blocks nothing]", "2. a [holds up a (1 goal)]"])) != [], "items not sorted most-blocking first are refused")
check(checkin.unranked(reply(["Nothing needs you"])) == [], "Nothing needs you passes")
wrapped = reply(["1. a asks: go? [holds up a, b, c", "  (3 goals); on the critical path to the next release]"])
check(checkin.unranked(wrapped) == [], "an item wrapped over two lines passes")
with open(os.path.join(here, "..", "..", "skills", "workflow-monitoring", "scripts", "reply_hook.py")) as handle:
    check("checkin.unranked(text)" in handle.read(), "the Stop hook runs the ranking check on every check-in")
sys.exit(1 if fails else 0)
