# review.py gate and promote can take --suite-from <run-id>, reading REL-3's suite result from a GitHub Actions run of the regression workflow instead of running it locally; it accepts only a run whose head SHA equals the gate ref, that completed, and whose jobs together cover every nightly row; NOTRUN, ENV, FAIL, KNOWN and budget-LEFT rows still refuse unless a red waiver names the issue (TOP-DECISION 36, o191)

- Slug: gate-ci-suite
- Touches: skills/workflow-release/scripts/review.py, dev/toy/test-gate-ci-suite.py, docs/wiki/Release.md, docs/wiki/Tests.md, .loop/regression.tsv
- ETA: 215 active minutes (estimate 170m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a completed full regression run on the candidate SHA, review.py gate vN --suite-from <id> refuses exactly the rows that run shows non-PASS without a waiver, and records the run id in loop/gate/vN.json.
2. A run for a different SHA, an unfinished run, or a run missing rows (a job cut by budget) refuses with 'suite run does not cover the candidate'; each is a negative control in the toy.
3. REL-3 gets one revision naming a CI run as an accepted suite source (revision tooling, record o191); one new test row seen red then green; no other row changes; only review.py, one toy, Release.md's REL-3 and its generated tables change.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
