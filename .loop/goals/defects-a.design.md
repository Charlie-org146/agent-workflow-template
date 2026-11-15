# Design: defects-a (five open defects)

## Problem

Five small defects are open: monitor.py report may crash on a non-record JSON in loop/runs (#3862), goal.py pr can copy a home-folder path into the pull request body (#3841), goal.py pr posts required statuses for checks the lane does not run (#3840), render.py hardcodes regression.yml in Tests links (#3839), and flow.py starts a headless `claude -p` for an unbound goal with `workers: app` (#4184).

## Approaches

1. One fix per defect, each in the script that owns it, each with a regression row seen failing first. Cost: five small edits and one shared toy; risk: the size caps (private.py, flow.py, role.py are near 20,480 bytes).
2. A shared "claims" module for pull-request text and statuses. Cost: a new file (the package is at the 99-file cap); more risk. Rejected.

Chosen: approach 1, with new helpers in spend.py (room left) so the capped scripts grow by a few bytes.

## What each done line needs

- #3862: v0.28.51 already skips non-record files; a row (monitor-stray-runs-3862) proves it, and the PR closes the issue with that proof.
- #3841: private.plain also strips Windows home folders; role.lane_part runs the lane's row lines through it too.
- #3840: spend.lane_checks keeps a required check only when a workflow job of that name runs only regression.py; the rest print BLOCKS; goal.py posts on the pull request's real head (after the bookkeeping commit), not the pre-bookkeeping commit.
- #3839: render.workflow_file reads the regression routine's `github:FILE` from the automation registry; regression.yml stays the default.
- #4184: spend.app_only; flow.py refuses a new step for an unbound goal when `workers: app`, naming `sessions.py bind SLUG SESSION`; a running job is untouched.

## Open questions

- Auto-binding a session in `goal.py new` (the second half of #4184's text) is not in the done line; left for a follow-up.
- test-statuses.sh needs a workflow with the jobs lane-a and lane-b now; it skips on Windows, so Linux CI is its check.
