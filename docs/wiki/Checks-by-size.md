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

- CBS-1: **Reviewed 2026-11-24** Checks by goal size: one table says which checks each size runs <!-- reviewed 3bbde7e1 -->
  - Goal routine (the standard every goal follows), beside DEL-22's plan levels. Page: docs/wiki/Checks-by-size.md.
  - ### Problem
  - Every one of my goals runs the full set of checks, whether it's a 20-line fix or a new gate. On 11-22 to 11-23, plan review took 32 to 144 minutes a goal, whatever its size.
  - Planning already sizes goals (DEL-22). The checks should follow the same size, from one place.
  - ### Requirements
  - CBS-1.1 One settings table lists, for small, medium and large goals, which checks run and in which named form. The template ships defaults, and only my words change the table.
  - **Metric.** Checks run that the table doesn't call for. Target 0.
  - **Test.** A small goal's record shows exactly the table's checks for small, each in its named form.
  - CBS-1.2 Some checks are in every row and can't be lightened: the build gate, the PR's reached-test run before merge, two leak readers on hand-written text before any push, and every safety class.
  - **Metric.** Goals merged without one of these. Target 0.
  - **Test.** A table row that skips the PR's reached-test run for small goals is refused when settings are read.
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

### CBS-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-24 | Checks by goal size: one table says which checks each size runs <br> Goal routine (the standard every goal follows), beside DEL-22's plan levels. Page: docs/wiki/Checks-by-size.md. <br> ### Problem <br> Every one of my goals runs the full set of checks, whether it's a 20-line fix or a new gate. On 11-22 to 11-23, plan review took 32 to 144 minutes a goal, whatever its size. <br> Planning already sizes goals (DEL-22). The checks should follow the same size, from one place. <br> ### Requirements <br> CBS-1.1 One settings table lists, for small, medium and large goals, which checks run and in which named form. The template ships defaults, and only my words change the table. <br> **Metric.** Checks run that the table doesn't call for. Target 0. <br> **Test.** A small goal's record shows exactly the table's checks for small, each in its named form. <br> CBS-1.2 Some checks are in every row and can't be lightened: the build gate, the PR's reached-test run before merge, two leak readers on hand-written text before any push, and every safety class. <br> **Metric.** Goals merged without one of these. Target 0. <br> **Test.** A table row that skips the PR's reached-test run for small goals is refused when settings are read. <br> CBS-1.3 Each lighter form is defined in advance and says what it still covers, such as one review round, or one red-team pass with no reruns. A goal never improvises a lighter check. <br> **Metric.** Lighter checks recorded without a named form. Target 0. <br> **Test.** A medium goal's red team runs light; its record names the form and shows one pass. <br> CBS-1.4 Every check a goal skipped or ran light is listed on its release. The cut shows the list and can require a full run of any of them first. <br> **Metric.** Skipped or light checks missing from the release list. Target 0. <br> **Test.** Three goals skip a check; the release lists all three, and a cut that requires it runs it first. <br> ### Non-goals <br> It doesn't size goals: DEL-22 does, and ASZ-1 picks the size. <br> It doesn't make any check faster or cheaper: that's SKP-1 and CHP-1. <br> ### Reference <br> adapted: risk-based testing, ISO/IEC/IEEE 29119 (test depth follows the risk of the change). <br> own: the size table with its fixed rows that can't be turned off. | migration r1; date from its stamp | o916: "Approve all three (Recommended)" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [sizing-cbs-1-1](Tests#t-sizing-cbs-1-1) | requirement | CBS-1 | Given the checks table, when a small goal is sized, then its record shows exactly the table's small checks, each in its named form. | PASS 2026-11-27 |
| [sizing-cbs-1-2](Tests#t-sizing-cbs-1-2) | requirement | CBS-1 | Given a table row that skips the full test run for small goals, when the table is read, then it is refused naming the row and the check. | PASS 2026-11-27 |
| [sizing-cbs-1-3](Tests#t-sizing-cbs-1-3) | requirement | CBS-1 | Given a medium goal, when its red team runs light, then its record names the form and shows one pass, and the full form is refused. | PASS 2026-11-27 |
| [sizing-cbs-1-4](Tests#t-sizing-cbs-1-4) | requirement | CBS-1 | Given three goals that skip a check, when cutcheck runs, then it lists all three, and a required full run runs the check first and fails the cut when it fails. | PASS 2026-11-27 |
