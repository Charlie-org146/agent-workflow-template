# Plan: fix-windows-toy-rows

Design: `.loop/goals/fix-windows-toy-rows.design.md` (approach A: fix each toy's path and line-ending handling; never loosen an assertion).

## Checked against the code
- `dev/toy/test-shard-balance.py` exists; its "affected" check (near line 117 to 123) builds `script = "python3 " + os.path.join(root, "skills", "workflow-regression", "scripts", "cutgate.py") + " 's/shard-[0-7]/t.tsv'"`, runs it with `bash -c` in a `tempfile.mkdtemp` folder, then reads `all.tsv` there.
- `dev/toy/test-one-review-start.py` exists; its page fixture writes `docs/wiki/F.md` (lines about 557 to 562) and three checks refuse on `docs/wiki\F.md`; a later `git commit` in a temp repo raises CalledProcessError.
- The row `toy-leak-row-setup` is an inline command in `.loop/regression.tsv`; its own steps (init, commit, stage) pass on Windows; it then runs the command of row `toy-leak-config-keep`, which runs `dev/toy/test-budget-order.py` and `dev/toy/test-merge-where.py` under a temp HOME.
- Rows `rows-pr-full`, `orv-start-review`, `orv-checks-stay` are in `.loop/regression.tsv` and call those toys.

## Build steps (each: seen red on Windows first; the fix changes handling of paths or line endings, never an assertion)
1. Reproduce each of the four rows red on native Windows (clean env, Git Bash) and name the failing line of each in the commit message; also run `toy-leak-config-keep`'s command by itself and name its failing step.
2. test-shard-balance.py: pass bash a forward-slash path (as_posix) for cutgate.py and the working folder, so `all.tsv` lands where the toy reads it.
3. test-one-review-start.py: compare and write page paths with `/` (a small normalising helper where the toy joins or compares paths); then re-run to see whether the final commit failure remains; if it does, name its cause and fix it the same way or stop and report.
4. toy-leak-row-setup: fix the layer step 1 names (the toys under the borrowed command, or the staged-file check made indifferent to CRLF with `core.autocrlf` on), editing the toy or the row command, not what it asserts.
5. Re-run the four rows and the neighbours of each touched toy on Windows, then the package check; the rows stay as they are for Linux (the same commands, only the toys' handling changes).

## Tests (one per done line)
Each of the four rows seen red on Windows before its fix and green after (done lines 1 to 3), shown by the row's own command; for done line 4 a diff read of each commit: no assertion text, expected value or row command changed except the path or line-ending handling named; done line 5 by the package gate.

## What could break
The Linux run of the same toys (a forward slash is also fine there; a CRLF-tolerant check must still catch a real missing file), and the other rows that share these toys or the borrowed command.

## Out of scope
Anything beyond the four rows (OPS-1.10); no new rows; no change to product code under skills/.

## Review round revisions (ceo approve; design and engineering changes; this section wins over the steps above)
- Causes are hypotheses until step 1 names the failing line of each row. Step 1 also names which `bash` ran (Git Bash or the System32 launcher) and captures each red run's output into the PR notes as the red evidence for done line 4.
- test-shard-balance.py: the fix is `Path(...).as_posix()` for the cutgate.py path inside the bash command text only; `cwd=work` stays native. If `all.tsv` is still missing, the cause is elsewhere and step 1's capture says where.
- test-one-review-start.py, likely cause: the fixture's `put()` (lines 50 to 52) and `commit()` (55 to 58) and the owner-words writes (about 445 and 465) use text-mode `open()` with no `newline`, so autocrlf turns the page into CRLF: the fix is `newline="
"` in the fixture, a line-ending fix, not a changed comparison and not a path normaliser. The backslash in "docs/wiki\F.md" is built in product code (`skills/workflow-delivery/scripts/start_answer.py:313`, from `safety_scan.read_diff`): if step 1 shows the refusal text still carries a backslash after the fixture writes LF, that is a product defect outside Touches and the goal STOPS and reports to the operation session; it does not narrow done line 2 and it does not patch around it in the toy.
- toy-leak-row-setup: step 4 is gated on step 1 naming the failing step of the borrowed `toy-leak-config-keep` command (it runs test-budget-order.py, test-merge-where.py and under it test-entry-config.sh). `dev/toy/test-entry-config.sh` joins Files conditionally; a failing layer outside dev/toy or `.loop/regression.tsv` stops the goal the same way. Any edit to the `toy-leak-config-keep` command is shown by a diff read to change handling only, never what it checks. If a CRLF-tolerant staged-file check is needed it uses `tr -d ''` on the output, never a looser pattern. Done line 3's wording ("CRLF") may not match the root cause; the true cause is recorded.
- Neighbours to rerun on Windows by row name after each fix: shard-balance, budget-order-first, toy-leak-merge-where, toy-leak-row-merge, toy-leak-config-keep, and the toys beside the edited ones (test-shard-budget.py, test-one-review-decide.py, test-one-review-findings.py).
- Package line (done line 5): the 20,480-byte cap is for scripts under skills/*/scripts (the package caps check names `skills/workflow-x/scripts/`), not for dev/toy files, so edits to test-one-review-start.py (45 KB) do not trip it; the package gate head is run at the end to show it.
- Linux: the same commands run on Linux with only path and line-ending handling changed; GitHub's run on the PR head is the proof for "stays green on Linux" (no local Linux run).
- Files: dev/toy/test-shard-balance.py, dev/toy/test-one-review-start.py, .loop/regression.tsv (only if the borrowed row command needs it), and conditionally dev/toy/test-budget-order.py, dev/toy/test-merge-where.py, dev/toy/test-entry-config.sh (named by step 1, not before).

## PENDING
PENDING: 1. Whether test-one-review-start.py's failure is a fixture line-ending problem (in scope) or a backslash built in product code (stop and report): resolved by step 1.
PENDING: 2. Which layer of the `toy-leak-config-keep` command fails on Windows and whether it lies in dev/toy: resolved by step 1.

Files: dev/toy/test-shard-balance.py, dev/toy/test-one-review-start.py, dev/toy/test-budget-order.py, dev/toy/test-merge-where.py, dev/toy/test-entry-config.sh, .loop/regression.tsv
Lines: 60
Gates: none
Classes: none
