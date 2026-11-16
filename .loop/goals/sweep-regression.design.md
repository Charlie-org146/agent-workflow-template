# Design: sweep-regression

## Problem
About 113 open "Regression: <row>" issues have never been rerun on current main. `regression.py run ROW --live` reruns one row and opens, comments on or closes its issue. The sweep runs each row once, closes the passing ones with the pass line, and groups the rest by cause in one new tracking issue. It fixes nothing.

## Approaches
1. Driver script over `run ROW --live`, two rows at a time, results into a tsv. Cost: a small script kept in the scratchpad, no repo change. Risk: `--live` skips every row when GitHub's issue-list GraphQL query returns 5xx (seen 2026-11-15, filed as a v1.1 item).
2. Run without `--live`, then close issues by hand with `gh`. Cost: bypasses regression.py's bookkeeping, which done line 1 forbids.

## Chosen
Approach 1. Before the full run, probe one row to check the issue read works; if it still 504s, stop and report instead of skipping rows. Back off on 5xx. Skip the five test-settings.sh rows (they write the real ~/.workflow-loop on Windows) and hash ~/.workflow-loop around each row to list other leaking toys. Restore `.loop/regression-runs.tsv` afterwards. The only repo change is a dated report under `docs/` holding the counts and the groups.

## Done line needs
- Rerun and close: the driver plus regression.py's own close path.
- Grouping: real defect (file named), Windows-only, needs Linux or Mac (off-machine to-do), flaky, leaks into the home folder; one summary comment on a new tracking issue.
- Dirty runs file: `git restore`.
- Counts: closed, failing by group, skipped; "health:" issues left alone.

## Open questions
None for the owner. The run waits for v1.0.0 on origin/main (about 16:30).
