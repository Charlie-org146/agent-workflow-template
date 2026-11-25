# Plan: v110-main-red, the four rows that are red on main pass on main in the clean env

## Implementation plan

Goal: make the rows tasks-rows-only-added, guards-null-report-nofiles, full-auto-no-new-file and codex-key-commands pass on main in the clean environment, by finding and fixing the cause of each, with no row loosened, skipped or added to a known list. A patch, no version task. Owner o1015 (ledger o961); the done lines and the workflow change are approved by owner o1026 (ledger o966); the revisions below follow the decision top recorded on o1014 (TD1705). Issues 5870, 5871, 5872 and 5895.

What "the clean environment" means for each done line: BOTH GitHub's scheduled regression job and the local clean-environment lane (the environment emptied but for HOME, PATH, TERM and LOOP_ROLE), and each must pass. Where a needed ref such as the base branch's remote ref is missing, a row FAILS, naming the ref and the fix, and never passes vacuously. This reads the done lines; it does not change them.

Size of the change: medium. One line added to the checkout of the regression job in the generator of the scheduled workflow and the workflow regenerated from it; one function of the generator moved whole into a new sibling module to keep its size under the line; tightened checks and error text in the three history toys and in the live Codex toy; a bounded diagnosis of the live Codex row with a timeout.

### Depends on (order)
Nothing. It shares no file with the goals in flight (their changes are in the schedule scripts and the delivery scripts).

