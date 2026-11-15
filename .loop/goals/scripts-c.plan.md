# scripts-c plan

Checked against the code on origin/main plus the work already done on this branch.

## Build steps (done)
1. Trim the eleven scripts under 19,000 LF bytes: comments, docstrings, one unused constant (`CLASSES` in defects.py), `lean.rows()`, an unused import and constant, and a few repeated blocks folded into helpers (`lean.load`, `lean.land_seconds`, `lean.top`, `workflows.conf_of`); no printed text, exit code or return value changed.
2. `enforce.automation_gaps`: accept regression_runs `actions` when `.github/workflows/regression.yml` exists, or `mac`; flag anything else (#3821). `defects.gaps_files` already flags regression.yml only for mac; unchanged.
3. Toy `dev/toy/test-migration-runs.py`; rows `migration-runs`, `scripts-c-health-under-19000`, `scripts-c-regression-under-19000`, each seen red (restoring origin/main's enforce.py; appending 1,500 bytes to lean.py and runs.py).

## Test for each done line
1. the two size rows. 2. migration-runs. 3. no reviewed text edited (the diff touches no docs/wiki page).

## What could break
- A trimmed docstring that is `--help` text: module `usage:` blocks were kept.
- A removed unused name that something imports: grepped across skills, dev and .github; the package gate and the Python toys of each file pass.
- Package file cap: still 99 files.

## Out of scope
- workflow-setup scripts (adoption owns them); docs and release scripts (scripts-b).
