# gate-ci-suite-net0: plan

Carried from gate-ci-suite (TOP-DECISION 48, o205): the commits, this plan and the independent reviews of the earlier slug carry over. What changes: done line 3 is net 0 rows. The toy's proof is folded into the existing REL-3 row `rel-red-row-refused` (command `python3 dev/toy/test-release-gate.py rows && python3 dev/toy/test-gate-ci-suite.py`, seen red with a break copy, then green); the regression table stays at 1300 rows, so the cap is not touched; the pages review.py and the config edit-and-revert stale carry kept stamps.

Claims checked against the code: `skills/workflow-release/scripts/review.py` has `check_suite`, `gate_refusals`, `promote` and `gate_cli`; `release.run` shells out through `subprocess.run`, so a toy can stand gh in; `regression.yml` prints `PASS|FAIL|KNOWN|SKIPPED <row>` per row and, in its summary job, `SHARDS n of n reported. UNRUN k`; REL-3 exists on Release.md at r2 and record o191 names gate-ci-suite, Release and REL-3.

## Build steps

1. review.py: `ci_text(work, run, sha)` and a shared `ROW` regex; `check_suite(work, red, run, sha)`; `gate_refusals(..., run)` passes the checked-out commit and writes `suite_run`; `promote` and `gate_cli` thread `--suite-from`. Keep review.py at or under 19,000 LF bytes (row `release-scripts-under-19000`): tighten docstrings, share one `tsv` reader.
2. dev/toy/test-gate-ci-suite.py: a throwaway repo, gh stood in with fixture logs shaped like main's nightly 44357340394, no network.
3. REL-3 r3 through `criteria.py revise` (o191); `regression.py add` one row; `regression.py red` with a break copy; `criteria.py render`.
4. Pre-checks: docs check, entry check, wiki prepare, guard against main; restamp or edit the pages review.py stales once the owner's touches allow it.

## Tests per done line

1. A completed run on the candidate: non-PASS rows refuse exactly, a waiver clears them, the run id is in vN.json.
2. Different SHA, unfinished run, UNRUN rows, 7 of 8 shards, a missing row, no summary line, an unreadable run: each refuses "suite run does not cover the candidate", each beside a passing control.
3. The row `gate-ci-suite` is seen red (the coverage refusal broken in a copy) and green (the toy on HEAD).

## What could break

- review.py grows past 19,000 bytes: measured, 18,973.
- The CI log format changes: the toy's fixture follows the real log; the regex reads the result token after the timestamp.
- SKIPPED rows in CI are exit-77 skips: not refused, as locally; a time-cut row is caught by `UNRUN`, not by its token.

## Out of scope

Health stays local; no workflow, no script other than review.py, no other row.
