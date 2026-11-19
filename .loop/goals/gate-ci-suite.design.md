# gate-ci-suite: design

## Problem

The hard-release gate (`review.py gate` and `promote`, REL-3) runs the whole nightly suite itself, on one machine, in up to four hours (`LOOP_GATE_SECONDS`), and that machine is the operation PC, where most rows cannot run. A GitHub Actions run of the regression workflow already runs every row on Linux, sharded, and logs each result. The gate should be able to read that run instead of running the suite, without ever accepting a run that does not prove the candidate.

## Approaches

1. **Read the CI run's logs (chosen).** `--suite-from RUN` runs `gh run view RUN --json headSha,status` and `gh run view RUN --log`, parses the same `PASS|FAIL|KNOWN|NOTRUN|ENV` lines as the local route, and refuses unless the run is on the candidate, completed, fully reported and complete. Cost: about 25 lines in review.py, which sits 216 bytes under the 19,000-byte row, so docstrings are tightened and one tab reader is shared. Risk: the log format is read by regex; mitigated by a fixture shaped like the real CI log of main's nightly 44357340394.
2. **Read the run's results artifact** (`regression-results.tsv` per shard). Structured, but it needs `gh run download`, unzipping and a temp folder, which is more code than the size cap allows, and the artifact expires after 90 days. Rejected.

## Coverage, as decided

A run covers the candidate when all hold: its head SHA equals the commit of the gate ref; its status is completed; the summary job's line `SHARDS n of n reported. UNRUN 0` is present (a shard that never reported, or rows skipped for out of job time, are a cut-by-budget run; main's own nightly prints `UNRUN 98`); and every row of the candidate's `.loop/regression.tsv` with level land or nightly has a result line in the merged log of every job. Rows printed SKIPPED (exit 77) are not refused, as in the local route. FAIL, KNOWN, NOTRUN and ENV rows refuse unless a red waiver names the issue, exactly as REL-3 says today. The run id is stored in `loop/gate/vN.json` as `suite_run`.

## What each done line needs

1. `check_suite(work, red, run, sha)` takes the CI text instead of the local run; the refusal lines are the existing "row X is S with no owner waiver naming an issue"; `gate_refusals` writes `suite_run`.
2. `ci_text` returns "suite run does not cover the candidate (another commit | not completed | cut by budget | N rows are unlogged)"; one negative control per case in `dev/toy/test-gate-ci-suite.py`, with the passing control beside them.
3. REL-3 revision r3 through `criteria.py revise` (record o191); one new row `gate-ci-suite`, seen red with a break copy; Tests tables rendered. Stale pages that the review.py change causes are handled with the owner's touches decision (How-to-use-Release, Delivery, How-to-use-Delivery).

## Open questions

None for the owner. Known limit: a gate run with `--suite-from` still runs health locally.
