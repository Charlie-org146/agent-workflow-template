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
"` in the fixture, a line-ending fix, not a changed comparison and not a path normaliser. The earlier STOP for a product-code backslash is superseded by the Red team revisions below (the cause is criteria.py, now in scope).
- toy-leak-row-setup: step 4 is gated on step 1 naming the failing step of the borrowed `toy-leak-config-keep` command (it runs test-budget-order.py, test-merge-where.py and under it test-entry-config.sh). `dev/toy/test-entry-config.sh` joins Files conditionally; a failing layer outside dev/toy or `.loop/regression.tsv` stops the goal the same way. Any edit to the `toy-leak-config-keep` command is shown by a diff read to change handling only, never what it checks. If a CRLF-tolerant staged-file check is needed it uses `tr -d '
'` on the output, never a looser pattern. Done line 3's wording ("CRLF") may not match the root cause; the true cause is recorded.
- Neighbours to rerun on Windows by row name after each fix: shard-balance, budget-order-first, toy-leak-merge-where, toy-leak-row-merge, toy-leak-config-keep, and the toys beside the edited ones (test-shard-budget.py, test-one-review-decide.py, test-one-review-findings.py).
- Package line (done line 5): the 20,480-byte cap is for scripts under skills/*/scripts (the package caps check names `skills/workflow-x/scripts/`), not for dev/toy files, so edits to test-one-review-start.py (45 KB) do not trip it; the package gate head is run at the end to show it.
- Linux: the same commands run on Linux with only path and line-ending handling changed; GitHub's run on the PR head is the proof for "stays green on Linux" (no local Linux run).
- Files: skills/workflow-docs/scripts/criteria.py, dev/toy/test-shard-balance.py, dev/toy/test-one-review-start.py, .loop/regression.tsv (only if the borrowed row command needs it), and conditionally dev/toy/test-budget-order.py, dev/toy/test-merge-where.py, dev/toy/test-entry-config.sh (named by step 1, not before).

## Red team revisions (3 BREAKs; this section wins over the earlier ones; condensed re-plan)
- The STOP for a product-code backslash is removed. The backslash in "docs/wiki\F.md" comes from `skills/workflow-docs/scripts/criteria.py:102` (`os.path.join(folder, name)`), which reaches `start_answer.py:276` through `milestones.py:290` and `deployments.py:259`; it is not `start_answer.py:313` or `read_diff`. The operation session added `skills/workflow-docs/scripts/criteria.py` to Touches. Fix: make `criteria.pages()` return a repo path joined with "/". The line-609 commit failure in test-one-review-start.py is most likely the same cause; step 1 confirms it.
- Fixed rule for the toys (B2): a toy edit may only change how a fixture is written (`newline="\n"`, how a path is quoted), never an expected value or a comparison. No normalising helper in the toy; the expected strings at test-one-review-start.py lines 627, 636 and 668 stay literal "docs/wiki/F.md". Done line 4's evidence is a fresh-context reader's check of every changed assertion line, not my own diff read.
- rows-pr-full (fail-open): the row greps two PASS lines only; the build also requires test-shard-balance.py to exit 0 with no FAIL line, and row `shard-balance` (regression.tsv:633), which runs the same toy, is in the Windows reds and greens.
- test-shard-balance.py quoting: use `shlex.quote` (or single quotes) around the path in the bash command at line 112 (the red team's fix), not `as_posix`; name which `bash` runs, since `C:\Windows\System32\bash.exe` (WSL) can win the search: resolve Git Bash explicitly or check for it and stop.
- Before step 1: run `toy-leak-config-keep` alone on Windows once; if it is red, find the layer (it may be the MSYS `$h` path in .gitconfig, regression.tsv:753). `dev/toy/test-entry-config.sh` joins Files only if named.
- A row command in `.loop/regression.tsv` may change only how it handles paths, and each such change is listed as a deliver-first line for the owner.
- Scrub absolute home paths and the account name out of every red output before it goes into the PR notes, replacing the temp root with `<tmp>`.
- The PR's affected rows must select `toy-leak-row-setup` on Linux; if they do not, run it explicitly and put that run in the PR's CI evidence.
- Build notes: line cites (test-shard-balance.py 112, 119, 122; test-one-review-start.py 348, 445, 569); CRLF comes from text-mode `open`, not from autocrlf; done line 3's CRLF premise is a deliver-first line, since the row compares names only.
- Files adds `skills/workflow-docs/scripts/criteria.py` (and its Windows-red neighbours: milestones.py, deployments.py are read, not edited, unless step 1 names them); `dev/toy/test-shard-balance.py` and `dev/toy/test-one-review-start.py` stay.

## Last read and operation notes
- Which bash: the toy resolves Git Bash explicitly (the `bash.exe` beside the `git` it runs, under the Git install's usr/bin or bin folder) and STOPS the toy with a clear message if it cannot find it; it never takes the first `bash` on PATH.
- Done line 2 and the literal expected strings: done line 2's "compared the same with / or \" is met by the product producing "/" paths (criteria.pages() joins with "/"), so the toy's literal "docs/wiki/F.md" expectations are stricter than a tolerant comparison, not looser.
- criteria.py (operation notes, top confirms it stays in this goal with no split): its fix is shown red first on Windows (the row failing before the change), and its LF byte count after the change is pasted and must be under 20,480 bytes.
- Done line 3: if toy-leak-row-setup passes on Windows with no change, the line is met as written; the PR notes say why (the row compares names only) and it goes to the owner as a deliver-first line.
- Touches: the goal file's Touches line is the operation session's to extend (it said it added skills/workflow-docs/scripts/criteria.py); the build waits on that line showing it.

## PENDING
PENDING: 1. Whether test-one-review-start.py's failure is a fixture line-ending problem (in scope) or a backslash built in product code (stop and report): resolved by step 1.
PENDING: 2. Which layer of the `toy-leak-config-keep` command fails on Windows and whether it lies in dev/toy: resolved by step 1.

## Build notes (wording from the fixes read)
- No fix is written before step 1's red capture for that row exists.
- If the STOP for a product-code backslash fires, done line 2 stays unmet in this goal; no toy-side normaliser is added.
- test-entry-config.sh is in Files only if step 1 names it as the failing layer.

Files: dev/toy/test-shard-balance.py, dev/toy/test-one-review-start.py, dev/toy/test-budget-order.py, dev/toy/test-merge-where.py, dev/toy/test-entry-config.sh, .loop/regression.tsv
Lines: 60
Gates: none
Classes: none
