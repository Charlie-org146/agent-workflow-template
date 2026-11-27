# Test levels G2 (LVL-1.1, LVL-1.3 run rule, LVL-1.4; owner o980, o985; split TD1749): L1 on the pull request

- Slug: v110-lvl-l1
- Touches: skills/workflow-regression, skills/workflow-delivery, .github/workflows, dev/toy, .loop/regression.tsv, skills/workflow-regression/scripts/completion.py, skills/workflow-regression/scripts/levels_cli.py, skills/workflow-setup/scripts/settings.py, skills/loop-files.md, .loop/START.md
- ETA: 430 active minutes (estimate 342m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a change that reaches one L0 row, one L1 row and one L2 row, when L1 runs on its pull request, then the L0 and L1 rows run and the L2 row doesn't.
2. Given a goal whose pull request will get L1, when the goal reaches its test step, then its L0 rows run, it records no local L1 run, and it names L1 as the cover.
3. Given a green pull request in the merge queue, when the queue checks it, then no test row runs there and the queue's checks are the same as before this change.
4. Given a pull request whose change reaches no private row, when L1 runs, then every private row runs.
5. Given a security row that fails once and then passes, when L1 ends, then the row shows FLAKY, one issue is open, and it is not counted as a pass.
6. Given L1 runs for 11 minutes, when it ends, then it shows "missed: <cause>" with its three slowest rows, and every chosen row ran.
7. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. In a copy of this repository with its own .git folder and HOME, run `python3 dev/toy/test-l1.py`. Expect: the last line is `ALL PASS`.
2. In the same copy, run `python3 dev/toy/test-l1-pr.py`. Expect: the last line is `ALL PASS`.

## Notes

Departures from the plan (TD2073: the plan no longer matched the code it was written for), each with its reason:

1. Room in lanes_cli.py: table_changed moved whole into completion.py (merge_runs had already moved).
2. No marker step: the lvl-armed row is already in the table. Rows this goal adds have level entries.
3. The L1 functions are in completion.py (levels.py is past its split size and levels_read.py has no room); the miss report is in cutgate.py. notes and rank (from tiers.py) and fit, minutes and budget (from runs.py) also moved whole into completion.py, so tiers.py did not grow.
4. The flag is --test-level; the help of `add --test-level` now says what it does.
5. There is no noretry tag, so that clause is dropped.
6. A private row listed nightly runs on L1 with a NOTE; nothing is refused.
7. A security or private row is always L1, so there is no private row at L2.
8. flaky.tsv is uploaded by its own step with if-no-files-found: ignore (a hashFiles condition cannot see the runner's temp folder).
9. The private-name scan is loaded by path from the delivery skill; the secret-shape pattern is copied.
10. Step 1's local mapping is dropped (ruled by top): only the pull request's `nightly` run is L1. While the cover claims L1, the goal's local lane runs the L0 rows and the planned rows the pull request leaves out; with the cover off it runs as before.
11. regression-flaky.yml grants its three permissions on its one job, with `permissions: {}` at the top.
12. Plan v7 step 5's tail in the issue is dropped (safety F2): the flaky issue carries the row, 'failed then passed', the PR, the SHA and the checks link; no failure output leaves from CI.

Security:

- The owner approved the new .github/workflows/regression-flaky.yml (issues: write on its one job) and the level-map edit to .github/workflows/regression-pr.yml: owner record o1065 (earlier relayed approvals o991, o998).
- TRUST CHANGE: cover.py's WF_SHA, the fingerprint of the reviewed pull request workflow, is re-pinned to 533fbed6f28fac049a2bd2c45eaa3bdbffed1ac6. The value is computed from the committed file the way cover.py reads it: `git show HEAD:.github/workflows/regression-pr.yml | python3 -c 'import hashlib,sys; print(hashlib.sha1(sys.stdin.read().strip().replace("\r\n","\n").encode()).hexdigest())'`. A reviewer of this re-pin reads the workflow file it pins. The row lvl-l1-pin shows the cover is refused when the workflow differs.

Later work:

- Using a size's levels is not in this goal.

Pull request notes:

- TRUST CHANGE: the cover's pinned fingerprint of the pull request workflow changes with this goal's edit to that workflow (owner record o1065).
- A new workflow, regression-flaky.yml, runs from the default branch and files one issue for a security row that fails once and then passes (owner record o1065).
- Deliver-first: cover.py is 17,957 B, over the 17,500 B its earlier plan set for it (the 20,480 B limit holds).
