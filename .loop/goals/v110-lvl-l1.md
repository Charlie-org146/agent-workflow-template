# Test levels G2 (LVL-1.1, LVL-1.3 run rule, LVL-1.4; owner o980, o985; split TD1749): L1 on the pull request

- Slug: v110-lvl-l1
- Touches: skills/workflow-regression, skills/workflow-delivery, .github/workflows, dev/toy, .loop/regression.tsv
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
