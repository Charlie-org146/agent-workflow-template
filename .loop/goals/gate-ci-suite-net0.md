# review.py gate and promote can take --suite-from <run-id>, reading REL-3's suite result from a GitHub Actions run of the regression workflow instead of running it locally; it accepts only a run whose head SHA equals the gate ref, that completed, and whose jobs together cover every nightly row; NOTRUN, ENV, FAIL, KNOWN and budget-LEFT rows still refuse unless a red waiver names the issue. Replaces gate-ci-suite (TOP-DECISION 48), carrying its commits (o205)

- Slug: gate-ci-suite-net0
- Touches: skills/workflow-release/scripts/review.py, dev/toy/test-gate-ci-suite.py, docs/wiki/Release.md, docs/wiki/How-to-use-Release.md, docs/wiki/Tests.md, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/How-to-use-Delivery.md, docs/wiki/Guardrails.md, docs/wiki/How-to-use-Guardrails.md, docs/wiki/Home.md, .loop/START.md
- ETA: 215 active minutes (estimate 170m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a completed full regression run on the candidate SHA, review.py gate vN --suite-from <id> refuses exactly the rows that run shows non-PASS without a waiver, and records the run id in loop/gate/vN.json.
2. A run for a different SHA, an unfinished run, or a run missing rows (a job cut by budget) refuses with 'suite run does not cover the candidate'; each is a negative control in the toy.
3. REL-3 gets one revision naming a CI run as an accepted suite source (revision tooling, o205); the toy's proof is folded into an existing REL-3 row (seen red then green), so net test rows grow by at most 0 against main's 1300 (TOP-DECISION 48); only review.py, the toy, Release.md REL-3, How-to-use-Release, generated tables and kept stamps change.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
