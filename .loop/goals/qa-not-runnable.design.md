# qa-not-runnable design

## Problem
qa refuses to record a lane when the only failing rows are rows this machine cannot run (pnpm or node missing, a POSIX-only
import such as fcntl). GRD-11 says a step only another machine can do never blocks the goal (#4492).

## Approaches
1. Classify in `runs.execute`: a failing row whose exit is 127 or whose output says a tool or POSIX-only module is missing
   becomes a SKIPPED state marked `notrun`, printed `NOTRUN id`. The lane then exits 0 when nothing else fails; the lane line
   carries `N pass; M not runnable here`; goal.py record puts that in the step's note. One to-do per goal is filed live.
   Cost: one new small module (`notrun.py`). Risk: a real failure whose text matches the patterns is hidden.
2. Let the owner list unrunnable rows in a file. Rejected: manual, and the thermis case had 92 rows.

## Chosen
Approach 1. Patterns are narrow (exit 127, `command not found`, `No module named 'fcntl|termios|pwd|grp|resource'`, a Node
ENOENT spawn); anything else stays a failure.

## What each done line needs
1. `NOTRUN` apart from `FAIL` in `runs.execute`. 2. `regression.py run` exits 0 with only NOTRUN left, 1 with a real failure;
`role.lane_note` gives the note. 3. `notrun.todo`: one `other-machine` issue per goal on the rows' feature milestone.
A toy (`dev/toy/test-not-runnable.py`) proves all three with negative controls.

## Open questions
None for the owner.
