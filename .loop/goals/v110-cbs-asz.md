# Implement CBS-1 and ASZ-1 (v1.1.0 Task 14, priority 1; owner o907): one table says which checks each goal size runs, and the loop sizes each goal itself

- Slug: v110-cbs-asz
- Touches: skills/workflow-delivery, skills/workflow-monitoring, .loop/config.json, dev/toy, .loop/regression.tsv, skills/workflow-release
- ETA: 420 active minutes (estimate 335m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each CBS-1 and ASZ-1 test case on their pages, when the regression runs, then each runs as a real test linked to its requirement and passes, and each fails on a fixture that breaks only that rule.
2. Given a goal's plan, when it is frozen, then it is sized small (3 files or fewer, 150 lines or fewer, no gate and no safety class), medium (10 files or fewer and no safety class) or large (everything else) with its reason recorded, its checks come from the CBS-1 table, and a goal touching a safety class is always large.
3. Given a goal whose build passes its size, when the build is recorded, then it is re-sized up and the added checks run before its PR, and a goal's size never goes down during the goal.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
