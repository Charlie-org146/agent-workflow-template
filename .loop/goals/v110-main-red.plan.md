# Plan: v110-main-red, the four rows that are red on main pass on main in the clean env

## Implementation plan

Goal: make the rows tasks-rows-only-added, guards-null-report-nofiles, full-auto-no-new-file and codex-key-commands pass on main when run from the clean environment, by finding and fixing the cause of each, with no row loosened, skipped or added to a known list. A patch, no version task. Owner o1015 (ledger o961); the done lines and the one workflow change are approved by owner o1026 (ledger o966). Issues 5870, 5871, 5872 and 5895.

Size of the change: small to medium. One line added to each of two checkout steps in the scheduled regression workflow, and a cause hunt for the live Codex row that may need only its toy or its documented precondition. No script under skills/ is expected to change; if the Codex cause is in one, its bytes and room go in this plan before any edit.

### Depends on (order)
Nothing. It shares no file with the goals now in flight (their changes are in skills scripts and the schedule modules; this one is in dev/toy, the regression workflow and, only if a row's command must change, the regression table).

### What exists
- Three of the four rows are history rows: each reads a past goal's own merge on the base branch (the tasks text goal, the null-report goal, the full-auto goal) and compares it with its first parent. With no remote-tracking ref for the base branch, or a shallow history, each fails ("the base ref is missing here", "the change this row was written for adds no file under skills"). Given the base ref and full history, all three print ALL PASS locally (first reading, a clean clone, clean environment).
- The scheduled regression workflow's checkout steps use the default depth of one commit, so on GitHub the history rows see a shallow clone with no history of the base branch. The pull request workflow and the release workflow check out with full history. The scheduled run on main shows exactly these three rows red (tasks-rows-only-added, guards-null-report-nofiles, full-auto-no-new-file), each on its own shard.
- The live Codex row (codex-key-commands) is red on main in the clean environment with six failed checks, and its cause is not known: a missing Codex sign-in under an emptied environment is likely but unverified. It already skips by design (exit 77) when Codex is not installed or not signed in on the runner; the issue is that it fails, not skips, here.

### Design
A. History rows. Add full history (fetch depth zero) to the two checkout steps of the scheduled regression workflow that run the shards and the summary, nothing else in any workflow. This matches the pull request workflow, loosens no row, and keeps every check and negative control. It is the only workflow change and is the owner's (o1026). The third checkout step in that file is left as it is unless the build shows a history row runs there.
B. Prove it before and after. A toy case builds a shallow clone of a fixture and runs the three history checks against it (red: the base ref and merge are missing), then against a full clone (green). The three rows' own commands stay unchanged.
C. The live Codex row. The build reproduces the six failures in the clean environment and names the cause. If the cause is the environment (no sign-in, no tool on the path), the fix is the row's documented precondition and the toy's honest skip (exit 77 only where Codex really cannot answer, with the reason printed), never a loosened check. If it is a defect in a script, the fix is to that script and its bytes and room are stated first. If the cause needs a guard change, a secret or a sign-in in CI, the build stops and asks the operation (a safety class).
D. No loosening. No row is changed, skipped, added to the known list or removed; the regression table changes only if a row's command must change, with the same checks and the same negative controls and its approved-row-changes line.

### Files
Edited: the scheduled regression workflow (two checkout steps), the Codex toy (only if the cause is there), the regression table (only if a command must change). New: at most one toy file for the shallow-versus-full history case, if it does not fit in an existing toy. No script under skills/ unless the Codex cause is in one (then its bytes and room first).

Files: .github/workflows/regression.yml, dev/toy/test-codex.sh, dev/toy/test-tasks.py
Lines: about 60
Gates: the planning gate, the build gate, the ship gate
Classes: security (one GitHub workflow change, fetch depth zero on two checkout steps, owner o1026)

### Tests
Each done line is one row run in the clean environment (empty environment but HOME, PATH, TERM and LOOP_ROLE): the four rows pass singly. A new toy case shows the three history checks red on a shallow clone and green on a full one. The Codex cause gets its own case, red on the head before the fix. The package line is covered by the existing size, no-loosened-test, no-red-row and private-name checks.

### NOT in scope
Any workflow file other than the scheduled regression workflow; any change to the pull request or release workflows; loosening, skipping or adding a row to the known list; a version task.

### Decisions (the planner's, for review)
- Way (a), full history on the scheduled run's checkouts, over way (b), toys that fetch the one merge they read: (a) is one line per checkout, matches the pull request workflow, loosens nothing and needs no network inside a toy. It goes to the owner as the one safety-class question and is covered by o1026.
- The Codex row: a cause hunt first; the plan fixes the rule for what each cause may change, not the cause.

### Alternatives weighed and set aside
- Toys that find their merge without the base ref or deep history (fetch the one merge, or skip with 77 where history is missing): skipping loosens the row and fetching needs network in a toy.
- Adding the three rows to the known list or the skip list: forbidden by the goal.

### Risks
The Codex cause may need a guard, a secret or a sign-in in CI; then the build stops and the owner is asked. The workflow change is a safety class and waits for the owner's word as o1026 gives it. Confidence in the estimate is low (40%) because of the Codex cause.
