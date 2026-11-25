<!-- workflow-docs -->
# Fast checks

Review: **Unreviewed**

How to use: [How-to-use-Fast-checks](How-to-use-Fast-checks)

## Problem

- Status: written, not built. Built by goal v110-skp-1. Reviewed approves the wording; availability is shown separately.
- My fast-cut ran 3 local test runs and 2 wiki regenerations before its PR, and the PR's full GitHub run then covered every test anyway.
- Checks have no time limit, so one slow check holds every later step.

## Requirements

### Functional

- SKP-1: **Reviewed 2026-11-24** Fast checks: skip what a later check covers, and time-limit the rest <!-- reviewed d78eaff4 -->
  - Principle 3 (Fast). Page: docs/wiki/Fast-checks.md.
  - ### Problem
  - My fast-cut ran 3 local test runs and 2 wiki regenerations before its PR, and the PR's full GitHub run then covered every test anyway.
  - Checks have no time limit, so one slow check holds every later step.
  - ### Requirements
  - SKP-1.1 Each check names the later check that covers the same risk. When that later check is certain to run on the same change, the earlier one is skipped, and the record names the cover. One example: the local test run, when the PR's reached-test run on GitHub is the merge evidence.
  - **Metric.** Checks run whose risk a later check on the same change fully covers. Target 0.
  - **Test.** A goal whose PR gets a reached-test run on GitHub records no local test run, and names that run as the cover.
  - SKP-1.2 Generated files are regenerated once, from committed data only, right before the leak read. They're never regenerated in a loop.
  - **Metric.** Regenerations per goal past one. Target 0.
  - **Test.** A goal that changes a test row regenerates the wiki once, and the leak read covers that commit.
  - SKP-1.3 Each check has a time limit at each level: a goal step, a PR, a merge and a release. A check over its limit shows "missed: <cause>", and the next step starts at once.
  - **Metric.** Checks over their limit with no cause shown. Target 0.
  - **Test.** A check past its 5-minute limit shows its cause, and the goal's next step has already started.
  - ### Non-goals
  - It never skips a check on CBS-1.2's fixed list.
  - It doesn't choose which checks a size runs: that's CBS-1.
  - ### Reference
  - adapted: Google's presubmit practice (light checks early; the full suite still runs before submit).
  - adapted: Lean "remove waste before optimising".
  - own: the covered-by skip, recorded with its cover.

### Non-functional

None

## Non-goals

- It never skips a check on CBS-1.2's fixed list.
- It doesn't choose which checks a size runs: that's CBS-1.

## Success metrics

- **Metric.** Checks run whose risk a later check on the same change fully covers. Target 0.
- **Metric.** Regenerations per goal past one. Target 0.
- **Metric.** Checks over their limit with no cause shown. Target 0.

## Revisions

### SKP-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-24 | Fast checks: skip what a later check covers, and time-limit the rest <br> Principle 3 (Fast). Page: docs/wiki/Fast-checks.md. <br> ### Problem <br> My fast-cut ran 3 local test runs and 2 wiki regenerations before its PR, and the PR's full GitHub run then covered every test anyway. <br> Checks have no time limit, so one slow check holds every later step. <br> ### Requirements <br> SKP-1.1 Each check names the later check that covers the same risk. When that later check is certain to run on the same change, the earlier one is skipped, and the record names the cover. One example: the local test run, when the PR's reached-test run on GitHub is the merge evidence. <br> **Metric.** Checks run whose risk a later check on the same change fully covers. Target 0. <br> **Test.** A goal whose PR gets a reached-test run on GitHub records no local test run, and names that run as the cover. <br> SKP-1.2 Generated files are regenerated once, from committed data only, right before the leak read. They're never regenerated in a loop. <br> **Metric.** Regenerations per goal past one. Target 0. <br> **Test.** A goal that changes a test row regenerates the wiki once, and the leak read covers that commit. <br> SKP-1.3 Each check has a time limit at each level: a goal step, a PR, a merge and a release. A check over its limit shows "missed: <cause>", and the next step starts at once. <br> **Metric.** Checks over their limit with no cause shown. Target 0. <br> **Test.** A check past its 5-minute limit shows its cause, and the goal's next step has already started. <br> ### Non-goals <br> It never skips a check on CBS-1.2's fixed list. <br> It doesn't choose which checks a size runs: that's CBS-1. <br> ### Reference <br> adapted: Google's presubmit practice (light checks early; the full suite still runs before submit). <br> adapted: Lean "remove waste before optimising". <br> own: the covered-by skip, recorded with its cover. | migration r1; date from its stamp | o916: "Approve all three (Recommended)" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [cover-claim](Tests#t-cover-claim) | requirement | SKP-1 | Given a goal whose PR will get L1 on GitHub, when its qa lane starts, then the covered rows run no local row, only the uncovered rows run as a partial lane, every unknown keeps the whole lane, and the cover is never granted at pr. | PASS 2026-11-25 |
| [cover-ids-lane](Tests#t-cover-ids-lane) | requirement | SKP-1 | Given a lane that runs only some rows, when regression.py run takes --ids, then exactly those rows run as one lane with the memory wait and a slot, no tracked file is written and the record keeps the other rows. | PASS 2026-11-25 |
| [cover-moves](Tests#t-cover-moves) | requirement | SKP-1 | Given the reach finder moved to row_reach.py, when the modules load, then the moved code is byte for byte the old code, every old name still resolves, every entry point imports alone and in the cycle orders, and the runner fingerprint covers the new files. | PASS 2026-11-25 |
| [cover-batch-body](Tests#t-cover-batch-body) | requirement | SKP-1 | Given a goal that ran with a cover, when a batch merge names it, then the batch is refused with COVER_NOBATCH, and a failed PR body edit refuses with BODY_STALE without a merge, lane or push. | PASS 2026-11-25 |
