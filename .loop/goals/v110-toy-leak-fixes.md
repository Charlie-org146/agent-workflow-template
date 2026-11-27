# Four known toy leaks fixed

- Slug: v110-toy-leak-fixes
- Touches: skills/workflow-regression/scripts/actions.py, dev/toy/test-merge-where.py, dev/toy/test-budget-order.py, dev/toy/test-platform-limits.py, dev/toy/test-entry-config.sh, .loop/regression.tsv, docs/wiki/Tests.md
- ETA: 460 active minutes (estimate 367m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given test-merge-where.py started from a checkout, when it ends, then it has written no run record into that checkout.
2. Given a row started while a lane's handoff variables are set, when its environment is set, then it holds none of the lane's note, queued or started paths.
3. Given test-platform-limits.py started by a caller whose home trusts no folder, when it runs, then its session checks pass.
4. Given test-entry-config.sh run from a worktree, when it ends, then it has not changed that repo's user name or email and has registered no worktree in it.
5. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## Notes

Build notes from the plan step (operation rulings TD2043 to TD2046). Plan: .loop/goals/v110-toy-leak-fixes.plan.md. All six plan reviews and the one red team read the text with sha1 0a96639ab672, which is kept privately and not edited (TD1811); the file here is that plan reworded for publication with the same meaning, sha1 6922e7719dc4 (TD2086). The build waits for v110-no-size-cap-a.

### Required items for the build

Each fix is proved red and green as that check's own assertion.

1. Build: line 4's checks fail on a git read error, find this run's values in the clone with the same probe, and show the checkout's name and email entries the same before and after. The line 4 red also tries today's fixed values. The check says only changed or unchanged and never prints a real name or email.
2. Build: the new line 4 row fails on every FAIL line except the one named old control, and requires the toy's other PASS lines.
3. Correction to the plan's sentence on the paths that start rows: row_env covers the rows started by runs.execute, cmd_criteria and cmd_red; the remaining row-start paths are deferred; the list is kept privately.
4. Build: item 1; and before each recorded red, a run with a break that changes nothing prints STILL GREEN. Line 1's recorded break is 1a (the early change back with the stand-in kept); 1b is shown by hand.
5. Build:
   - Both toys unset inherited GIT_* at the top; mktemp, the clone and each cd before an identity write are guarded; the clone's origin is removed after checking that red and the rows do not need it; the clone's worktrees are pinned to the checkout's HEAD commit; the whole new toy is run from a detached worktree, and a shallow one is checked, reading every PASS and FAIL line; the clone mode for a busy object store is picked after measuring.
   - Line 3 asserts that assign d under the stand-in home refuses with FOLDER_TRUST, with the session pool and send count unchanged.
6. Build: user.name and user.email are checked before every commit, and each commit's author afterwards.

### Deliver-first lines

- DF1 (owner: #5352 alone): "Build: row entry-committed-config passes again, with its negative control able to fail for its stated reason (#5352)."
- DF2: "Build: the remaining row-start paths are deferred; the list is kept privately. The slots.started() docstring says what a row receives."

Neither touches .loop/regression-known.tsv.

### The red team's 10 breaks and their dispositions

One pass on plan sha1 0a96639ab672. The record's accept mark (o1000, set by the operation for principles 2, 3, 4 and 8) does not say which break is which; this table does (TD1830). RT is the line in the reader's reply; id is the first 8 characters of the SHA-1 of the break's text in the red-team record.

| RT | principle | id | disposition | what the build or record does |
|---|---|---|---|---|
| RT1 | 2 | 3e5c6641 | fixed in build (TD2043/TD2044) | Required item 2. |
| RT2 | 2 | 8134d73c | fixed in build (TD2043/TD2044) | Required item 1. |
| RT4 | 2 | fa61fee7 | fixed in build (TD2043/TD2044) | Required item 5, line 3. |
| RT13 | 3 | f4245c20 | accepted risk | The wait on v110-no-size-cap-a is the operation's; the build record carries its ETA when it has one. |
| RT14 | 4 | 1c103dcb | accepted risk | The goal's budget from the freeze is 240 minutes and 3,000,000 tokens; the ETA is 460 active minutes. |
| RT15 | 3 | 551482f4 | accepted risk | The build times one full run of the entry toy and records it. |
| RT16 | 2 | e2b11ec8 | accepted risk | REG-4's text says at most 600 rows; main already has 764; the prerequisite's done line 1 allows any number. |
| RT17 | 2 | d3b65389 | accepted risk | The reds for lines 2 and 3 are quoted in the build record and the PR body. |
| RT18 | 2 | 1bd39054 | named deferral | DF2. |
| RT20 | 8 | 00cef940 | accepted risk | Delivery fills Verify by hand with numbered steps and Expect lines before release. |

### Two further red-team points (not breaks)

- RT5, accepted risk: line 3's clean test home relies on how the folder-trust check treats the toy's new empty home.
- RT6, accepted risk and named deferral: the further line 1 check is not added here. "Build: line 1 also checks that a fixture slug unique to the run leaves no record in the real checkout's common git folder."

### Reviews

All six plan reviews said build with changes; none rejected. The goal's record keeps each verdict cut at 200 characters (a tool limit); the Claude engineering verdict is the one cut.

### Added during the build

- Build: the two toys and the row filter no longer pass the caller's git environment.
- Build: one fix from the review to the git settings that rows and the toys keep.
- Red for line 2 (RT17; run on the same patch as 4da454609): "FAIL: a row never inherits a lane's note, queued or started path".
- Red for line 3 (RT17; run on the same patch as 5425fb21b): "FAIL: d: with no free session a new one is refused with the reason" and "FAIL: d: a free (archived) session is woken, renamed and sent the goal".

### Red team pass 2 (the rerun, on plan sha1 6922e7719dc4) and its dispositions

One Codex pass after the size of this goal rose to large. It added three breaks to the record; pass 1's ten are unchanged. The record's accept mark (o1000, set by the operation for principles 2, 3, 4, 7 and 8) does not say which break is which; this table does. N is the break's order in pass 2; id as in the table above.

| N | principle | id | disposition | what the build or record does |
|---|---|---|---|---|
| N1 | 2 | de85878b | in two parts: fixed in build; the part pass 1 already raised stays deferred | The row-merge checker (dev/check-row-merge.py) starts rows with the row environment; row toy-leak-row-merge. The deferred part is DF2. |
| N2 | 2 | fcb48bc2 | deliver-first, with DF1 (#5352) | "Build: the entry toy's old control reports a setup error apart from its expected result." |
| N3 | 7 | 0fa1c48f | deliver-first | "Build: the entry toy runs with its own git configuration and home." |
