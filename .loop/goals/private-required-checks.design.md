# Design: private-required-checks

## Problem
On a private repo the base branch can require checks whose jobs run scripts other than regression.py (`checks`, `scan` on a v1.0.0 migration PR, #4537). Without Actions minutes those jobs never report. `private.pr_result` posts a local status only for a required check whose job runs regression.py alone (`tests.lane_checks`, #3840); the others only print BLOCKS after the PR is open, and the PR stays BLOCKED.

## Approaches
1. **Classify every required check; run the plain ones here; name and stop on the rest before the PR (chosen).** `tests.classify(top, contexts)` returns (regression, local, cannot): a job of `run:` steps only (no third-party `uses:`, no secrets, no matrix) is *local*, a regression-only job is *regression*, everything else *cannot*. `lane_checks` (the pr_result path) runs each local job's steps here and posts success only when every step exits 0 (a failing step is named, never posted green). Before the PR is opened `private.unsatisfiable(top, base)` lists the *cannot* checks of a private repo's required set and `goal.py pr` stops with that list. This is also the freeze-time dry run #4535 asks for.
2. Post success for every required check unseen: hides a failing check. Rejected.
3. Only name them after the PR is open (today): leaves the PR blocked. Rejected.

## Each done line
1. A fixture repo requiring a regression check, a plain script check and a third-party-action check: the plain one is run and posted, the third-party one is named and the pr step stops before the PR (toy cases).
2. Fixture requiring one regression check and one non-regression check, and a negative control requiring only the regression check: it passes as before, nothing named.

## Constraints
No new file (package cap): code in tests.py (classify), private.py (unsatisfiable) and a one-argument widening of lane.py's loader. goal.py and lane.py are over 19,000 LF bytes on main, so goal.py is trimmed by what it gains. Fixtures only; no real private repo is touched.
