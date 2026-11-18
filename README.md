# agent-workflow-template

<!-- template:begin -->
Built with the [jcl2018/agent-workflow-template](https://github.com/jcl2018/agent-workflow-template) workflow loop.
<!-- template:end -->

[The wiki](https://github.com/jcl2018/agent-workflow-template/wiki/Home) has the features, how to use each one, the settings and what runs by itself.

## 1. Documentation-driven

Nothing is built that a Reviewed requirement doesn't ask for, and the PRD changes only by your words.

![Documentation-driven](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-01-documentation-driven.svg)

Enforced by: DOC-2, DOC-20, DOC-22, DEL-2, DEL-18 (planned: regroup 2), DEL-19 (planned: regroup 2), REG-1

## 2. The loop and coverage

Every requirement is enforced and proven, and whatever falls short, conflicts or has no owner becomes work until it is fixed or the PRD is revised.

![The loop and coverage](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-02-the-loop-and-coverage.svg)

Enforced by: REG-1, REG-6, REG-9, REG-10, REG-15 (planned: regroup 3), REG-16 (planned: regroup 3), DOC-3, HLT-4, HLT-6, HLT-12 (planned: regroup 4), GRD-9, DEL-14

## 3. The docs are true

The pages agree with each other and with the code: one ID, one name for each command, and no two requirements that contradict.

![The docs are true](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-03-the-docs-are-true.svg)

Enforced by: DOC-1, DOC-6, DOC-12, DOC-13, DOC-20, DOC-21 (planned: regroup 3), HLT-5, HLT-13 (planned: regroup 4), REL-10 (planned: regroup 2), INT-2 (planned: regroup 3), INT-3 (planned: regroup 3)

## 4. Nothing stale or left over

The tests ran today, merged work is released, and no stale branch, idle session, old finding or question to you is left behind.

![Nothing stale or left over](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-04-nothing-stale-or-left-over.svg)

Enforced by: AUT-2, AUT-3, REG-4, REL-9 (planned: regroup 2), REL-1, REL-5, REL-6, REL-7, MON-6, MON-8, HLT-8, HLT-12 (planned: regroup 4), CHK-7 (planned: regroup 4)

## 5. Fast, cheap and small

Goals, tests and health stay inside their time and token limits, and scripts, pages and the package stay inside their size limits, including Agensi's.

![Fast, cheap and small](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-05-fast-cheap-and-small.svg)

Enforced by: GRD-2, GRD-7, GRD-8, GRD-19 (planned: regroup 4), GRD-20 (planned: regroup 4), GRD-21 (planned: regroup 4), GRD-22 (planned: regroup 4), DEL-17 (planned: regroup 2), REG-7, REG-11 (planned: regroup 3), REG-14 (planned: regroup 3), AUT-7, HLT-11 (planned: regroup 4), SET-3

## 6. Nothing private escapes

No private name, path, address or key leaves the machine, and automation gets only the access it needs.

![Nothing private escapes](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-06-nothing-private-escapes.svg)

Enforced by: GRD-3, GRD-4, GRD-5, GRD-16 (planned: regroup 4), AUT-6, AUT-9, INT-4 (planned: regroup 3), MCH-6 (planned: regroup 2)

## 7. It works installed fresh

A repo that adopts the template gets the same loop, checks and guardrails, with nothing rebuilt there.

![It works installed fresh](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-07-it-works-installed-fresh.svg)

Enforced by: SET-1, SET-6, SET-16, SET-21 (planned: regroup 2), GRD-10, MCH-1, MCH-2

## 8. It stops for you only when it must

It asks you only for what is yours to decide: anything destructive, costly or private, and any change to the PRD. Everything else it decides, tells you, and lets you reverse.

![It stops for you only when it must](https://raw.githubusercontent.com/jcl2018/agent-workflow-template/main/docs/wiki/principle-08-it-stops-for-you-only-when-it-must.svg)

Enforced by: DEL-3, DEL-17 (planned: regroup 2), MON-11, MON-18, MCH-3, REL-11 (planned: regroup 2), REL-8, DOC-2, CHK-7 (planned: regroup 4), CHK-9 (planned: regroup 4)
