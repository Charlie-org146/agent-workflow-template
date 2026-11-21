# The private-name scan fails closed (owner o675; TD527; DEL-9): with no private-name list found, the scan exits non-zero with one line naming the missing file, and every caller (goal.py pr, the plain route, routing finish, merge.py, hooks) treats that as a stop, never as clean; an empty list passes and a list with a planted hit fails. Only paths are read or printed, never a list's contents

- Slug: scan-fail-closed
- Touches: skills, dev/toy
- ETA: 290 active minutes (estimate 230m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given no list, an empty list, and a list with a planted hit in a toy, then the scan fails, passes and fails respectively, the missing-list line names the path, and each caller stops on the missing list (negative controls)
2. Given the pull request, then it cites o675, every row is SEEN RED, no list's contents appear in any output or commit, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, the full package.py on an export passes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
