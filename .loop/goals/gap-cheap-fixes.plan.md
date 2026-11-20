# gap-cheap-fixes plan

Checked against the code: the five `--body` spots are merge.py `file_issue` (gh lambda over `run`), milestones.py (two `post(...)` calls) and prdcopy.py (two `post(...)` calls); `prd.out` (imported as `post`) forwards `**kw` to `subprocess.run`, so `input=` works. `lane.py` `finalize` appends the "; over N min (goal_lane_minutes)" note; health's `milestone.py` has `limits()`, `lane_rows()` and `timing_rows()`; `rules.py` `requirements_per_page` defaults to 6 while `settings.py`, `deployments.CRITERIA_MAX_DEFAULT` and the Home table say 10.

## Build steps
1. merge.py: `run(args, cwd=None, **kw)`, the gh lambda takes `**k`, the issue-create call passes `--body-file -` with `input=`; trim one comment to stay under 19,000 bytes. milestones.py and prdcopy.py: the four calls pass `"--body-file", "-"` and `input=text`.
2. lane.py: drop the goal_lane_minutes note. health milestone.py: drop `lane_rows` and the limit. Remove the setting from settings.py, survey.py, settings.md, config.json and the two commands.md lines.
3. rules.py: default 10 in both places.
4. Rows: pr-body-by-file covers the four scripts with an in-row control; lane-over-minutes and health-timing assert no lane limit but the budget; cap-default-10 also checks health's rule. Render and entry.py write.

## Test per done line
1. pr-body-by-file, seen red with the old `--body` put back (pure grep, valid on Windows). 2. lane-over-minutes (test-tiers.sh) and health-timing (test-timing.sh), seen red with the old lane.py and milestone.py. 3. cap-default-10 (test-docs-format.sh), seen red with rules.py back at 6. 4. size and row counts: scripts under 19,000 bytes, 1300 rows.

## What could break
Toy fakes that read gh argv: none asserts body text, but any fake that reads `--body-file` as a path would fail on `-` (checked: the three inline fakes log argv only). An adopted repo's config holding goal_lane_minutes now carries an unregistered key. The three toy rows are skipped on Windows, so CI and the Mac are their proof.

## Out of scope
Requirement text; other `--body` users that already use files; the README rewrite.

PENDING: seen-red proofs for lane-over-minutes, health-timing and cap-default-10 from a non-Windows runner
