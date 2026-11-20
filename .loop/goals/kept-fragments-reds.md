# Seven regression rows went red on main at v1.0.110 (run 44676371830), first seen at the release of #5380 kept-fragments: apply-rerender-howto, doc18-howto-restamp, doc19-item-missing, doc19-item-unknown, doc19-runbook-plain, home-guard-catches-leak, restamp-marks-3867. For each, decide read-only whether its test asserts the old stamp behaviour that #5380 changed on purpose (then update the test and name the requirement it proves) or #5380 broke something real (then fix the code). No test is weakened to pass (TD247)

- Slug: kept-fragments-reds
- Touches: dev/toy, .loop/regression.tsv, skills/workflow-docs/scripts
- ETA: 385 active minutes (estimate 308m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the seven rows, when it runs on this branch, then it passes (negative control: the old-behaviour input that #5380 removed still fails the updated test where the test is about that behaviour, so the test still bites)
2. Given the finding for each row, then the goal's result names for each row whether the test or the code was wrong, the requirement it proves, and the evidence read (the assertion text and the #5380 hunk); no row is added to the known list
3. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main (trim to pay), net regression rows are 0, and no requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
