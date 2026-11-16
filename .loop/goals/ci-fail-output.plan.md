# Plan: ci-fail-output

1. actions.py: on a failing row, compute shown() once, append "#### FAIL id" plus its last 20 lines to GITHUB_STEP_SUMMARY, reuse the text for the issue body; trim comments to stay under 19,000 bytes; regenerate regression.yml.
2. dev/toy/test-ci-summary.py runs the workflow's block over a toy repo.
3. Rows ci-summary-fail-output and ci-summary-passing-left-out, both seen red.

Out of scope: grouping the 100 rows by cause (next goal).
