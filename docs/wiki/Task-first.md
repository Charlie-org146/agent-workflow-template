<!-- workflow-docs -->
# Task first

Review: **Unreviewed**

How to use: [How-to-use-Task-first](How-to-use-Task-first)

## Problem

- Status: written, not built. Built by goal v110-tsk-1. Reviewed approves the wording; availability is shown separately.
- On 11-23, after fast-cut merged, the operation put four tool fixes in a row ahead of my Task 1 goals: a fix for main's red tests, a local test-run fix, a PR-tool README fix and a slow-row fix. Each was right on its own. Together, they pushed every fast goal from the afternoon into the evening, and I had to say "the original fast goals first" (o899) to turn it around.
- The default should be the other way round: my tasks are the work, and fixes to the loop's own tools serve them.

## Requirements

### Functional

- TSK-1: **Reviewed 2026-11-24** Task first: the operation schedules my tasks ahead of fixes to its own tools <!-- reviewed 7dd236aa -->
  - Principle 8 (Autonomous and human-friendly), linked from principle 3 (Fast) · Topic: Operations · Page: `docs/wiki/Task-first.md`
  - ### Problem
  - On 11-23, after fast-cut merged, the operation put four tool fixes in a row ahead of my Task 1 goals: a fix for main's red tests, a local test-run fix, a PR-tool README fix and a slow-row fix. Each was right on its own. Together, they pushed every fast goal from the afternoon into the evening, and I had to say "the original fast goals first" (o899) to turn it around.
  - The default should be the other way round: my tasks are the work, and fixes to the loop's own tools serve them.
  - ### Requirements
  - TSK-1.1 **The schedule puts my tasks first.** When the operation picks the next goal for a worker or the heavy slot, a goal from a task in my release brief comes before a fix, patch or tool goal, unless DLF-1.3's safety list says otherwise. Ties go by the brief's priority, then by the goal closest to merging.
  - **Metric.** Minutes a ready task goal waits behind a fix goal that doesn't block it. Target 0.
  - **Test.** With a ready task goal and a ready patch goal that doesn't block it, the slot goes to the task goal, and the record says why.
  - TSK-1.2 **A fix only goes first when it truly blocks.** A fix goal may go ahead of a task goal only when that task goal can't reach its merge without it, and there's no workaround the loop already has. The operation names the blocked goal and why no workaround fits. A fix that only makes things cleaner or faster waits.
  - **Metric.** Fix goals scheduled ahead of a task goal without a named blocked goal and reason. Target 0.
  - **Test.** A PR-tool bug that has a known per-goal workaround is queued after the task goals, and the task goals use the workaround meanwhile.
  - TSK-1.3 **A workaround is the default, and the fix follows.** When a tool bug hits a task goal, the operation uses a recorded workaround for that goal at once, opens one issue, and queues the real fix after the current task goals. The workaround never skips anything on DLF-1.3's list.
  - **Metric.** Task goals stopped by a tool bug that had a recorded workaround. Target 0.
  - **Test.** The second goal to hit the same tool bug uses the first goal's workaround without asking, and the fix stays queued behind it.
  - TSK-1.4 **A red main doesn't stop my tasks by itself.** When main's own test run is red only on rows that pass on PR runs, task goals keep merging on their own green PR runs with no new reds. A red that reaches PR runs or a safety class still stops merges.
  - **Metric.** Task merges held by a red main whose red rows pass on PR runs. Target 0.
  - **Test.** Main is red on one row that passes on PR runs; a task goal with a green PR run and no new red merges.
  - TSK-1.5 **I can see and change the order.** The board shows the schedule in order, each goal marked task or fix, with the reason any fix is ahead of a task. One line from me reorders it.
  - **Metric.** Fix goals ahead of task goals with no reason shown. Target 0.
  - **Test.** The board shows a fix ahead of a task goal with its blocked-goal reason, and my reorder line moves it back.
  - ### Non-goals
  - It never delays a fix to a safety class, a leak or a loosened test; those are DLF-1.3's list and go first.
  - It doesn't decide what's a task and what's a fix: the release brief names the tasks, and everything else is a fix.
  - ### Reference
  - adapted: Kanban classes of service (expedite only true blockers; standard work flows first).
  - adapted: SRE error budgets (reliability work preempts feature work only past a set line).
  - own: the task-first schedule with a named blocked goal for every fix that jumps the queue.

