# kr-lanes-2: design

## Problem
Six regression rows (guards-resume, lane-messages-table, lanes-trace-check, repo-narrow-178, st-union-contexts, toy-no-leftovers) fail on main and sit in the known-red list. Each fails for its own reason, in the product or in the toy. The goal clears them at their roots without weakening a check, and removes exactly their known lines. Two neighbouring reds (lanes-trace, #5693; the rerun fraction behind lanes-headers, #5694) are not fixed here: each needs a redesign, which the owner ruled to do before v2.0 in their own goals.

## Premises checked
1. The rows are red because of drift, not because the checks are wrong: every cause was traced to a commit or a missing line (a changed report record, a missing documentation row, a fixture that copied too few scripts, a workflow fixture without the job a check asks for, a renamed statement, a toy that sources its helper late, a regex that matched part of a folder name).
2. A fix that edits a toy must keep or tighten the assertion; a fix in the product must have its own proof. The pull request body states cause, fix and proof per row.
3. The two redesigns are out of scope because their causes are structural: a trace that cannot finish in its limit, and a closure mesh that sends nearly every script to the batch module.

## Approaches
A (chosen): fix each row at its root, one commit per cause, rerun each row alone twice, remove its known line, name the redesigns in the body. Effort small to medium, risk low.
B: widen the known list or raise limits: rejected, it hides the drift.
C: fold the redesigns into this goal: rejected, the owner ruled they get their own goals.

## Done means
Each of the six rows passes alone twice outside any sandbox, with the session variables unset; no assertion weakened; the six known lines removed and the two redesign lines unchanged; only the scripts, toys, rows and pages the fixes need change.
