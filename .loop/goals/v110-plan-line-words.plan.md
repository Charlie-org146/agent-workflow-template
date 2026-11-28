# Plan: v110-plan-line-words

Rewrite line 75 of .loop/goals/fix-windows-toy-rows.plan.md so the drive-letter, forward-slash and MSYS forms of the Windows users folder are named in words, meaning unchanged. No other line changes.

Files: .loop/goals/fix-windows-toy-rows.plan.md

Lines: 1
Gates: none
Classes: none

Steps:
1. Line 75 holds the change (already made by hand commit 033701a07; disclose in the PR notes). The build step accepts the existing diff.
2. Fetch origin main first, so every check below uses a fresh origin/main. Done line 1 check: grep the added diff line only for a drive letter plus colon plus a slash or backslash, and for a leading slash, one letter, slash; both give 0 hits. The branch-wide cover is step 4's scan, which reads every added line, the commit messages and the goal files.
3. Done line 2 check: `git diff origin/main --numstat -- .loop/goals/fix-windows-toy-rows.plan.md` shows 1 added and 1 deleted (a replaced line); `git diff origin/main --name-only` lists that file plus only the goal's own two files (the goal file and this plan file). The PR notes say plainly that done line 2 is read this way.
4. Done line 3 check: `private.py scan --base origin/main` is clean on the branch at the final head, and a fresh commit of the patched tree (the plan file's own commit) passes the Mac's commit hook; the hook's pass is read from the commit succeeding, its file is not read. The hand commit 033701a07 passed it too.
5. Done line 4 (the standard package line) is run by the ship step and is not checked here.
