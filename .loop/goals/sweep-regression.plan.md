# Plan: sweep-regression

Files checked: `skills/workflow-regression/scripts/regression.py` (`run ROW --live`), `.loop/regression.tsv` (rows), `.loop/regression-runs.tsv` (written by runs). The only repo change is a report under `docs/`.

## Build steps
1. Wait for "Release v1.0.0" on origin/main (about 16:30); merge origin/main into the branch.
2. Probe one row with `run ROW --live`. If the issue read still returns 5xx, stop and report; do not skip rows.
3. Run the driver over the open Regression rows, one at a time unless memory allows two. Skip the five `test-settings.sh` rows. Hash ~/.workflow-loop around each row.
4. Close passing rows through regression.py's own close path; for failing rows classify by cause (real defect with file, Windows-only, needs Linux or Mac, flaky, leaks into the home folder, stale).
5. Create one tracking issue with one summary comment; move non-defect issues to "Backlog: Regression" with a one-line group comment; leave real defects open with no milestone.
6. `git restore .loop/regression-runs.tsv`; commit `docs/sweep-regression-2026-11-15.md` with the counts.

## Tests per done line
- Rerun and close: the issue shows "Passing again" with the pass line; the driver's results file lists every row.
- Grouping: the tracking issue holds one comment, every failing row in exactly one group.
- Dirty runs file: `git status` shows it clean in the main checkout.

## What could break
GitHub 5xx on the issue read (probe first, back off); a toy that writes ~/.workflow-loop (skip list plus hash check); memory below the lane floor (one row at a time).

## Out of scope
Fixing any failing row, the "health:" issues, and the GraphQL 504 itself (v1.1 backlog).

VERDICT: self: plan covers every done line