### Non-functional

None

## Non-goals

- It never delays a fix to a safety class, a leak or a loosened test; those are DLF-1.3's list and go first.
- It doesn't decide what's a task and what's a fix: the release brief names the tasks, and everything else is a fix.

## Success metrics

- **Metric.** Minutes a ready task goal waits behind a fix goal that doesn't block it. Target 0.
- **Metric.** Fix goals scheduled ahead of a task goal without a named blocked goal and reason. Target 0.
- **Metric.** Task goals stopped by a tool bug that had a recorded workaround. Target 0.

## Revisions

### TSK-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-24 | Task first: the operation schedules my tasks ahead of fixes to its own tools <br> Principle 8 (Autonomous and human-friendly), linked from principle 3 (Fast) · Topic: Operations · Page: `docs/wiki/Task-first.md` <br> ### Problem <br> On 11-23, after fast-cut merged, the operation put four tool fixes in a row ahead of my Task 1 goals: a fix for main's red tests, a local test-run fix, a PR-tool README fix and a slow-row fix. Each was right on its own. Together, they pushed every fast goal from the afternoon into the evening, and I had to say "the original fast goals first" (o899) to turn it around. <br> The default should be the other way round: my tasks are the work, and fixes to the loop's own tools serve them. <br> ### Requirements <br> TSK-1.1 **The schedule puts my tasks first.** When the operation picks the next goal for a worker or the heavy slot, a goal from a task in my release brief comes before a fix, patch or tool goal, unless DLF-1.3's safety list says otherwise. Ties go by the brief's priority, then by the goal closest to merging. <br> **Metric.** Minutes a ready task goal waits behind a fix goal that doesn't block it. Target 0. <br> **Test.** With a ready task goal and a ready patch goal that doesn't block it, the slot goes to the task goal, and the record says why. <br> TSK-1.2 **A fix only goes first when it truly blocks.** A fix goal may go ahead of a task goal only when that task goal can't reach its merge without it, and there's no workaround the loop already has. The operation names the blocked goal and why no workaround fits. A fix that only makes things cleaner or faster waits. <br> **Metric.** Fix goals scheduled ahead of a task goal without a named blocked goal and reason. Target 0. <br> **Test.** A PR-tool bug that has a known per-goal workaround is queued after the task goals, and the task goals use the workaround meanwhile. <br> TSK-1.3 **A workaround is the default, and the fix follows.** When a tool bug hits a task goal, the operation uses a recorded workaround for that goal at once, opens one issue, and queues the real fix after the current task goals. The workaround never skips anything on DLF-1.3's list. <br> **Metric.** Task goals stopped by a tool bug that had a recorded workaround. Target 0. <br> **Test.** The second goal to hit the same tool bug uses the first goal's workaround without asking, and the fix stays queued behind it. <br> TSK-1.4 **A red main doesn't stop my tasks by itself.** When main's own test run is red only on rows that pass on PR runs, task goals keep merging on their own green PR runs with no new reds. A red that reaches PR runs or a safety class still stops merges. <br> **Metric.** Task merges held by a red main whose red rows pass on PR runs. Target 0. <br> **Test.** Main is red on one row that passes on PR runs; a task goal with a green PR run and no new red merges. <br> TSK-1.5 **I can see and change the order.** The board shows the schedule in order, each goal marked task or fix, with the reason any fix is ahead of a task. One line from me reorders it. <br> **Metric.** Fix goals ahead of task goals with no reason shown. Target 0. <br> **Test.** The board shows a fix ahead of a task goal with its blocked-goal reason, and my reorder line moves it back. <br> ### Non-goals <br> It never delays a fix to a safety class, a leak or a loosened test; those are DLF-1.3's list and go first. <br> It doesn't decide what's a task and what's a fix: the release brief names the tasks, and everything else is a fix. <br> ### Reference <br> adapted: Kanban classes of service (expedite only true blockers; standard work flows first). <br> adapted: SRE error budgets (reliability work preempts feature work only past a set line). <br> own: the task-first schedule with a named blocked goal for every fix that jumps the queue. | migration r1; date from its stamp | o916: "Approve all three (Recommended)" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| - | requirement | TSK-1 | no passing test | not enforced |
