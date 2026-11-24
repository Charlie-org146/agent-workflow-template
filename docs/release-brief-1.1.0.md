# v1.1.0 brief (minor, revision 4)

- What it's about: v1.1.0 implements the spec approved on 2026-11-24, as the 16 tasks of the plan.

## Tasks

1. Fast routine: deliver first, task first and checks by size (DELIVER, SIZE, FIRST, SAFETY; GOAL-2, GOAL-8, BUDGET-5, QUICK-3).
2. The spec is in: the 33 approved pages become the spec; old pages point at the new IDs; test rows keep their links; release on every merge turned off (FEAT, PRIN, RLS-1).
3. Side by side: memory lines on the Mac (MACHINE-5, MACHINE-6).
4. Quick checks (QUICK, SCAN, LIMIT, HEALTH-4, GOAL-9, GUARD-3).
5. On GitHub: goals, tasks and releases as issues and milestones (GOAL, TASK-1 to 5, RLS-2, RLS-3, FIND-1 to 4).
6. Settings (CONFIG).
7. Timed and costed (CLOCK, COST, BUDGET-1 to 4, MEANS, GOAL-6, GOAL-7).
8. Pull request tests and the queue (PRTEST, QUEUE).
9. Identity and guards (ACCESS, GUARD-1, GUARD-2, GUARD-4, FEAT-4).
10. Tests on pytest (TEST, FEAT-6).
11. Health, reviewer and red team (HEALTH, REVIEW, RED, FIND-5, PRIN-4 to 6, FEAT-7).
12. Board and questions (BOARD, ASK, OPER, TASK-6, TASK-7).
13. Machines and the package (MACHINE-1 to 4, PACK).
14. Adapters (ADAPT).
15. Adoption (ADOPT).
16. Staging, production and the cut (RLS-4 to 7).

- Work in flight: the deliver-first, task-first and checks-by-size goals are task 1's first goals; the quick-checks goal joins task 4 and the clock goal task 7; the rest of revision 2's tasks are done or carried as issues.
- Not in it: rewriting the 315 test scripts one by one.
- Done when: every requirement's tests pass on the reached-test run, the full set is green on main, and v1.1.0 is tagged through the cut (RLS-4).
Frozen: df28acaab5f014ccb646b8ce0abe364370112fc02592d2c29d6b138837cdaf78 o924 o928 2026-11-24
