# Fix the four Windows-only regression rows (rows-pr-full, orv-start-review, orv-checks-stay, toy-leak-row-setup) that fail the same on base, so board-views' qa record can pass on the PC (owner o336, TD2448).

- Slug: fix-windows-toy-rows
- Review: one
- Touches: dev/toy, .loop/regression.tsv
- ETA: 240 active minutes (estimate 190m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a native Windows checkout (Git Bash, Python 3), when the regression row rows-pr-full runs, then dev/toy/test-shard-balance.py passes, with its temp folder path and all.tsv read the same on Windows as on Linux, and the row stays green on GitHub's Linux run.
2. Given a native Windows checkout, when the rows orv-start-review and orv-checks-stay run, then dev/toy/test-one-review-start.py passes all its checks, with the docs/wiki paths compared the same with / or \, and both rows stay green on GitHub's Linux run.
3. Given a native Windows checkout with core.autocrlf on, when the row toy-leak-row-setup runs, then its command exits 0 (the staged-file check isn't thrown off by the CRLF conversion), and the row stays green on GitHub's Linux run.
4. No row's expected result or assertion is loosened to pass: each fix changes how the toy handles paths or line endings, not what it checks, and each row is seen red on Windows before the fix.
5. The standard package line.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
