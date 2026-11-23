# v110-fast-ci-2: the Mac's full-depth plan review (at 23fb088de)

Relayed by operation-pc from operation-mac, who ran it with the CEO, devex and eng review skills loaded. The full text is operation-mac's scratchpad file review-fast-ci-2.md; this page keeps the verdicts and the findings as relayed.

Verdicts: CEO CONDITIONAL, devex CONDITIONAL, eng BLOCKED.

BREAK C1 (against done line 2): the plan built only the queue path and left the PR path "as today (fast-cut's)". Taken: the plan now names the dependency on v110-fast-cut for the PR-path clauses and asks top whether line 2 may lean on it.
BREAK E1 (against "never fewer"): the key covers the import closure; a control checks it. Taken.
E2: queue-cache writes the result cache from main's copy of ci_plan. Taken.
HIGH C2: done line 3 cannot be proven before the merge; the 110 job-minutes figure needs a source. Taken.
MEDIUM E3 which workflow file merge_group runs (settled by the first real run after the merge); E4 `gh pr merge --auto --match-head-commit` with a queue may be refused (GraphQL fallback with expectedHeadOid); E5 18 jobs per queue run beside 9 per PR with no concurrency figure; E6 required-check names must be exact; E7 settings.py is at 20,028 bytes and the ci_limits line grows it. Taken.
C3: ci_limits code push-to-main is 35 (o751), and DEL-27.4's 10 minutes is the queue-to-main number: kept apart (`queue_to_main`, `pr_to_queue`). Taken.
DX: the gate prints the reproduce command, the log path and a stable code; queue-enter OFF prints one line and the docs give `gh variable set QUEUE_ENTER --body true` plus the ruleset precondition; each arming refusal has its own message. LOW: spike ci_plan.py's size; the clock failure line prints the limit and the setting name. Taken.

Verified true by the review: regression-pr.yml's shape, affected's row-times save, the byte sizes, config's merge_queue false, max_regression_rows 1300, and the repository is public.

Note on the earlier plan record: the first plan record said depth full, but the review behind it was three independent read-only agent passes (feasibility, security, scope), not the three review skills. This record, made with `plan --again` after the Mac's full-depth review is attached, replaces it.
