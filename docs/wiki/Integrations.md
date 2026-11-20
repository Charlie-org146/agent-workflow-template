<!-- workflow-docs -->
# Integrations

How to use: [How-to-use-Integrations](How-to-use-Integrations)

Review: **Unreviewed** <!-- kept merge-queue-ci@2b2c3a54a -->

## Problem
- The loop works with systems outside the repo, such as documents, trackers, mail, chat, agents and deploy targets, and each one is wired in its own way, so a new system means rebuilding something.
- A system outside the repo can break a check or silently change the repo's text, and I can't tell from one place which systems are connected or differ.
- I need one contract so a new system plugs in without rebuilding anything, and nothing outside can break or silently change the repo.

## Requirements

### Functional
- INT-1: **Reviewed 2026-11-19** Every integration is a declared, visible adapter <!-- reviewed debd1c31 -->
  - Anything outside the repo that the loop works with, a document, a tracker, a mailbox, a chat, an agent or a deploy target, is an integration declared in one registry: what it carries, which way it flows, where its secrets live and the health rule that proves it is connected. It is opt-in per repo or page. [INT-1]
  - Adding a system means one reader or writer, one registry row and one How-to page. No loop code changes, and an adopted repo gets it by declaring it, not by building it. [INT-6]
  - The board shows each integration's connection state and its open deltas as waiting on me, with the words to accept either side, and health counts an open delta or an unreadable integration as a finding, never as passing. [INT-5]
- INT-2: **Reviewed 2026-11-19** Integrations never override the repo copy <!-- reviewed 93df798f -->
  - Every check, test and publish reads the repo's own copy and never the outside system. An integration that can't be reached says not connected, changes nothing and never breaks the loop. [INT-2]
  - Where both sides can change the same thing, sync compares them with what they last agreed on. Each difference is a delta naming what changed and on which side, and it stays open until someone accepts one side's text. It is posted on the feature's Backlog milestone. [INT-3]
  - A repo can keep its GitHub milestones in step with an outside Milestones page under this contract, opt-in by one setting. [INT-8]
- INT-7: **Reviewed 2026-11-19** PRDs may sync with an outside document <!-- reviewed 0fced196 -->
  - A PRD lives in the repo by default. A page can opt in to keep step with an outside document, in Notion or behind a link, under this contract; the repo's copy stays the one every check reads. [INT-7]

### Non-functional

None

## Non-goals
- GitHub is the one system the loop assumes, so it is not an integration under this contract.
- The mail digest, connector checks, agent profiles and deploy targets keep their own requirements (Automation, Setup, Delivery and Documentation); this page does not restate them.
- No connector is attached for me: I attach each one with the narrowest access.

## Success metrics
- An integration that can't be reached prints not connected and changes nothing, and every check, test and publish still ends the same way.
- Adding a system takes one reader or writer, one registry row and one How-to page, with no change to the loop's code.
- Every open delta and every unreadable integration shows on the board and in health as waiting on me, never as passing.

## Revisions

### Retired

- INT-3: moved to INT-2
- INT-4: moved to GRD-5
- INT-5: moved to INT-1
- INT-6: moved to INT-1
- INT-8: moved to INT-2

