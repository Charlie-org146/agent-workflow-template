# roadmap-wiki design

## Problem
The owner wants the work left before v1.0.0 "printed to a wiki" so they can organize it. docs/ROADMAP.md is hand text from before the triage
(seven V1 items, no live status), and docs/triage-2026-11-14.md ranks seven groups of open work. Scope set by the owner: every open template
issue not on a Backlog milestone is cleared before v1.0.0; the Backlog-milestone issues wait for v1.1 and later ("after v1.0"); a rollout
(migrate-thermis, migrate-steward, migrate-portfolio, migrate-skillset, in parallel) follows v1.0.0; off-machine to-dos do not block.

## Approaches
1. **Hand-written wiki page.** Copy the triage tables into docs/wiki/Roadmap.md. Cheapest, but it goes stale the day an issue closes and the owner
   asked for something easy to regenerate.
2. **docs/ROADMAP.md is the hand source (issue or goal, outcome, blocks, per group); one command renders the page.** The command joins those rows with
   live facts: open issues (`gh issue list`), the run records and queue.md (in flight / queued), the Backlog milestones (the "after v1.0" list, no hand
   upkeep), the "To-do:" issues (off-machine), and the Unreviewed requirements read from the pages. A closed issue drops out. Cost: one gh call and a
   small parser; risk: the package cap is 99 files and every docs script sits near 20 KB, so the code cannot be a new file.

## Chosen: 2
The command is `batch.py roadmap [--live] [--out FILE]` in workflow-monitoring (batch.py has 13 KB of room and already reads queue.md and the run
records; its status/start commands are the same "what is queued, what runs" view). Without --live it prints the page and writes nothing; with --live
it also reads gh and writes docs/wiki/Roadmap.md. The page is a guide page (`<!-- workflow-docs guide -->`: mapped, kept fresh, no PRD contract, no
Home row) and is mapped in .loop/docs.tsv to docs/ROADMAP.md, so editing the hand source makes the page stale until it is rebuilt. docs.py publish
already publishes every mapped page and never overwrites one it did not write. Status per row: "in flight" when a running goal's slug is in the row or
the issue has an open PR from a running goal, "queued" when the slug is queued in queue.md, else "open". The Priority column is always empty.

## What each done line needs
1. docs/ROADMAP.md: seven group tables (size caps, Windows-safe, regression trust, open defects, adoption, Unreviewed requirements (generated),
   package rules), a Rollout section, nothing about Backlog (generated). Columns: Issue or goal | Outcome | Blocks | Status | Priority.
2. `batch.py roadmap`; Roadmap in .loop/docs.tsv; the page committed; docs.py check green; wiki publish lists Roadmap. SKILL.md and commands.md
   get the command; no reviewed page changes, so no owner words are needed.
3. dev/toy/test-roadmap.py on a fake gh and a fake run folder; one regression row per claim (closed drops out, status, Backlog apart, Priority empty,
   page matches a fresh render), each seen red.

## Open questions
None for the owner. (If the owner later wants the roadmap as a numbered requirement, that is a Documentation page change and needs their words.)
