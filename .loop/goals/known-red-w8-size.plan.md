# known-red-w8-size: plan

Claims checked against the code and the CI log: each of the nine rows' commands and the FAIL text in run 44463859531; the sizes of every script in the five skill folders; `docedit` (a throwaway) only replaces docstrings and four comment texts; board_lines.py has 1,676 bytes of room and live_board imports board_lines (hence the lazy import).

## Build steps (done and committed)

1. SKILL.md line caps (rewrap), skill-kept toy re-aim, setup.py, regression.py, lanes.py, runs.py (its notes go to the regression references), report/rules/automation/controls (docstring trims only), the checkin.py move and kept stamps.
2. Merge main (v1.0.80); then main again after w11 lands.

## Tests per done line

1. Each row's own command on the PR head: the five size rows pass by hand on Windows; the toy rows (skill-kept, skill-size-116, size-141) skip on Windows and are proven by CI; the lane runs the rest. docs-release-scripts-under-19000 waits for w11.
2. regression-known.tsv is untouched and regression.tsv has the same 1,300 ids as main.

## What could break

- A moved helper breaks an import: 12 monitoring toys pass; checkin.gather is board_lines.gather (asserted).
- Docstring text a toy reads: grep of dev/toy for each cut phrase found none that asserts on it.
- Stale pages: restamped; the health references are not touched, so Principles is not stale.

## Out of scope

The eleven docs scripts (w11), any behaviour change, any row added or waived.
