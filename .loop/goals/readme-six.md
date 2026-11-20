# README.md, docs/wiki/Home.md and the wiki pages are rewritten to the owner-approved final README (owner words o514 "yes build it", about 03:31 on 2026-11-20, answering whether README-final-draft.md is a yes): six principles, 27 requirements, What this is, the Adoption and Confidence columns and the six gap-fills at its end. The source of truth is operation-top/readme-drafts/README-final-draft.md in the operation-top worktree; its requirement wording is the owner's (DOC-2) and is used exactly: if any text cannot be built as written (a docs-check rule, a page shape, a LOCKED requirement), the worker stops and reports it and does not reword. Requirements whose text is rewritten are marked Reviewed on owner record o514; folded requirements are marked absorbed with their pages repointed; the Adoption column carries the draft's values and Confidence is left blank for the health goal to fill. The sentence of each principle also goes into skills/workflow-health/references/commands.md so the docs check's sentence rule passes. Documents only: no script, test, workflow, setting or regression row changes. It touches the Tests pages, so before its push it merges the rows-600-a branch (or main once that has landed) and re-renders

- Slug: readme-six
- Touches: README.md, docs/wiki, skills/workflow-health/references/commands.md
- ETA: 425 active minutes (estimate 338m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given README.md, docs/wiki/Home.md and docs/wiki/Principles.md, then they state the six principles and 27 requirements exactly as README-final-draft.md does, with What this is, the Adoption values and a blank Confidence column, and the docs check passes
2. Given every requirement the draft rewrites, folds or adds, then its page carries the draft's text, rewritten ones are Reviewed on owner record o514 with a Revisions row, folded ones are marked absorbed with every reference repointed, and no ID or link is left dangling
3. Given this goal's diff, then only documents (README, docs/wiki, the health commands reference and the goal's own records) change, no script, test, workflow, setting or regression row changes, and any text the draft could not express as written is listed in the pull request instead of being reworded

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
