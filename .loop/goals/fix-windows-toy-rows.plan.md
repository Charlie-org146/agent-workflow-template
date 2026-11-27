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

## PENDING
none.

Files: dev/toy/test-shard-balance.py, dev/toy/test-one-review-start.py, dev/toy/test-budget-order.py, dev/toy/test-merge-where.py, .loop/regression.tsv
Lines: 60
Gates: none
Classes: none
