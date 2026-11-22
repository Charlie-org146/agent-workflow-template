# Fix #5727: the full regression workflow's matrix-smoke job fails on main at the adopt step with SETUP_PRIVATE_NAME because #5682 made the private-name hook fail closed when no list exists and gave only the regression step an empty list (owner o712, Operation TD687). Re-frozen as fix-5727-smoke-env-2 to widen the Touches: the matrix-smoke job is generated from lanes_cli.py MATRIX_JOB, the setup skill lists its refusal codes, and the Tests page is rendered

- Slug: fix-5727-smoke-env-2
- Touches: .github/workflows/regression.yml, skills/workflow-setup/scripts/setup.py, dev/toy, .loop/regression.tsv, skills/workflow-regression/scripts/lanes_cli.py, skills/workflow-setup/SKILL.md, docs/wiki, .loop/regression-known.tsv
- ETA: 225 active minutes (estimate 179m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given regression.yml's matrix-smoke job, then its run step gets env LOOP_PRIVATE_NAMES: /dev/null, the same as #5682 gave the regression step, and nothing else in the workflow changes
2. Given setup.py's SET-8 private-name check, then it tells the hook's exit 2 (no list, or the list or scan is broken) apart from exit 1 (a real hit), and the refusal names the real cause in each case
3. Given a toy, then it covers both exits: a missing list refuses with the no-list cause, and a real hit refuses with SETUP_PRIVATE_NAME, and no existing test is loosened
4. Given the full regression run on main after the merge, then matrix-smoke is green, and the goal stops at a draft pull request held for review whose body comes from the PR notes

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

Fixes #5727.

**What was wrong.** #5682 made the private-name hook fail closed: with no list it exits 2 (and for a broken list or scan), a real hit exits 1. The full regression workflow's matrix-smoke job runs `matrix-smoke.py`, whose adopt step runs `setup.py` on a toy repo. On a runner with no list the hook exited 2, `setup.py` read every nonzero exit as "a staged adoption file holds a private name", and the adopt step failed with `SETUP_PRIVATE_NAME` although nothing private was staged. Only the regression step had been given an empty list.

**What this changes (7 files, +53/-2 before the notes and the restamp):**
- `skills/workflow-regression/scripts/lanes_cli.py`: the matrix-smoke job is generated, so the fix goes into its generator `MATRIX_JOB`: the "Smoke set on Linux" step gets `env: LOOP_PRIVATE_NAMES: /dev/null`, the same line #5682 gave the regression step.
- `.github/workflows/regression.yml`: regenerated from that generator with `regression.py workflow`. The diff is exactly those two added lines (the env block); no trigger, permission, secret, job or other step changes, and `regression-pr.yml` is unchanged. A hand edit of this file alone would have been reverted by the next regeneration, which is why the generator carries the change.
- `skills/workflow-setup/scripts/setup.py`: SET-8 keeps `SETUP_PRIVATE_NAME` for hook exit 1 (text unchanged) and refuses any other nonzero exit as the new `SETUP_PRIVATE_LIST`: it shows the hook's exit number, says the hook's own line above names the cause and its repair, warns that an empty list scans for nothing, prints no command of its own, and rolls back as before (nothing written).
- `skills/workflow-setup/SKILL.md`: the refusal-code list states both meanings.
- `dev/toy/test-setup-adopt.sh`: a new case `set8-no-list-refused` (no existing case changed): no list, a list file that does not exist, a stand-in hook that exits 64 and one killed by a signal (all refused as `SETUP_PRIVATE_LIST`, nothing written), a real hit (still `SETUP_PRIVATE_NAME`, the name not printed), and a check that the matrix-smoke step carries the empty list in both the generator and the committed workflow. It declares that it reads `regression.yml`.
- `.loop/regression.tsv` and `docs/wiki/Tests.md`: the row `defect-5727-smoke-private-list` and its rendered line.

**Evidence.** The new case passes; the row passes (RESULT 1 passed, 0 failed); `regression.py red` printed SEEN RED with `setup.py` reverted and again with the generator and workflow reverted; all 15 setup-adopt cases pass one by one (14 on a clean `origin/main`, same results there); `test-guard-enforce setup`, `test-scan-closed` and `test-matrix` pass; the full matrix-smoke set (package, adopt, freeze, qa, health, runbook, relay) passed in a scratch clone with the empty list; `docs.py check` reads DOCS OK. Review ran at full depth, two passes (testing, maintainability and performance specialists, Claude and Codex adversarial, exploratory QA), converged. The plan reviews (CEO, eng and DX) were run by hand because the autoplan guard refused its first phase read; the run record quotes the refusal.

**Disclosures.** These fail identically on a clean `origin/main` and are not from this change: `test-regression.sh` (11 failing lines, including the shard split), `test-package-headroom.py` (`workflow-health/scripts/report.py` is over its 19,000-byte cap, which also makes the matrix-smoke package step fall back to a plain ZIP) and the full `test-setup-adopt.sh` run stopping at an early case (each case passes when run alone). Done line 4 (matrix-smoke green on the full run on main) can only be shown after the merge, by the next scheduled full run. The pull request is opened ready for review under the owner's later instruction, not as a held draft.

**Decisions left for the owner (both recorded as PENDING in the review; the recommended answer, skip, was kept):**
1. Whether `matrix-smoke.py` should set its own empty private-name list the way `actions.row_env` does for rows. Without it, a machine or agent session with no list still fails the adopt step, now with the accurate `SETUP_PRIVATE_LIST` (it already failed there since #5682, with the wrong code). Past done line 1, so not done here.
2. Whether `regression.py workflow` should patch an existing consumer repo's matrix-smoke job: it appends the job only when absent, so a repo that already holds the old job does not get the env line.

**Follow-ups for the owner (none changed here):** `release.py:244` and `workflow-health` `controls.py:464` read the hook's exit codes the same way `setup.py` did (any nonzero is a hit); `private.py`'s own repair text says "an empty file passes", but an empty list scans nothing; `setup.py`'s call to the hook has no parent-side timeout (the hook has its own 30-second alarm on POSIX only); a crash inside `private.py` that exits 1 still reads as a private name; a missing sibling `private.py` skips the scan silently (existing behavior).

**Merged-in work by the toy identity.** The branch holds the known-list row for `ls-narrow-triggers` (owner o711, #4061) in `.loop/regression-known.tsv`, from commit 546b5500f, whose author is the leaked toy identity "Toy" (#5749), not a person. The history is left as it is. After main took the shard-timeout-30 patch (abe55bdf7), which fixes `ls-narrow-triggers`' stale shard-list clause, that row passes on main, so the merge dropped the known-list row this branch added (#4061, TD851); the known list now holds only main's rows.
