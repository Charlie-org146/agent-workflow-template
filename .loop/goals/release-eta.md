# A release gets an owner-set target time and freeze point; every goal's STATUS carries an ETA with its basis and reports a slip over 15 minutes at once; the check-in forecasts the critical path from measured merge pace (design accepted; owner o155).

- Slug: release-eta
- Touches: not declared
- ETA: 270 active minutes (estimate 216m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A release record holds the owner-set target and freeze times, shown on the board and in STATUS with minutes left; goals without a MERGE-GO at the freeze are marked next release and keep the front of its queue; failing rows are never waived
2. Every worker STATUS line carries eta, eta_basis and slip; a slip over 15 minutes sends STATUS at once with an Issues line; the forecaster uses the median and quartiles of the last 5 merge gaps (MERGE-GO and CI waits included), with tonight's gaps as a test fixture
3. No new shipped file (the code folds into an existing script with room); requirement wording goes to the owner before merge; it merges only after the v2.0 tag; net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 dev/toy/test-release-eta.py`.
   Expect: every line is PASS and the last line is ALL PASS (the pace of the night's gaps 44, 49, 22 and 20 minutes is 33, a slip over 15 minutes sends STATUS, a goal with no MERGE-GO is next release after the freeze).
2. Run `python3 skills/workflow-monitoring/scripts/layers.py status --target 2026-11-19T02:00 --freeze 2026-11-19T01:00` in a repo with a few merges, then `python3 skills/workflow-monitoring/scripts/layers.py board` with LOOP_OP_ROLE=top.
   Expect: the board prints a Release line with the target, the freeze and a forecast band (or "no measured pace yet" with fewer than 3 merge gaps).
3. Read OPS-24 on the Operation page and CHK-10 and CHK-11 on the Check-in-and-board page.
   Expect: each is Unreviewed with one revision row (owner record o183), awaiting the owner's review.

