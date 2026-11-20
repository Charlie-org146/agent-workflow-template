# The lane-control toy's deterministic drift is fixed, so its 31 asserts that only lane-control-all covers get a green gate again (TD448, TD449; REG-4). dev/toy/test-lane-control.sh fails 'drift: check' because lanekit.py's copy of check differs from slots.py's. Make the two match, aimed at whichever is right: say which and why, with evidence (git history, callers, tests). Add a negative control that fails when the copies drift. When lane-control-all passes on main in a full run, it comes off the known list (removing a known row only makes the gate stricter; listed for the owner)

- Slug: lane-control-drift
- Touches: skills, dev/toy
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the pull request, then it says which copy of check was right and why, with evidence, and lanekit.py's and slots.py's check match
2. Given test-lane-control.sh on this branch, then it prints ALL PASS (44 asserts), lane-control-all passes, and a negative control with a drifted copy fails
3. Given this goal's diff, then only the copy that was wrong, the toy and the goal's record files change, every script stays under 20,480 bytes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `bash dev/toy/test-lane-control.sh | grep -E "exactly the same source|negative control: a lanekit"`.
   Expect: PASS for both lines (the copy matches slots.py, and a lanekit.py whose check differs is reported as drift).
2. Compare the two `check` functions in skills/workflow-delivery/scripts/lanekit.py and skills/workflow-regression/scripts/slots.py.
   Expect: they differ in nothing, including the comment on `if os.name == "nt":`.
