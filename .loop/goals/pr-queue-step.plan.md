# pr-queue-step plan

Checked: `pool.pr_order` (the drop rule), `pool.pr_turn`, `graph.pr_queue` (dispatches `pr_<op>`), and `goal.py` cmd_pr (calls `queue("turn", ...)`).

## Build steps
1. `pool.pr_join`; `goal.py pr` calls `queue("join", ME, state)` before `queue("turn", ...)`.
2. Toy `dev/toy/test-pr-queue-step.py`; rows `pr-queue-keeps-place`, `pr-queue-step-toy`, each seen red against a break that removes the join.

## Test per done line
The two rows. Done 1: A keeps first place; done 2: both negative controls.

## What could break
A goal that never reaches pr never calls the join, so it is still dropped when it is not at pr. pool.py 19.0 KB, goal.py 19.1 KB, under 20 KB.

## Out of scope
The drop rules, the heartbeat limit, why a worker stays silent.

PENDING: none
