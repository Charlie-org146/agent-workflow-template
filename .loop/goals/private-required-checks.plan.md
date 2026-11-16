# Plan: private-required-checks

1. tests.py: `classify` and the local run in `lane_checks`; trim its header text to fit. 2. lane.py: loader takes the function name (net zero bytes). 3. private.py: `unsatisfiable`. 4. goal.py: stop before the PR with the names; trim its docstring to pay for it. 5. dev/toy/test-private-checks.py: fixture workflows with gh stubbed (required_checks and gh calls monkeypatched): regression-only, plain script, third-party, failing plain script, negative control. 6. rows seen red, docs, flow.

## Tests
plain job run and posted; failing plain job not posted green and named; third-party job named and pr stops; regression-only passes as before (negative control).

## What could break
Running a repo's own CI commands locally: bounded by a timeout and only for jobs of plain run steps. Windows: the steps run through sh.

## Out of scope
The real private repo; secrets-using jobs; matrix jobs.

PENDING: none
