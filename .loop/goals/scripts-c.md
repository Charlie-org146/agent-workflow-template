# scripts-c, v1.0.0 group 7 (third script-size goal): every .py file under skills/workflow-health/scripts and skills/workflow-regression/scripts is at or under 19,000 bytes with LF endings, and #3821 (the MIG_AUTOMATION rule and the leftover-workflow check follow the reviewed spec) is fixed

- Slug: scripts-c
- Touches: skills/workflow-health/ skills/workflow-regression/

## Done lines

Frozen. A wrong done line needs a new goal.

1. every .py file under skills/workflow-health/scripts and skills/workflow-regression/scripts is at or under 19,000 bytes counted with LF endings, reached by trimming prose and dead code or moving code into a new module, with the package staying at 99 files or fewer
2. #3821 is fixed: the MIG_AUTOMATION rule in enforce.py and the leftover-workflow check in defects.py accept regression_runs=actions for a public repo whose .github/workflows/regression.yml exists and flag a leftover regression.yml only when regression_runs is mac, shown by a toy case seen red, and #3821 is closed with the proof
3. one regression row per skill (workflow-health and workflow-regression) holds the size line, on a requirement both skills already have, each seen red; no reviewed requirement text changes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-migration-runs.py` and `python3 dev/toy/test-hook-count.py`. Expect: every line starts with PASS and each exits 0.
2. Count the bytes of every `.py` under `skills/workflow-health/scripts` and `skills/workflow-regression/scripts` with LF endings (the two size rows do it). Expect: none is over 19,000.
3. Run `python3 dev/toy/test-package-gate.py head`. Expect: a PASS line saying the package passes with 99 files or fewer.
