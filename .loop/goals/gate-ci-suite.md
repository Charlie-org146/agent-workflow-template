# review.py gate and promote can take --suite-from <run-id>, reading REL-3's suite result from a GitHub Actions run of the regression workflow instead of running it locally; it accepts only a run whose head SHA equals the gate ref, that completed, and whose jobs together cover every nightly row; NOTRUN, ENV, FAIL, KNOWN and budget-LEFT rows still refuse unless a red waiver names the issue (TOP-DECISION 36, o191)

- Slug: gate-ci-suite
- Touches: skills/workflow-release/scripts/review.py, dev/toy/test-gate-ci-suite.py, docs/wiki/Release.md, docs/wiki/Tests.md, .loop/regression.tsv, docs/wiki/How-to-use-Release.md, docs/wiki/Delivery.md, docs/wiki/How-to-use-Delivery.md
- ETA: 215 active minutes (estimate 170m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a completed full regression run on the candidate SHA, review.py gate vN --suite-from <id> refuses exactly the rows that run shows non-PASS without a waiver, and records the run id in loop/gate/vN.json.
2. A run for a different SHA, an unfinished run, or a run missing rows (a job cut by budget) refuses with 'suite run does not cover the candidate'; each is a negative control in the toy.
3. REL-3 gets one revision naming a CI run as an accepted suite source (revision tooling, record o191); one new test row seen red then green; no other row changes; only review.py, one toy, Release.md's REL-3 and its generated tables change.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `python3 dev/toy/test-gate-ci-suite.py`.
   Expect: 20 PASS lines, then `passed all` and `ALL PASS`; it also passes with `LOOP_ROLE=worker` set.
2. Run `python3 skills/workflow-release/scripts/review.py --help`, then `python3 skills/workflow-release/scripts/review.py gate v2 --suite-from`.
   Expect: the usage shows `[--suite-from RUN]` on gate and promote; the second command prints `REFUSED: --suite-from needs a run id.` and starts no suite.
3. Open docs/wiki/Release.md, find `### REL-3` under Revisions.
   Expect: row r3 above r2 with owner record o191 and the requirement naming `--suite-from RUN` and "suite run does not cover the candidate".
4. Run `python3 skills/workflow-docs/scripts/docs.py check`, `python3 skills/workflow-docs/scripts/entry.py check` and `python3 skills/workflow-docs/scripts/criteria.py guard origin/main gate-ci-suite`.
   Expect: DOCS OK: 16 pages, ENTRY OK and GUARD OK.
