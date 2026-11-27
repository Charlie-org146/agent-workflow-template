# Make the four rows that are red on main pass on main in the clean env, by finding and fixing each cause, with no row loosened, skipped or added to a known list (owner o1015, ledger o961; done lines and the regression.yml full-history change approved by owner o1026, ledger o966; issues #5870, #5871, #5872, #5895; a patch, no version task)

- Slug: v110-main-red
- Touches: dev/toy, .loop/regression.tsv, .github/workflows/regression.yml, skills/workflow-regression/scripts
- ETA: 450 active minutes (estimate 357m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given main, when the row tasks-rows-only-added runs in the clean env, then it passes.
2. Given main, when the row guards-null-report-nofiles runs in the clean env, then it passes.
3. Given main, when the row full-auto-no-new-file runs in the clean env, then it passes.
4. Given main, when the row codex-key-commands runs in the clean env, then it passes.
5. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## For the pull request

Fixes #5870 (row tasks-rows-only-added).

- #5871 (row guards-null-report-nofiles) and #5872 (row full-auto-no-new-file) stay open at merge. Main's scheduled run marks each "Passing again" and shuts it once its row passes there.
- Workflow change, stated plainly: the checkout of the scheduled regression job now fetches full history (fetch depth zero). It is set in the generator, actions.py, and regression.yml is regenerated; no other workflow line changes (owner o966).
- Done line 5, how it is read (TD2015): "every script stays under 20,480 bytes" means every packaged script.
- Row change (TD1995, o1074): tasks-rows-only-added now also fails whenever its test ends with an error. Stricter only; it has its approved-row-changes line.
- The tasks test now uses a fixed machine reading, the same one the shell tests get (#4375); every one of its conditions is unchanged. Separately, in the tasks test and the full-auto test, the forced failure for a missing origin/main became an exit with a HIST code that still fails: HIST-E01 for a missing ref, HIST-E02 for a shallow history, HIST-E03 for a git command that failed.
- Five wiki pages change: one line each on the two Regression pages and the two Fast-checks pages, plus the Tests re-render.
- New row: history-rows-fail-closed. A history row that can't read the history it compares fails with a code and its fix.
- Codex test, one expected value corrected, not loosened (TD2111): one check expected setup to refuse a bare agent command. That refusal was removed on purpose by aeca3f9c8 ("adoption never blocks"); the check now requires exit 0 and the agent_command gap line with its fix.
- Line 4's live proof was dropped under o1038 (top's TD2110), revertible by the owner typing "allow main-red's live Codex runs". Done line 4 is not shown met, and #5895 stays open. The lanes of this goal run with no Codex program, so codex-key-commands is SKIPPED there, which is not a pass.
- Red-team break 2 was decided by top under the owner's o1037 standing rule (TD2098(1)) and is revertible.
- Build review: three full rounds. Round 3 did not pass: one of its two readers failed it. As the operation decided (TD2125), its one item to fix now is fixed, and a fresh reader checked that change alone and passed it. No fourth full round was run, and round 3's other items are not fixed in this change.
- The four make-room rows (make-room-2-identical, make-room-4-surface, make-room-b-2-identical, make-room-b-4-surface) can only be shown by the first scheduled run on main that contains this change. That check is not met at merge.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
