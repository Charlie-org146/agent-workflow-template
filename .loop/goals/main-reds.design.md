# Design: main-reds

Branch: loop/main-reds
Status: proposed for delivery review
Mode: Builder

## Problem
Nine specified issues obstruct trustworthy regression results and adoption. The owner approved one bundle (o22); success means fixing causes and proving behavior, including preventing recurrence where main already contains a partial fix.

## Premises
- Preserve the nine-issue boundary and the three frozen done lines. Suppressing red rows without fixing causes would leave main unreliable.
- Reuse existing process guards, milestone helpers and toy fixtures. No new dependencies or package files are needed.
- Main already contains optional-v matching in audit.release_trouble and Backlog milestone selection in milestones.py; verify their callers and regression evidence before changing working code.

## Alternatives
A. Targeted fixes in existing scripts and toy tests. Cost: medium; risk: localized behavior regressions. Reuses proctree, existing milestone helpers, regression rows and Home guard tests. Best fit for package caps and concurrent owners. Chosen.
B. Centralize all process and filesystem isolation in a new shared abstraction. Cost: large; risk: changes unrelated workers and increases package files. Cleaner in theory, but unnecessary to prove these nine defects.
C. Quarantine red rows. Cost: small; risk: silently loses coverage. Rejected because it fails the frozen done lines.

## Behavior and evidence to implement
1. #4901: routing.py imports proctree but still directly starts agent and login processes. Reuse the delivery process guard and verify the DEL-10 static check plus cancellation behavior. Limit changes to the issue's process starts to respect the agent-routing owner's scope.
2. #4896: file.saves_rows calls IS.about with one argument; use its actual signature and preserve stable issue matching. Repair Delivery How-to and README contract fixtures or production documentation according to failing output. Run judge-key-old, doc19-item-missing and link-unread-never-pass with all five session variables unset.
3. #4865: defects.ids_unique uses defined(root), which counts requirement-looking How-to items. Distinguish canonical requirement definitions from instructional references; retain a negative control with real duplicate definitions. Run consistency.
4. #4858 and #4683: homeguard.other_runs currently exempts lane tickets and certain scheduler output. Exempt routine logs written by other runs, preserve strict-mode checking and schedule registry/new-entry detection, and distinguish lane tickets from arbitrary state where applicable. Existing test-home-guard.py supplies safe TOY_REAL_WL fixtures; never test by writing the owner's folder. The issue body explicitly permits legitimate lane tickets.
5. #4772: setup catches KeyboardInterrupt and calls undo while update.commit may still own the index. Stop and wait for the git process tree before rollback, preferably in the existing subprocess helper; preserve hook refusals and Windows support. Prove the hook-signal row on the old and changed code, checking no child, lock or adoption state remains.
6. #4660: audit.release_trouble already accepts optional v. Add or confirm tests for bracketed and plain headings, optional v, and the gh fallback only when absent. Preserve the landed implementation if correct.
7. #4695: docs.cmd_sync delegates through audit.sync and milestones.py already defines Backlog milestone selection. Trace the actual filing call and test both existing Backlog and bare-name-only states, including creation when missing, without real issue writes.
8. #4758: assemble the toy SMTP value at runtime in test-machine.sh, keep checking that output never exposes the assembled value, and avoid a broad scanner exclusion.

## Proof and limits
Use existing toy files and register defect rows linked to all nine issues. Capture failing evidence against the relevant old code before each fix; reuse historical evidence only if supported by the regression tooling. Run affected rows on a clean committed checkout, remove owned known-red entries, keep every package script below 19000 bytes and the package at most 100 files. Commit only intended files; local config is excluded. Existing unrelated reds are outside scope.

## Failure modes
Overbroad Home exclusions could hide leaks; use negative controls for arbitrary state. Killing only git could orphan a hook; stop the process tree and wait before restoring the index. Excluding all How-to text could hide genuine definitions; use the documented requirement-page contract and real-duplicate controls. Existing main fixes could tempt duplicate changes; prove them first. Newly merged main may change test selection, so rerun the lane after merging.

## Distribution and next steps
Existing package and PR workflow distributes the fixes. Plan first, build with fail/pass regression evidence, review, qa, ship and create the PR through goal.py. Stop at the PR without merging.

## The Assignment
Inspect the PR's linked defect evidence for all nine issues before deciding whether it should merge.

## What I noticed
The owner said "Yes, one bundle" and specified precise rows and process behavior. Those constraints support localized fixes and evidence in one reviewable change, with no scope expansion.

## Open questions
No product decision remains. The full planning review must run before implementation; any unavailable mandatory review dependency must be reported rather than claimed complete.

## Reviewer Concerns

Disposition: COMPLETED

Stop: PASS

No blocking findings remain. The 1 open minor finding(s) below are recorded for the user, not fixed.

### R1-1 — clarity (minor)

**Problem**

> Behavior item 2 says to run with 'all five session variables unset' without naming the variables in this standalone design. The owner prompt contains their names, but a later planning reviewer given only this document cannot recover the exact list.

**Remedy**

> When producing the engineering plan, spell out CLAUDECODE, CLAUDE_CODE_HOST_SESSION_ID, CLAUDE_CODE_SESSION_ID, CLAUDE_CODE_SESSION_ATTENDED and CLAUDE_CODE_CHILD_SESSION, and apply the unsets to all lanes as the owner's instruction requires.
