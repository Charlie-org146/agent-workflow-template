# The land-tier row lane-start-mark-once stops being flaky (issue 5517, label flaky; TD443): it FAILED in full run 44761911403 (shard 12, main 23637447) and PASSED alone on the same main (run 44766730553), and its inputs were unchanged between the two full runs, so the cause is how it behaves under a full shard's load or ordering. FIRST diagnose from the failing job's log and the toy: name the exact failing assert and why load or ordering breaks it (a timing wait, a shared temp path, a port, a lock, a leftover file). THEN fix that cause. The row stays in the land tier and gets no retry (either would loosen it); the fix is in the toy or the code it tests, at the same strength, with a negative control

- Slug: lane-start-flake
- Touches: dev/toy, skills
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the pull request, then it names the failing assert from run 44761911403's shard 12 log and the cause under load, with evidence
2. Given the row run under one busy loop per CPU several times, then it passes every time, it is still a land-tier row, nothing retries it, and a negative control still fails it when the behaviour it guards is broken
3. Given this goal's diff, then only the files the cause needs and the goal's record files change, every script stays under 20,480 bytes, and docs.py check and criteria.py render --check pass

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `TOY_GROUP=mark bash dev/toy/test-lane-control.sh`.
   Expect: PASS for the nested-run start-mark check, PASS for the negative control (a started() that rewrites an existing mark fails it), and ALL PASS, in about 3 seconds.
2. Run `bash dev/toy/test-lane-control.sh | grep "nested run never rewrites"`.
   Expect: the same PASS line in the whole toy, which is unchanged apart from calling the check as a function.