### INT-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Every integration is a declared, visible adapter <br> Anything outside the repo that the loop works with, a document, a tracker, a mailbox, a chat, an agent or a deploy target, is an integration declared in one registry: what it carries, which way it flows, where its secrets live and the health rule that proves it is connected. It is opt-in per repo or page. [INT-1] <br> Adding a system means one reader or writer, one registry row and one How-to page. No loop code changes, and an adopted repo gets it by declaring it, not by building it. [INT-6] <br> The board shows each integration's connection state and its open deltas as waiting on me, with the words to accept either side, and health counts an open delta or an unreadable integration as a finding, never as passing. [INT-5] | consolidation (TOP-DECISION 89) | o313: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | One contract for every integration <br> Anything outside the repo that the loop works with, a document, a tracker, a mailbox, a chat, an agent or a deploy target, is an integration declared in one registry: what it carries, which way it flows, where its secrets live and the health rule that proves it is connected. It is opt-in per repo or page. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Integrations never override the repo copy <br> Every check, test and publish reads the repo's own copy and never the outside system. An integration that can't be reached says not connected, changes nothing and never breaks the loop. [INT-2] <br> Where both sides can change the same thing, sync compares them with what they last agreed on. Each difference is a delta naming what changed and on which side, and it stays open until someone accepts one side's text. It is posted on the feature's Backlog milestone. [INT-3] <br> A repo can keep its GitHub milestones in step with an outside Milestones page under this contract, opt-in by one setting. [INT-8] | consolidation (TOP-DECISION 89) | o264: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | The repo stays the source of truth <br> Every check, test and publish reads the repo's own copy and never the outside system. An integration that can't be reached says not connected, changes nothing and never breaks the loop. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A difference is a delta, never a silent overwrite <br> Where both sides can change the same thing, sync compares them with what they last agreed on. Each difference is a delta naming what changed and on which side, and it stays open until someone accepts one side's text. It is posted on the feature's Backlog milestone. | consolidation (TOP-DECISION 89): absorbed into INT-2 | o265: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A difference is a delta, never a silent overwrite <br> Where both sides can change the same thing, sync compares them with what they last agreed on. Each difference is a delta naming what changed and on which side, and it stays open until someone accepts one side's text. It is posted on the feature's Backlog milestone. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Nothing leaves without my say <br> An integration reads by default. It writes outside only behind an explicit switch and, for shared text, an accepted delta. I attach each connector myself with the narrowest access, and its secrets live outside the repo. | consolidation (TOP-DECISION 89): absorbed into GRD-5 | o296: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Nothing leaves without my say <br> An integration reads by default. It writes outside only behind an explicit switch and, for shared text, an accepted delta. I attach each connector myself with the narrowest access, and its secrets live outside the repo. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Every integration is visible <br> The board shows each integration's connection state and its open deltas as waiting on me, with the words to accept either side, and health counts an open delta or an unreadable integration as a finding, never as passing. | consolidation (TOP-DECISION 89): absorbed into INT-1 | o314: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Every integration is visible <br> The board shows each integration's connection state and its open deltas as waiting on me, with the words to accept either side, and health counts an open delta or an unreadable integration as a finding, never as passing. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | A new system is an adapter, not a rewrite <br> Adding a system means one reader or writer, one registry row and one How-to page. No loop code changes, and an adopted repo gets it by declaring it, not by building it. | consolidation (TOP-DECISION 89): absorbed into INT-1 | o315: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | A new system is an adapter, not a rewrite <br> Adding a system means one reader or writer, one registry row and one How-to page. No loop code changes, and an adopted repo gets it by declaring it, not by building it. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | PRDs may sync with an outside document <br> A PRD lives in the repo by default. A page can opt in to keep step with an outside document, in Notion or behind a link, under this contract; the repo's copy stays the one every check reads. [INT-7] | consolidation (TOP-DECISION 89) | o200: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | PRDs kept in an outside document <br> A PRD lives in the repo by default. A page can opt in to keep step with an outside document, in Notion or behind a link, under this contract; the repo's copy stays the one every check reads. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

### INT-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-19 | Milestones kept in step with an outside page <br> A repo can keep its GitHub milestones in step with an outside Milestones page under this contract, opt-in by one setting. | consolidation (TOP-DECISION 89): absorbed into INT-2 | o266: "consolidate the requirements ... absorb some requirements into the existing one requirement," |
| r1 | 2026-11-18 | Milestones kept in step with an outside page <br> A repo can keep its GitHub milestones in step with an outside Milestones page under this contract, opt-in by one setting. | migration r1; date from the run day | o155: "start regroup 3 and 4" |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| - | requirement | INT-1 | no passing test | not enforced |
| [sync-not-connected](Tests#t-sync-not-connected) | requirement | INT-2 | Given the INT-2 cases of test-docs-sync.py, when it runs once, then it prints every PASS line the 15 merged rows checked and no FAIL line. | PASS 2026-11-20 |
| [sync-delta-posted](Tests#t-sync-delta-posted) | requirement | INT-2 | Given a new delta on a page whose backlog milestone is Backlog: <page>, when docs.py sync runs, then it posts one GitHub issue on that milestone (created first if missing, never the bare page name, even when that milestone exists) and one comment on the external page. | not run |
| [sync-health-delta](Tests#t-sync-health-delta) | requirement | INT-2 | Given an open delta, when health checks the docs, then it reports a FAIL row of the docs rule for it. | not run |
| [sync-board-delta](Tests#t-sync-board-delta) | requirement | INT-2 | Given an open delta, when the check-in's board is built, then it lists the delta as waiting on the owner. | not run |
| [sync-no-gh](Tests#t-sync-no-gh) | requirement | INT-2 | Given gh that fails, when docs.py sync finds a delta, then it shows the delta, says not connected and exits 0. | not run |
| [milestone-sync-no-source](Tests#t-milestone-sync-no-source) | requirement | INT-2 | Given the INT-2 cases of test-milestone-sync.py, when it runs once, then it prints every PASS line the 12 merged rows checked and no FAIL line. | PASS 2026-11-20 |
| [prd-copy-no-reader](Tests#t-prd-copy-no-reader) | requirement | INT-2 | Given the INT-2 cases of test-prd-copy.sh, when it runs once, then it prints every PASS line the 9 merged rows checked and no FAIL line. | PASS 2026-11-20 |
| [prd-sync-no-reader](Tests#t-prd-sync-no-reader) | requirement | INT-2 | Given a source no reader can reach, when docs.py sync runs, then it prints not connected, exits 0 and leaves the copy as it was. | not run |
| [prd-copy-no-source](Tests#t-prd-copy-no-source) | requirement | INT-2 | Given a page with no PRD source, when docs.py sync and render run, then the page is never visited, gets no block and raises no signal. | not run |
| - | requirement | INT-7 | no passing test | not enforced |
| [doc-nongoal-milestone-sync](Tests#t-doc-nongoal-milestone-sync) | defect | [#4546](https://github.com/jcl2018/agent-workflow-template/issues/4546) closed (2026-11-16) | Given the Documentation page, when INT-3 syncs milestones, then no Non-goals line leaves milestone sync for later. | not run |
