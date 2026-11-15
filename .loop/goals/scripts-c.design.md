# Design: scripts-c

## Problem

Eleven scripts under skills/workflow-health/scripts and skills/workflow-regression/scripts are over 19,000 LF bytes (defects 20,474, lanes 20,341, lean 20,236, workflows 20,213, health 20,027, runs 19,974, controls 19,949, narrow 19,777, file 19,621, enforce 19,460, regression 19,183), and issue #3821 says migration-check's MIG_AUTOMATION rule (enforce.py `automation_gaps`) wrongly flags a public repo that runs the regression in Actions.

## Approaches

**A. Trim prose and dead code in place.** No new file; the package is at its 99-file cap. Cost: many small edits across eleven files. Risk: behavior change, held down by touching only comments, docstrings, provably unused code and repeated blocks with identical results, and by running each file's Python toys.
**B. Move code into new modules.** Rejected: the package has 99 files, the cap.

## Chosen: A

For #3821 the reviewed spec says public repos use actions and private repos use mac, so `automation_gaps` now accepts `regression_runs: actions` when .github/workflows/regression.yml exists and flags anything else; the leftover-workflow check in defects.py (`gaps_files`) already flags regression.yml only when regression_runs is mac, so it stays and the toy locks it in.

## What each done line needs

1. Sizes: every .py in both folders at most 19,000 LF bytes, shown by one row per skill (scripts-c-health-under-19000, scripts-c-regression-under-19000) seen red.
2. #3821: toy test-migration-runs.py (public, private, leftover and wrong-setting cases), row migration-runs seen red; close #3821 with the proof after the merge.
3. No reviewed requirement text changes.

## Open questions

- Which requirements the size rows link to. Recommended: HLT-2 (health's Size rule) and REG-9.
