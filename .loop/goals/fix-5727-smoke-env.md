# Fix #5727: the full regression workflow's matrix-smoke job fails on main at the adopt step with SETUP_PRIVATE_NAME because #5682 made the private-name hook fail closed when no list exists and gave only the regression step an empty list (owner o712, Operation TD687)

- Slug: fix-5727-smoke-env
- Touches: .github/workflows/regression.yml, skills/workflow-setup/scripts/setup.py, dev/toy, .loop/regression.tsv
- ETA: 325 active minutes (estimate 260m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given regression.yml's matrix-smoke job, then its run step gets env LOOP_PRIVATE_NAMES: /dev/null, the same as #5682 gave the regression step, and nothing else in the workflow changes
2. Given setup.py's SET-8 private-name check, then it tells the hook's exit 2 (no list, or the list or scan is broken) apart from exit 1 (a real hit), and the refusal names the real cause in each case
3. Given a toy, then it covers both exits: a missing list refuses with the no-list cause, and a real hit refuses with SETUP_PRIVATE_NAME, and no existing test is loosened
4. Given the full regression run on main after the merge, then matrix-smoke is green, and the goal stops at a draft pull request held for review whose body comes from the PR notes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
