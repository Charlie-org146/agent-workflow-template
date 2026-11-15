# Plan: sweep-health

## Build steps
1. `health.py check` and `health.py preview` on this worktree (origin/main): save the output, count what `preview` would close, update, open and reopen per group.
2. For each group whose preview only closes and updates (size, consistency, docs, traceability, requirements, performance), run `health.py file --group G` and keep its output (CLOSED lines are the proof: health re-ran the rule and no longer finds it). Never pass `--review`, never a regression group.
3. Adoption: close each "no longer found" issue by hand with a comment quoting the line health no longer prints, except #3822 (Mac-only rule skipped on this PC) and #3821 (stays, owner-kept).
4. Re-run `health.py check` and `preview`: the swept groups must show no `WOULD close`.
5. Open one tracking issue ("health sweep, 2026-11-15"), post one summary comment grouped by cause, marking findings scripts-b (PR #4278) and scripts-c will close (size findings in docs, release, health and regression scripts; hooks count #4345).
6. Write `docs/sweep-health-2026-11-15.md` (counts, groups, the tracking issue link), add the regression row, commit, and run review, qa, ship, pr, merge.

## Tests (one per done line)
- Done line 1 and 4: row `sweep-record-counts` runs `python3 dev/toy/test-sweep-health.py`, which reads the record and checks that closed + still open add up to the issues it lists, and that each group row names a cause. Seen red by removing the record.
- Done line 2: the same toy checks the record names the tracking issue and has a scripts-b and a scripts-c column.
- Done line 3: the toy checks the branch diff holds only files under docs/ and .loop/ (no script edit), and the record says no mail and no digest.

## What could break
- `file` closes a finding whose rule was skipped here: checked in the preview first; adoption is done by hand.
- `file` opens a new issue: allowed (it lands on a Backlog milestone) and listed on the tracking issue.
- A group's counts move while the sweep runs (other goals merge): the record states the main commit it was taken at.

## Out of scope
Fixing any finding, the Regression: issues (pool-09), mail, digest, scheduled rounds, editing scripts or pages.
