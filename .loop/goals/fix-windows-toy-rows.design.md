# Design: fix-windows-toy-rows

## Problem
Four regression rows pass on GitHub's Linux run and fail on native Windows, and they fail the same on the base commit, so this is not a product defect: the toys assume POSIX paths and line endings. They are `rows-pr-full` (dev/toy/test-shard-balance.py), `orv-start-review` and `orv-checks-stay` (dev/toy/test-one-review-start.py) and `toy-leak-row-setup` (an inline command in .loop/regression.tsv). Until they pass on the PC, a goal's qa record on this machine is refused (LANE_MISSING).

## What is known (read from the failing runs, no new run yet)
- test-shard-balance.py: the "affected" check builds a bash command with a Windows-style path in its text (`python3 C:\...\cutgate.py ...`) and runs it with bash in a Windows temp folder; the toy then reads `all.tsv` from that folder and it is missing (FileNotFoundError). The likely cause is the backslashes in the command or the folder, which bash treats as escapes.
- test-one-review-start.py: three checks refuse with "no approved item names AB-1 on docs/wiki\F.md" and "the unit of AB-1 is not the approved text", then a `git commit` in a temp repo raises CalledProcessError. The page path is compared with a backslash on Windows where the fixture writes a slash; the later commit failure may be the same cause or a separate one.
- toy-leak-row-setup: its own setup steps (init, commit, stage) succeed on Windows, so the failing step is the borrowed command of the row `toy-leak-config-keep`, which runs two other toys (test-budget-order.py, test-merge-where.py) under a temp HOME. That is a second layer to find; the CRLF warning on `git add` is only a warning.

## Approaches
A. Fix each toy where it assumes POSIX: use forward slashes (`as_posix`) in bash command text and in compared page paths, and make the staged-file check indifferent to CRLF. Every fix changes how a path or line ending is handled, never what a toy asserts. Cost: three small edits, plus finding the second layer in toy-leak-config-keep's command. Risk: low if each is seen red first on Windows.
B. Mark the four rows Windows-skip (skip-windows.sh, as other rows do). Cheapest, but it loosens the proof: done line 4 forbids it, and board-views' qa record would then be vacuous for these rows.

## Chosen: A
Reproduce each row red on native Windows first (first build step, one toy at a time, with the exact failing line named), then fix and rerun. If a row's second layer turns out to be a real product defect, stop and tell the operation session rather than widen the goal (OPS-1.10).

## What each done line needs
1. rows-pr-full: the shard-balance toy passes on Windows; the paths it passes to bash and the folder it reads agree.
2. orv-start-review and orv-checks-stay: the one-review-start toy passes all its checks on Windows with page paths compared with `/`.
3. toy-leak-row-setup exits 0 with core.autocrlf on, including the borrowed config-keep command.
4. No assertion or expected result is loosened; each row is seen red on Windows before its fix, and the fix commit names the line changed.
5. The standard package line: every script under 20,480 bytes, no test loosened, no row red, no committed private text.

## Open questions
- Whether test-one-review-start.py's final commit failure is the same cause as its path checks (found in the first build step).
- Whether toy-leak-config-keep's command passes on Windows by itself (it is a different row; if it fails there too, fixing it is in scope only as the dependency of toy-leak-row-setup).
