# Plan: size-warn-at-cap

Built: health.py (WARN = 19000, one-line rule change), commands.md, the toys with the old 18,432 line (docs-split, estimates, health-issues, health-listing, health-report, local-schedule, plan-cache, pods) now 19,000, two row descriptions, dev/toy/test-size-warn.py and three rows seen red. Then qa, ship, pr, merge, and the issue closes (REST, kept under 300 per 10 minutes).

## Tests
18,900 and 19,000 no warning; 19,100 warns; over 20,480 fails; the old band raises nothing.

## Out of scope
goal.py and lane.py being over 19,000 (G1 trims them); the reviewed HLT-2 wording.

PENDING: none
