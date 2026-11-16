# Design: lane-memory

## Problem
On the PC a lane's `lanes_cli.py affected` held 0.4 to 2.8 GB and ran 833 s, because the dependency walk entered `.git` (82,577 of 83,596 paths were inside it, every other worktree's files) and, on Windows, `normpath` made `.git\loop\...` slip past the `.git` guard in `references`. A lane that waited for memory and gave up reported LANE_BUG and charged a try, and rows that died with 0xC0000142 were counted as FAIL.

## Approaches
1. Fix the causes: `walk` skips `.git`, `references` normalizes slashes before its `.git` guard (small, in lanes.py); a new exit code EXIT_ENV (6) for "the machine, not the goal": runs.py marks start-failure codes ENV (a SKIPPED row with env), regression.py exits 6 when most rows are ENV, lanes_cli's memory wait exits 6 with a MEMORY_WAIT note, lane.py reports it, guards.py does not count it (own cap 10). Cost: small edits in six near-cap files. Risk: the byte caps.
2. Cap the process's memory (job object, a streaming walk) without touching the walk. Cost: much more code, Windows-only, and it hides the real bug. Rejected.

## Chosen
Approach 1. The cause is a wrong walk, so removing it is both the lean fix and the cheapest. ENV rows reuse the existing SKIPPED state so every reader of the run record still works, and they stay out of the NOTRUN to-do issues.

## What each done line needs
1. `affected` on the main checkout: before 1149 MB and 833 s, after 124 MB and 35 s (measured with a process-peak sampler); a toy walks a tree holding `.git` and checks nothing under it is listed or followed. MEMORY_WAIT: lanes_cli exits EXIT_ENV with a MEMORY_WAIT note, lane.py prints it as the lane line's last line, guards.failed_try counts no try (cap 10, then it counts); toy with negative controls (a LANE_FAIL still costs a try).
2. ENV: runs.py START_CODES (0xC0000142, STATUS_NO_MEMORY, commit limit), the lane prints `ENV id (exit N: could not start; rerun when memory allows)`; more than half ENV and none failed exits 6, which is not a counted try; toy with a row exiting 1 staying FAIL.

## Open questions
None for the owner. The five rows that README.md no longer selects (skill-criteria-in-references, skill-lines-docs-1403, skill-lines-docs-4171, template-in-commands, test-caps-controls) were reached only through files inside `.git`.
