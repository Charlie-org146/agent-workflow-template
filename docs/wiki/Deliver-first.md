<!-- workflow-docs -->
# Deliver first

Review: **Unreviewed**

How to use: [How-to-use-Deliver-first](How-to-use-Deliver-first)

## Problem

- Status: written, not built. Built by goal v110-dlf-1. Reviewed approves the wording; availability is shown separately.
- Time is money. On 11-22 to 11-23, every v1.1.0 goal was built and reviewed overnight, and none merged for about 14 hours. Each waited for my word on red-team breaks, review-cap approvals, minute budgets or test-row choices. Nearly all of them were process choices, and none of them loosened a check.
- This morning I turned on an interim deliver-first mode for Task 1 by hand (o889). It took 37 acceptances in one sitting. I want that to be the standing behaviour, without me typing it each time.

## Requirements

### Functional

- DLF-1: **Reviewed 2026-11-24** Deliver first: a goal never waits for me, unless it's a safety class <!-- reviewed 2069271e -->
  - Principle 8 (Autonomous and human-friendly), linked from principle 3 (Fast) · Topic: Build loop · Page: `docs/wiki/Deliver-first.md`
  - ### Problem
  - Time is money. On 11-22 to 11-23, every v1.1.0 goal was built and reviewed overnight, and none merged for about 14 hours. Each waited for my word on red-team breaks, review-cap approvals, minute budgets or test-row choices. Nearly all of them were process choices, and none of them loosened a check.
  - This morning I turned on an interim deliver-first mode for Task 1 by hand (o889). It took 37 acceptances in one sitting. I want that to be the standing behaviour, without me typing it each time.
  - ### Requirements
  - DLF-1.1 **A goal goes from plan to merge without waiting for me.** A red-team break, a plan past its review cap, a budget it has outgrown, a test failing outside the goal's own rows, or an open design choice does not stop it. Each one becomes a line on one tracked issue for the goal's release, with the exact words that settle it, and the goal moves on.
  - **Metric.** Minutes a goal spends waiting for my word on anything outside DLF-1.3. Target 0.
  - **Test.** A goal with three red-team breaks, a plan past its cap and a budget overrun merges on green, and its release has one issue listing all five, each with its settle line.
  - DLF-1.2 **Budgets raise themselves and say so.** When a goal reaches its time or token budget, the budget rises to measured spend plus the estimate of what's left, up to a cap of 2× the goal's estimate. Each raise is logged with the old and new figures. Past the cap, it asks me, as one line on the release issue, and keeps working at the cap meanwhile.
  - **Metric.** Goals stopped at a budget below the cap. Target 0.
  - **Test.** A goal at 240 of 240 minutes with 100 left goes to 340 without stopping, and the log shows both figures.
  - DLF-1.3 **Only safety waits.** These still stop a goal, and nothing else does:
  - the safety classes: deleting what can't be restored, money, security and sandbox settings, private data, steward merges;
  - a change to what a feature promises;
  - a test loosened or deleted;
  - the leak read before any push;
  - the PR's reached-test run before a merge.
  - Every other stop in the loop is removed or turned into DLF-1.1's issue line.
  - **Metric.** Goals merged past one of these. Target 0.
  - **Test.** A goal whose only break loosens a test does not merge, and the board names that as the reason.
  - DLF-1.4 **The release pays the debt.** A release can't be cut while its deliver-first issue has an open line. At the cut I get the whole list once, grouped by goal, each line with a recommendation, plus one line that accepts them all. A line I don't accept becomes a patch goal before the cut.
  - **Metric.** Releases cut with an open deliver-first line. Target 0. Separate questions to me about these lines before the cut. Target 0.
  - **Test.** Three goals merge with five open lines between them. The cut is refused, and I get one list of five plus one accept-all line.
  - DLF-1.5 **I can turn it off.** One setting, changed only by my words, turns deliver-first off for a goal, a task or a release. Then that scope waits for my word as today.
  - **Metric.** Changes to the setting without my words. Target 0.
  - **Test.** With it off for one goal, that goal's first break waits for me and the others don't.
  - ### Non-goals
  - It never skips the leak read, the PR's reached-test run before a merge, or a safety class.
  - It doesn't lower the bar for the release. It moves my review from each goal to the release, in one sitting.
  - It doesn't decide which checks are necessary; that's NCK-1.
  - ### Reference
  - adapted: trunk-based development (merge small changes early, keep what's owed visible).
  - adapted: technical debt registers (every shortcut recorded with its cost and paid before it compounds).
  - own: the release-level debt issue and the cut that refuses while it's open.

### Non-functional

None

## Non-goals

- It never skips the leak read, the PR's reached-test run before a merge, or a safety class.
- It doesn't lower the bar for the release. It moves my review from each goal to the release, in one sitting.
- It doesn't decide which checks are necessary; that's NCK-1.

## Success metrics

- **Metric.** Minutes a goal spends waiting for my word on anything outside DLF-1.3. Target 0.
- **Metric.** Goals merged past one of these. Target 0.
- **Metric.** Goals stopped at a budget below the cap. Target 0.

## Revisions

### DLF-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-24 | Deliver first: a goal never waits for me, unless it's a safety class <br> Principle 8 (Autonomous and human-friendly), linked from principle 3 (Fast) · Topic: Build loop · Page: `docs/wiki/Deliver-first.md` <br> ### Problem <br> Time is money. On 11-22 to 11-23, every v1.1.0 goal was built and reviewed overnight, and none merged for about 14 hours. Each waited for my word on red-team breaks, review-cap approvals, minute budgets or test-row choices. Nearly all of them were process choices, and none of them loosened a check. <br> This morning I turned on an interim deliver-first mode for Task 1 by hand (o889). It took 37 acceptances in one sitting. I want that to be the standing behaviour, without me typing it each time. <br> ### Requirements <br> DLF-1.1 **A goal goes from plan to merge without waiting for me.** A red-team break, a plan past its review cap, a budget it has outgrown, a test failing outside the goal's own rows, or an open design choice does not stop it. Each one becomes a line on one tracked issue for the goal's release, with the exact words that settle it, and the goal moves on. <br> **Metric.** Minutes a goal spends waiting for my word on anything outside DLF-1.3. Target 0. <br> **Test.** A goal with three red-team breaks, a plan past its cap and a budget overrun merges on green, and its release has one issue listing all five, each with its settle line. <br> DLF-1.2 **Budgets raise themselves and say so.** When a goal reaches its time or token budget, the budget rises to measured spend plus the estimate of what's left, up to a cap of 2× the goal's estimate. Each raise is logged with the old and new figures. Past the cap, it asks me, as one line on the release issue, and keeps working at the cap meanwhile. <br> **Metric.** Goals stopped at a budget below the cap. Target 0. <br> **Test.** A goal at 240 of 240 minutes with 100 left goes to 340 without stopping, and the log shows both figures. <br> DLF-1.3 **Only safety waits.** These still stop a goal, and nothing else does: <br> the safety classes: deleting what can't be restored, money, security and sandbox settings, private data, steward merges; <br> a change to what a feature promises; <br> a test loosened or deleted; <br> the leak read before any push; <br> the PR's reached-test run before a merge. <br> Every other stop in the loop is removed or turned into DLF-1.1's issue line. <br> **Metric.** Goals merged past one of these. Target 0. <br> **Test.** A goal whose only break loosens a test does not merge, and the board names that as the reason. <br> DLF-1.4 **The release pays the debt.** A release can't be cut while its deliver-first issue has an open line. At the cut I get the whole list once, grouped by goal, each line with a recommendation, plus one line that accepts them all. A line I don't accept becomes a patch goal before the cut. <br> **Metric.** Releases cut with an open deliver-first line. Target 0. Separate questions to me about these lines before the cut. Target 0. <br> **Test.** Three goals merge with five open lines between them. The cut is refused, and I get one list of five plus one accept-all line. <br> DLF-1.5 **I can turn it off.** One setting, changed only by my words, turns deliver-first off for a goal, a task or a release. Then that scope waits for my word as today. <br> **Metric.** Changes to the setting without my words. Target 0. <br> **Test.** With it off for one goal, that goal's first break waits for me and the others don't. <br> ### Non-goals <br> It never skips the leak read, the PR's reached-test run before a merge, or a safety class. <br> It doesn't lower the bar for the release. It moves my review from each goal to the release, in one sitting. <br> It doesn't decide which checks are necessary; that's NCK-1. <br> ### Reference <br> adapted: trunk-based development (merge small changes early, keep what's owed visible). <br> adapted: technical debt registers (every shortcut recorded with its cost and paid before it compounds). <br> own: the release-level debt issue and the cut that refuses while it's open. | migration r1; date from its stamp | o916: "Approve all three (Recommended)" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [dlf-lines-not-waits](Tests#t-dlf-lines-not-waits) | requirement | DLF-1 | DLF-1.1: Given three red-team breaks, a plan past its review cap, an open design choice and a budget past the cap, when the goal runs, then each becomes one line on the release's one issue with its settle words and the goal goes on. (not yet Given/When/Then) | not run |
| [dlf-budget-raises](Tests#t-dlf-budget-raises) | requirement | DLF-1 | DLF-1.2: Given a goal at 240 of 240 minutes with 100 left, when its budget is checked, then it rises to 340 without stopping, the log shows both figures, and past 2x the estimate it stays at the cap and files one line. (not yet Given/When/Then) | not run |
| [dlf-only-safety-waits](Tests#t-dlf-only-safety-waits) | requirement | DLF-1 | DLF-1.3: Given a break that loosens a test or touches a safety subject, when the stop table classifies it, then the goal waits and the board names the class, while every other stop becomes a line. (not yet Given/When/Then) | not run |
| [dlf-scan-every-path](Tests#t-dlf-scan-every-path) | requirement | DLF-1 | DLF-1.3: Given a planted private name in a line, an event, the cap line, a patch goal or the release issue body, when deliver-first writes it, then nothing is written outside the run record. (not yet Given/When/Then) | not run |
| [dlf-cut-refuses-open](Tests#t-dlf-cut-refuses-open) | requirement | DLF-1 | DLF-1.4: Given three goals with five open lines, when the release is cut, then it is refused with one list of five plus one accept-all line, and only the owner's comment accepts. (not yet Given/When/Then) | not run |
| [dlf-setting-off-waits](Tests#t-dlf-setting-off-waits) | requirement | DLF-1 | DLF-1.5: Given deliver-first off for one goal, when its first break arrives, then it waits for the owner and the other goals' breaks do not, and the setting changes only with an owner reference. (not yet Given/When/Then) | not run |
| [dlf-merge-on-green](Tests#t-dlf-merge-on-green) | requirement | DLF-1 | DLF-1.1: Given a goal with five open deliver-first lines on its release issue, when it is merged, then it merges on green and ends done and released; a goal that failed for another reason is still refused. (not yet Given/When/Then) | not run |
| - | requirement | DLF-1 | no passing test | not enforced |
