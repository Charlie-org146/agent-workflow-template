<!-- workflow-docs -->
# Checks by size

Review: **Unreviewed**

How to use: [How-to-use-Checks-by-size](How-to-use-Checks-by-size)

## Problem

- Status: written, not built. Built by goal v110-cbs-asz. Reviewed approves the wording; availability is shown separately.
- Every one of my goals runs the full set of checks, whether it's a 20-line fix or a new gate. On 11-22 to 11-23, plan review took 32 to 144 minutes a goal, whatever its size.
- Planning already sizes goals (DEL-22). The checks should follow the same size, from one place.

## Requirements

### Functional

- CBS-1: **Unreviewed** Checks by goal size: one table says which checks each size runs
  - Goal routine (the standard every goal follows), beside DEL-22's plan levels. Page: docs/wiki/Checks-by-size.md.
  - ### Problem
  - Every one of my goals runs the full set of checks, whether it's a 20-line fix or a new gate. On 11-22 to 11-23, plan review took 32 to 144 minutes a goal, whatever its size.
  - Planning already sizes goals (DEL-22). The checks should follow the same size, from one place.
  - ### Requirements
  - CBS-1.1 One settings table lists, for small, medium and large goals, which checks run and in which named form. The template ships defaults, and only my words change the table.
  - **Metric.** Checks run that the table doesn't call for. Target 0.
  - **Test.** A small goal's record shows exactly the table's checks for small, each in its named form.
  - CBS-1.2 Some checks are in every row and can't be lightened: the build gate, the full test run before merge, two leak readers on hand-written text before any push, and every safety class.
  - **Metric.** Goals merged without one of these. Target 0.
  - **Test.** A table row that skips the full test run for small goals is refused when settings are read.
  - CBS-1.3 Each lighter form is defined in advance and says what it still covers, such as one review round, or one red-team pass with no reruns. A goal never improvises a lighter check.
  - **Metric.** Lighter checks recorded without a named form. Target 0.
  - **Test.** A medium goal's red team runs light; its record names the form and shows one pass.
  - CBS-1.4 Every check a goal skipped or ran light is listed on its release. The cut shows the list and can require a full run of any of them first.
  - **Metric.** Skipped or light checks missing from the release list. Target 0.
  - **Test.** Three goals skip a check; the release lists all three, and a cut that requires it runs it first.
  - ### Non-goals
  - It doesn't size goals: DEL-22 does, and ASZ-1 picks the size.
  - It doesn't make any check faster or cheaper: that's SKP-1 and CHP-1.
  - ### Reference
  - adapted: risk-based testing, ISO/IEC/IEEE 29119 (test depth follows the risk of the change).
  - own: the size table with its fixed rows that can't be turned off.

### Non-functional

None

## Non-goals

- It doesn't size goals: DEL-22 does, and ASZ-1 picks the size.
- It doesn't make any check faster or cheaper: that's SKP-1 and CHP-1.

## Success metrics

- **Metric.** Checks run that the table doesn't call for. Target 0.
- **Metric.** Goals merged without one of these. Target 0.
- **Metric.** Lighter checks recorded without a named form. Target 0.

## Revisions

None

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| - | requirement | CBS-1 | no passing test | not enforced |
