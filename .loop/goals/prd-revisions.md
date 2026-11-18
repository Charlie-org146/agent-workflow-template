# prd-revisions: PRD pages keep a revision history per requirement and are read-only while a goal builds (DOC-20, DOC-22; owner o30)

- Slug: prd-revisions
- Touches: not declared
- ETA: 265 active minutes (estimate 212m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a Reviewed requirement, when its text is changed through the docs tooling, then the page keeps the earlier text as a numbered revision with its date, reason and owner record, shows the current revision first, and only that requirement reads as awaiting review: no other requirement on the page loses its Reviewed stamp.
2. Given a requirement that is dropped, merged or moved, when the docs check runs, then its ID stays on its page marked Retired, merged into ID or moved to ID, and the check fails a page where an ID is deleted or reused.
3. Given a goal that is building, when its branch changes the text of a Reviewed requirement that no done line of the goal states, then the pull-request step refuses and names the requirement; a gap is instead filed as a finding that lands as an issue on the feature Backlog milestone naming the requirement.
4. Given the nine pages as they are on main, when the migration runs, then every requirement keeps its current text as its latest revision with nothing lost, the docs check prints DOCS OK, and each new rule has a regression test seen failing and passing, with zero rows added net.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Open docs/wiki/Documentation.md and find `## Revisions`, then `### DOC-1`.
   Expect: a table with rows r2 above r1, each with a date, a reason and `o30: "..."`, and the DOC-1 line above reads Unreviewed.
2. Run `python3 skills/workflow-docs/scripts/criteria.py revise DOC-4 --text "Home is one table, reworded" --why "try it" --owner-record o30 --goal prd-revisions --dry-run` is not offered; instead copy the repo to a scratch clone and run the same command without --dry-run.
   Expect: it prints `REVISED DOC-4 r1->r2 (now Unreviewed, awaits review)` and only DOC-4 changes.
3. In a scratch clone reword a Reviewed requirement in docs/wiki/Delivery.md without a done line, commit, and run `python3 skills/workflow-docs/scripts/criteria.py guard origin/main prd-revisions`.
   Expect: `GUARD REFUSED DEL-... (Delivery): text changed` with a worker fix and an owner fix, and exit status 1.
4. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: no REVISION or IDS line and no unmigrated NOTE (every page has its Revisions section).
