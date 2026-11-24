<!-- workflow-docs -->
# Cheap checks

Review: **Unreviewed**

How to use: [How-to-use-Cheap-checks](How-to-use-Cheap-checks)

## Problem

- Status: written, not built. Built by goal v110-chp-1. Reviewed approves the wording; availability is shown separately.
- Every check costs me time and tokens whether or not it finds anything. Overnight, the red-team reruns mostly reworded the same breaks.
- Nobody can see which checks earn their cost, so none is ever retired.

## Requirements

### Functional

- CHP-1: **Unreviewed** Cheap checks: the cheapest form that does the job, and retire checks that find nothing
  - Principle 4 (Cheap). Page: docs/wiki/Cheap-checks.md.
  - ### Problem
  - Every check costs me time and tokens whether or not it finds anything. Overnight, the red-team reruns mostly reworded the same breaks.
  - Nobody can see which checks earn their cost, so none is ever retired.
  - ### Requirements
  - CHP-1.1 Every check records its time, tokens and findings on each run. The board shows each check's cost per finding.
  - **Metric.** Check runs with no recorded cost or findings. Target 0.
  - **Test.** After 10 goals, the board lists every check's minutes, tokens and findings, sorted by cost per finding.
  - CHP-1.2 A light form uses the cheapest means that still covers its risk. For example, a mechanical shape check for generated files instead of two readers, or a smaller model for one-pass reviews. Each form says what it gives up.
  - **Metric.** Light forms with no stated coverage. Target 0.
  - **Test.** A wiki table regeneration passes a shape check with no reader run, and the record names the form.
  - CHP-1.3 A check whose last 10 runs, for a kind of change, found nothing but process choices is flagged with its total cost. One line from me removes it or keeps it.
  - **Metric.** Checks with 10 empty runs and no flag. Target 0.
  - **Test.** After 10 empty red-team passes on small goals, the board flags them with their minutes and the line that removes them.
  - ### Non-goals
  - It never removes a check without my line.
  - Hand-written text always gets two readers before a push (CBS-1.2).
  - ### Reference
  - adapted: cost-of-quality accounting (what each check costs against what it prevents).
  - own: the cost-per-finding board and the 10-empty-runs flag.

### Non-functional

None

## Non-goals

- It never removes a check without my line.
- Hand-written text always gets two readers before a push (CBS-1.2).

## Success metrics

- **Metric.** Check runs with no recorded cost or findings. Target 0.
- **Metric.** Light forms with no stated coverage. Target 0.
- **Metric.** Checks with 10 empty runs and no flag. Target 0.

## Revisions

None

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| - | requirement | CHP-1 | no passing test | not enforced |
