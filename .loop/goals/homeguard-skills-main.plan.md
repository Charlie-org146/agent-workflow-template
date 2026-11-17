# homeguard-skills-main plan

Checked against the code: `homeguard.scan`, `other_runs`, `folder`, `main` (snap and diff), the `toy()` helper and the checks in test-home-guard.py, `git status --porcelain` in the real skills-main (clean today) exist as read.

## Build steps
1. homeguard.py: `other_runs` skips skills-main and the registry files (outside strict mode); `registry(top)`, `skills_main(top)`, `in_temp`, `temp_prefixes`; `scan` merges them.
2. test-home-guard.py: five checks (registry by another session, registry fixture in temp, skills-main moved, skills-main edited, skills-main stray file).
3. Rows homeguard-other-writer and homeguard-own-write, each seen red; done lines covered.
4. Regression and Tests re-rendered; DECISIONS.

## Tests per done line
1. other writer: registry real entry plus backup, skills-main committed move: exit 0, no LEAK.
2. own write: fixture entry, edited file, stray file: exit non-zero with the LEAK line naming the path.

## What could break
The guard on the real home: run it against the real folder (0.3 s, exit 0). A skills-main that is not a git checkout is hashed whole as before. Strict mode is unchanged.

## Out of scope
Per-process attribution; changing what lanes/ and the scheduler's own files allow.