### What exists
- Three of the four rows are history rows: each reads a past goal's own merge on the base branch and compares it with its first parent. With no remote-tracking ref for the base branch, or a shallow history, each fails ("the base ref is missing here", "the change this row was written for adds no file under skills"). Given the ref and full history, all three print ALL PASS locally.
- The scheduled workflow has three checkout steps: the regression job (it runs the rows in sixteen shards, so the history rows run there), the summary job (it downloads the shards' result files and writes one table; it runs no row and reads no history) and the matrix-smoke job (it runs the smoke set, not the history rows). All use the default depth of one commit. The pull request and release workflows use full history. The scheduled run on main shows exactly the three history rows red, each on its own shard.
- The workflow file is GENERATED: skills/workflow-regression/scripts/actions.py holds its template (its checkout step carries persist-credentials: false) and writes it; a toy in dev/toy (test-regression.sh) asserts the generator's output equals the committed file. So the workflow cannot be changed by editing the YAML alone: that fails the parity check and is undone by the next regeneration.
- actions.py is 18,997 bytes, 3 bytes under the 19,000 line (hard fail 20,480); it holds the template, a render function (1,062 bytes), a write function (1,212 bytes) and constants.
- The history toys call git diff and treat a failed diff as an empty change (a vacuous pass), and the live Codex toy verifies matching output without checking that the child command succeeded. Both are defects this goal must close (tightening only).
- The live Codex row (codex-key-commands) is red on main in the clean environment with six failed checks and its cause is not known. It already skips by design (exit 77) when Codex is not installed or not signed in; the issue is that it fails here.

### Design
A. Generator. Add fetch-depth: 0 beside persist-credentials: false in the checkout of the regression job in actions.py ONLY (TD1697: the summary and matrix-smoke checkouts stay unless the build shows a history row runs or is read there, and then that one is named here with its evidence first); regenerate the workflow with the tool's own write command; the parity toy stays green. No other line of any workflow changes (owner o966).
B. Byte plan for actions.py (a pure move, no edit of the moved text). Move ONE function, write (1,212 bytes), whole into a NEW sibling module of the same folder, actions_write.py (about 1,380 bytes with its imports and header). actions.py imports it at its bottom (after render is defined; the new module imports render from actions) so every existing caller of actions.write keeps working. actions.py goes from 18,997 to about 17,830 bytes before the one added line and about 17,860 after, the new module is about 1,380; both under 19,000. A toy calls write through the old name. The new file is the owner's to allow (a new script in the package), asked before the build.
C. History toys. A failed git diff, or any failed child command, is a FAILURE with a stable code, naming the repository, ref and merge it was reading and the safe fix (git fetch --unshallow; git fetch origin main, or the CI setting fetch-depth: 0), saying nothing was changed, and exiting non-zero; never an empty change. Every existing assertion and negative control is kept; the new checks only tighten. Negative controls: a fixture where git diff fails must fail the row, and a shallow fixture must name its fix.
D. The live Codex row. First a bounded diagnosis: run the row from the clean environment with a timeout and closed standard input (so Codex can never prompt), retain the invocation, versions, the names of the environment variables involved and the command artifacts, and name the cause of the six failures. The row's verification checks every command's expected exit status together with its existing assertions, and the toy validates the Codex process status; add controls for a failure after a success marker and after result files are written. The row must PASS in the clean environment on this machine with an authenticated Codex. The existing skip (exit 77) for a host with no Codex stays as it is for such hosts only and never counts as the goal's PASS: an unavailable prerequisite is incomplete work, reported as such. If the cause needs a guard change, a secret or a sign-in in CI, the build STOPS and asks the operation; nothing is converted to a skip. A missing sign-in is such a cause. The failure messages print the precondition, the human command, the reason, side effects none and a trace path.
E. No loosening. No row is changed, skipped, added to the known list or removed; the regression table changes only if a row's command must change, with the same checks and negative controls and its approved-row-changes line.

### Files
Edited: the generator (actions.py), the scheduled workflow (regenerated), the parity toy only if its assertion needs the new line (it should not), the three history toys, the live Codex toy, the regression table only if a command must change. New: the sibling module for the moved function (actions_write.py), and a toy case for the history failures and one for the Codex verification if they do not fit in the existing toys.

Files: skills/workflow-regression/scripts/actions.py, skills/workflow-regression/scripts/actions_write.py, .github/workflows/regression.yml, dev/toy/test-tasks.py, dev/toy/test-guards-null-report.sh, dev/toy/test-full-auto-files.py, dev/toy/test-codex.sh
Lines: about 150
Gates: the planning gate, the build gate, the ship gate
Classes: security (one GitHub workflow change, fetch depth zero on the regression job's checkout, owner o1026)

### Tests
Each done line is one row run singly in the clean environment: the four rows pass, in GitHub's regression job and in the local clean-environment lane. New toy cases, each red on the head before its fix: a failed git diff fails the history row with its code and fix; a shallow fixture names its fix; the Codex verification fails on matching output with a failing status. The parity toy stays green on the regenerated workflow; a case calls write through its old name. The package line is covered by the existing size, no-loosened-test, no-red-row and private-name checks, plus the byte plan above.

### NOT in scope
Any workflow file other than the scheduled regression workflow, and in it any line other than the regression job's checkout step; loosening, skipping or adding a row to the known list; converting the Codex failure to a skip; a version task; a guard change, a secret or a sign-in in CI (those stop the build and go to the owner).

### Decisions (the planner's, for review)
- The generator is the source; the YAML is regenerated, not edited.
- write (not render) is the function that moves: it depends only on render and the standard library, so the move is pure; render depends on the template and many constants.
- The Codex row must truly pass; the exit-77 skip stays only for hosts with no Codex and is never the goal's pass.
- The done lines mean both GitHub's job and the local lane.

### Alternatives weighed and set aside
- Editing the YAML only: fails the parity toy and is undone by regeneration.
- Trimming 25 bytes elsewhere in actions.py: it is a whole-file trim to fit, which the size rule refuses.
- Toys that fetch the one merge they read, or skip where history is missing: skipping loosens a row; fetching needs network in a toy.
- Adding the rows to the known list or the skip list: forbidden by the goal.

### Risks
The Codex cause may need a guard, a secret or a sign-in in CI; then the build stops and the owner is asked. The new file and the workflow change are safety-class and wait for the owner's word. Confidence in the estimate is low (40%) because of the Codex cause.
