# trim-scripts-98 plan

Checked: sizes by LF count (goal 19,128, role 19,425, lane 19,090, setup 19,108); dev/package.py counts 99 files; operation.md is
referenced by README, docs/ROADMAP, the monitoring SKILL.md, its commands.md, dev/toy/test-batch.sh and test-board.sh.

## Build steps
1. Simplify goal.py, role.py, lane.py, setup.py (no comment or text deletions; AST name check against main shows nothing new undefined).
2. Append operation.md to commands.md, delete it, repoint every link and the two toys.
3. Rows `trim-setup-under-19000` and `trim-package-98`, each seen red against a break that pads a script over the line.

## Test per done line
Done 1: the size rows. Done 2: `trim-package-98` and the board and batch text checks (the step-5 keys and governance phrases are in commands.md).

## What could break
A trim changing behavior (toys for not-runnable, pr-queue-step and the adoption proofs pass); the two bash toys skip on Windows.

## Out of scope
Other scripts near the line (checkin.py, pool.py, monitoring size rows).

PENDING: none
