# checkin-view plan

Checked against the code: `checkin.py` (render, grouped, gather), `graph.py` (stamp), `reply_hook.py` (decide, main check), `docs/wiki/Monitoring.md` (MON-5, MON-14, MON-16) all exist.

Build steps
1. Monitoring text: unreview MON-5 (o44) and MON-14, MON-16, Monitoring (o45); extend the three requirements; review all four with o44.
2. `graph.stamp` records the pod's machine (pc or mac); `checkin.py` gains release_of, feature_of, goal_line and groups each repo block by release then feature; the other-pod line names its machine.
3. `reply_hook.shown` flags a missing Machine line and any Dependencies goal with no marker, time or machine; wired into the hook and `check`.
4. `dev/toy/test-checkin-view.py` and three regression rows (MON-5, MON-14, MON-16).

Tests per done line: 1 docs.py check and criteria review; 2 the test's render checks; 3 the test's four negative controls (a missing Machine line, marker, time, machine each flagged).

What could break: replies for the existing hook tests; goals created before this change have no machine and read as this machine; Home/Tests tables re-render.

Out of scope: drawing another pod's goals (MON-17 keeps one line per pod); the board layout (MON-4).

PENDING: none
