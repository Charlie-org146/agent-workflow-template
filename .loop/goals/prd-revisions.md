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
