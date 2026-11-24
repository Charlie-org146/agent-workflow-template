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

- SKP-1: **Unreviewed** Fast checks: skip what a later check covers, and time-limit the rest
  - Principle 3 (Fast). Page: docs/wiki/Fast-checks.md.
  - ### Problem
  - My fast-cut ran 3 local test runs and 2 wiki regenerations before its PR, and the PR's full GitHub run then covered every test anyway.
  - Checks have no time limit, so one slow check holds every later step.
  - ### Requirements
  - SKP-1.1 Each check names the later check that covers the same risk. When that later check is certain to run on the same change, the earlier one is skipped, and the record names the cover. One example: the local test run, when the PR's full GitHub run is the merge evidence.
  - **Metric.** Checks run whose risk a later check on the same change fully covers. Target 0.
  - **Test.** A goal whose PR gets a full GitHub run records no local test run, and names that run as the cover.
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

None

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| - | requirement | SKP-1 | no passing test | not enforced |
