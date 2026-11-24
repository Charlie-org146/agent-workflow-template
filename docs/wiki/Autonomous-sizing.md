<!-- workflow-docs -->
# Autonomous sizing

Review: **Unreviewed**

How to use: [How-to-use-Autonomous-sizing](How-to-use-Autonomous-sizing)

## Problem

- Status: written, not built. Built by goal v110-cbs-asz. Reviewed approves the wording; availability is shown separately.
- Today a goal's size and its checks are argued over in messages, and they often wait for my word.
- The loop should pick them itself, say why, and only ask me when a safety class is involved.

## Requirements

### Functional

- ASZ-1: **Unreviewed** Autonomous sizing: the loop sizes each goal and picks its checks itself
  - Principle 8 (Autonomous). Page: docs/wiki/Autonomous-sizing.md.
  - ### Problem
  - Today a goal's size and its checks are argued over in messages, and they often wait for my word.
  - The loop should pick them itself, say why, and only ask me when a safety class is involved.
  - ### Requirements
  - ASZ-1.1 The loop sizes each goal at freeze from its plan: files touched, lines, gates, and whether it touches a safety class. It records the size with its reason and picks the checks from CBS-1's table. It doesn't wait for me. The size lines: small is 3 files or fewer, 150 lines or fewer, no gate and no safety class; medium is 10 files or fewer and no safety class; large is everything else.
  - **Metric.** Goals waiting for my word on their size or checks. Target 0.
  - **Test.** A new goal touching 2 files and no gate is sized small with its reason, and its checks start without a question to me.
  - ASZ-1.2 A goal's size only goes up on its own. If the build grows past its size, it's re-sized and the added checks run. It's never sized down mid-goal. A goal touching a safety class is always large.
  - **Metric.** Goals that grew past their size without a re-size. Target 0.
  - **Test.** A small goal whose diff passes the medium line is re-sized, and the medium checks run before its PR.
  - ASZ-1.3 The board shows each goal's size, reason and checks. One line from me changes a goal's size, and the change is logged with my words.
  - **Metric.** Size changes without a reason or my words. Target 0.
  - **Test.** My line sizes a goal up; the board shows the new size with my words, and the added checks run.
  - ### Non-goals
  - It doesn't set the table: that's CBS-1, and only my words change it.
  - It never sizes a safety-class goal below large.
  - ### Reference
  - adapted: change-risk scoring in release engineering (size from the diff, not a guess).
  - own: up-only re-sizing, and safety class means large.

### Non-functional

None

## Non-goals

- It doesn't set the table: that's CBS-1, and only my words change it.
- It never sizes a safety-class goal below large.

## Success metrics

- **Metric.** Goals waiting for my word on their size or checks. Target 0.
- **Metric.** Goals that grew past their size without a re-size. Target 0.
- **Metric.** Size changes without a reason or my words. Target 0.

## Revisions

None

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| - | requirement | ASZ-1 | no passing test | not enforced |
