# Plan: audit-pr-head

1. dev/toy/test-audit-pr-head.py (fix, stale) and dev/toy/test-new-binds.py (in, out), seen red first (done).
2. wiki.py `pending` audits the head's tree in a temporary worktree (+358 bytes, 19,024).
3. fit.py `bind_here`, called by goal.py new after FROZEN; trimmed goal.py comments and a fit.py note to stay under the cap (fit 20,461, goal 20,428).
4. Three defect rows (4208 x2, 4257), Tests tables re-rendered.

What could break: a leftover worktree (removed in a finally); bind refused outside the goal worktree (it prints the refusal; the goal stays frozen). Out of scope: reviewed wording, other callers of docs audit.
PENDING: none
