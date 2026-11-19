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
