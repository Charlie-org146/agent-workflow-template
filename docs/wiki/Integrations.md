<!-- workflow-docs -->
# Integrations

How to use: [How-to-use-Integrations](How-to-use-Integrations)

Review: **Unreviewed** <!-- kept entry-committed-config@a2026667 -->

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
| [sync-not-connected](Tests#t-sync-not-connected) | requirement | INT-2 | Given an mcp source and no connector, when docs.py sync runs, then it prints not connected, writes nothing and exits 0. | PASS 2026-11-18 |
| [sync-first-adopts](Tests#t-sync-first-adopts) | requirement | INT-2 | Given an external PRD and no repo copy, when docs.py sync runs, then it adopts the source with a baseline and no delta. | PASS 2026-11-18 |
| [sync-repo-delta](Tests#t-sync-repo-delta) | requirement | INT-2 | Given a requirement an agent changed in the repo copy, when docs.py sync runs, then it prints a DELTA naming the page, the id, the repo as the side and both texts. | PASS 2026-11-18 |
| [sync-source-delta](Tests#t-sync-source-delta) | requirement | INT-2 | Given a requirement people changed in the external document, when docs.py sync runs, then it prints a DELTA naming the source as the side and both texts. | PASS 2026-11-18 |
| [sync-both-sides](Tests#t-sync-both-sides) | requirement | INT-2 | Given a requirement changed in the repo and in the document, when docs.py sync runs, then it is a CONFLICT naming both texts. | PASS 2026-11-18 |
| [sync-dry-run-drift](Tests#t-sync-dry-run-drift) | requirement | INT-2 | Given a delta, when docs.py sync --dry-run runs, then it prints the DELTA, exits 1 and posts and writes nothing. | PASS 2026-11-18 |
| [sync-delta-no-overwrite](Tests#t-sync-delta-no-overwrite) | requirement | INT-2 | Given a delta, when docs.py sync runs, then the repo copy and the external document are both unchanged. | not run |
| [sync-owns-only](Tests#t-sync-owns-only) | requirement | INT-2 | Given a hand-written file where the repo copy goes, when docs.py sync runs, then it is SKIPPED and left as it was. | not run |
| [sync-delta-posted](Tests#t-sync-delta-posted) | requirement | INT-2 | Given a new delta on a page whose backlog milestone is Backlog: <page>, when docs.py sync runs, then it posts one GitHub issue on that milestone (created first if missing, never the bare page name, even when that milestone exists) and one comment on the external page. | not run |
| [sync-posts-once](Tests#t-sync-posts-once) | requirement | INT-2 | Given a delta already posted, when docs.py sync runs again, then it posts nothing more. | not run |
| [sync-accept-source](Tests#t-sync-accept-source) | requirement | INT-2 | Given a delta, when docs.py sync --accept PAGE:ID=source runs, then the source's text is written to the repo copy for that id only and the issue is closed. | not run |
| [sync-accept-repo](Tests#t-sync-accept-repo) | requirement | INT-2 | Given a delta, when docs.py sync --accept PAGE:ID=repo runs, then the repo's text is written to the external document through the writer for that id only and the issue is closed. | not run |
| [sync-agree-after-accept](Tests#t-sync-agree-after-accept) | requirement | INT-2 | Given every delta accepted, when docs.py sync runs, then the sides are in step and no delta is open. | not run |
| [sync-open-lists](Tests#t-sync-open-lists) | requirement | INT-2 | Given an open delta, when docs.py sync --open runs, then it lists the delta with no call to gh or the connector. | not run |
| [sync-health-delta](Tests#t-sync-health-delta) | requirement | INT-2 | Given an open delta, when health checks the docs, then it reports a FAIL row of the docs rule for it. | not run |
| [sync-board-delta](Tests#t-sync-board-delta) | requirement | INT-2 | Given an open delta, when the check-in's board is built, then it lists the delta as waiting on the owner. | not run |
| [sync-no-writer-posted](Tests#t-sync-no-writer-posted) | requirement | INT-2 | Given no writer, when docs.py sync finds a delta, then the issue is posted and the comment says not connected. | not run |
| [sync-accept-no-writer](Tests#t-sync-accept-no-writer) | requirement | INT-2 | Given no writer, when docs.py sync --accept PAGE:ID=repo runs, then it says not connected, exits 0 and changes nothing. | not run |
| [sync-no-gh](Tests#t-sync-no-gh) | requirement | INT-2 | Given gh that fails, when docs.py sync finds a delta, then it shows the delta, says not connected and exits 0. | not run |
| [milestone-sync-no-source](Tests#t-milestone-sync-no-source) | requirement | INT-2 | Given a repo with no milestones_source, when docs.py sync runs, then it prints nothing about milestones and calls neither gh, the reader nor the writer. | not run |
| [milestone-sync-repo-delta](Tests#t-milestone-sync-repo-delta) | requirement | INT-2 | Given a milestone changed only on GitHub, when docs.py sync runs, then it prints a DELTA naming the title, the repo as the side and both texts. | not run |
| [milestone-sync-source-delta](Tests#t-milestone-sync-source-delta) | requirement | INT-2 | Given a milestone changed only on the external Milestones page, when docs.py sync runs, then it prints a DELTA naming the source as the side and posts it as an issue. | not run |
| [milestone-sync-conflict](Tests#t-milestone-sync-conflict) | requirement | INT-2 | Given a milestone changed on GitHub and on the page, when docs.py sync runs, then it prints a CONFLICT and overwrites neither side. | not run |
| [milestone-sync-no-overwrite](Tests#t-milestone-sync-no-overwrite) | requirement | INT-2 | Given a milestone delta, when docs.py sync runs, then GitHub and the page are both unchanged. | not run |
| [milestone-sync-accept-source](Tests#t-milestone-sync-accept-source) | requirement | INT-2 | Given a delta, when docs.py sync --accept milestones:TITLE=source runs, then only that GitHub milestone is edited, by its number, and its issue is closed. | not run |
| [milestone-sync-accept-repo](Tests#t-milestone-sync-accept-repo) | requirement | INT-2 | Given a delta, when docs.py sync --accept milestones:TITLE=repo runs, then only that milestone is written to the page through the writer and its issue is closed. | not run |
| [milestone-sync-not-connected](Tests#t-milestone-sync-not-connected) | requirement | INT-2 | Given gh that cannot be reached, when docs.py sync runs with a milestones_source, then it prints not connected, changes nothing and exits 0. | not run |
| [milestone-sync-generic](Tests#t-milestone-sync-generic) | requirement | INT-2 | Given the template's milestone sync code, when it is searched, then it names no page link and no page id: only the opted-in repo's config does. | not run |
| [milestone-sync-reopen](Tests#t-milestone-sync-reopen) | requirement | INT-2 | Given a closed milestone missing from the page that GitHub then reopens, when docs.py sync runs, then it is a DELTA from the repo alone, never a conflict. | not run |
| [milestone-sync-dropped-source](Tests#t-milestone-sync-dropped-source) | requirement | INT-2 | Given a repo that dropped its milestones_source, when docs.py sync --open runs, then it lists none of its old milestone deltas. | not run |
| [milestone-sync-accept-fails](Tests#t-milestone-sync-accept-fails) | requirement | INT-2 | Given GitHub refusing a write, when docs.py sync --accept milestones:TITLE=source runs, then it prints not connected and accepts nothing. | not run |
| [prd-copy-normalised](Tests#t-prd-copy-normalised) | requirement | INT-2 | Given an external PRD that writes 'NL-1 Functional: (Reviewed date) text' and a 'New requirements' block, when docs.py sync adopts it, then the repo copy holds each requirement as an ordinary requirement line with its review mark. | not run |
| [prd-copy-no-reader](Tests#t-prd-copy-no-reader) | requirement | INT-2 | Given a page opted in to an external source with a copy in .loop/prd, when the docs check and audit run with no reader, then they pass with no UNREAD and no LINK. | not run |
| [prd-copy-block](Tests#t-prd-copy-block) | requirement | INT-2 | Given a page with a copy, when docs.py render runs, then the page shows Problem, Requirements, Non-goals and Success metrics as a block generated from the copy. | not run |
| [prd-copy-block-stale](Tests#t-prd-copy-block-stale) | requirement | INT-2 | Given a page whose generated PRD block was edited by hand, when the docs check runs, then it says STALE and names the copy. | not run |
| [prd-sync-source-add](Tests#t-prd-sync-source-add) | requirement | INT-2 | Given a requirement added in the external document, when docs.py sync runs, then it prints a DELTA naming the source and changes nothing until it is accepted. | not run |
| [prd-sync-repo-add](Tests#t-prd-sync-repo-add) | requirement | INT-2 | Given a requirement added in the repo copy, when docs.py sync runs, then it prints a DELTA naming the repo, and accepting it sends the text to the source through the writer. | not run |
| [prd-sync-conflict](Tests#t-prd-sync-conflict) | requirement | INT-2 | Given a requirement changed in the repo copy and in the external document, when docs.py sync runs, then it prints a CONFLICT naming both texts and overwrites neither side. | not run |
| [prd-sync-no-reader](Tests#t-prd-sync-no-reader) | requirement | INT-2 | Given a source no reader can reach, when docs.py sync runs, then it prints not connected, exits 0 and leaves the copy as it was. | not run |
| [prd-copy-no-source](Tests#t-prd-copy-no-source) | requirement | INT-2 | Given a page with no PRD source, when docs.py sync and render run, then the page is never visited, gets no block and raises no signal. | not run |
| [prd-copy-old-layout](Tests#t-prd-copy-old-layout) | requirement | INT-2 | Given a copy written before the repo's layout, when docs.py sync runs, then it skips the page naming the fix and leaves the copy as it was. | not run |
| [prd-copy-notion-shape](Tests#t-prd-copy-notion-shape) | requirement | INT-2 | Given an external PRD exported the way Notion writes it (html tags, a bold id over a first sub-bullet, the mark after the kind, a New requirements heading with a note), when docs.py sync adopts it, then the copy holds ordinary markdown requirement lines and none of its Source, Milestone, Review, Runbook or Deployments lines. | not run |
| - | requirement | INT-7 | no passing test | not enforced |
| [doc-nongoal-milestone-sync](Tests#t-doc-nongoal-milestone-sync) | defect | [#4546](https://github.com/jcl2018/agent-workflow-template/issues/4546) closed (2026-11-16) | Given the Documentation page, when INT-3 syncs milestones, then no Non-goals line leaves milestone sync for later. | not run |
