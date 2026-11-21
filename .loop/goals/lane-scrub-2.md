# The regression lane runner starts every row with the host session variables removed (Operation TD606): CLAUDE_CODE_HOST_SESSION_ID, the other CLAUDE_CODE_* session ids, and any LOOP_* that binds a goal to a live session, removed from a real copy of the environment in Python, never by shell word splitting, so a row run inside an app session behaves as on CI and can never claim the live session or write the real .git/loop/operation.id. Refs #5700, #5671, #5683 (re-frozen as lane-scrub-2 under Operation TD613, carrying lane-scrub's commits: the scrub also covers tests.lane_checks, whose embedded copy regenerates .github/workflows/regression.yml)

- Slug: lane-scrub-2
- Touches: skills/workflow-regression, skills/workflow-delivery, dev/toy, .loop/regression.tsv, .github/workflows/regression.yml, docs/wiki
- ETA: 210 active minutes (estimate 167m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a toy that reads those host session variables, when it runs as a row under the lane runner inside an app session, then it sees none of them
2. Given a lane run, then the real .git/loop/operation.id is byte-identical before and after (compared by hash, never printed), and with the scrub reverted the toy check fails
3. Given this goal's diff, then only the lane runner (actions.py and tests.lane_checks), its toy, its row and its rendered Tests line, the regenerated embedded copy of tests.py in .github/workflows/regression.yml (no trigger, permission or secret change, said in the pull request body) and the goal's own records change, every other variable in the row environment is unchanged, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
