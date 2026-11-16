# pr-queue-step design

## Problem
`pool.pr_order` drops the ticket of a goal whose run record is not at step checks or pr. A goal that asks for its pr turn can still
have `step: build` in its record (a silent worker; `pr_moved` sets build on a try lost to main moving), so each retry rejoins with a
later time and starves behind goals that reached pr after it (#4523).

## Approaches
1. `pool.pr_join(g, state)`: goal.py pr calls it before asking for its turn; a record not at checks or pr is set to pr and saved.
   Cost: one small function and one call. The drop rules stay as they are.
2. Make `pr_order` read the goal's flow instead. Rejected: it changes the drop rules, and goal.py would overwrite the record's step
   with its in-memory copy on its next save anyway.

## Chosen
Approach 1.

## What each done line needs
1. `goal.py pr` joins at pr, so A (record at build) stays first and B waits behind it in pr_order and pr_turn.
2. `dev/toy/test-pr-queue-step.py` covers A and B, with two negative controls: no join drops A's ticket; a merged goal's ticket is dropped.

## Open questions
None.
