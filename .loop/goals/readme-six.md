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
1. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: `DOCS OK: 16 pages` and no FORMAT, LINK, HOWTO or STALE line.
2. Open README.md.
   Expect: What this is (DEL-19's text, then the harness-engineering paragraph), System design with two grids, six principle sections each with its sentence, a table (Requirement, Summary, Follows, Feature, Adoption, Confidence), an Adoption line and a How it works paragraph, then Requirements by feature.
3. Run `diff <(grep "^## " README.md) <(grep "^## " docs/wiki/Home.md)`.
   Expect: no output.

## Deviations from the approved draft

Each is small, owner-visible and was accepted by the operation session (TD379, TD395):

- `dev/system-design.py` (not shipped, so not a package change) now reads the principle names from the README headings and handles six principles; without it the two grids would ship the eight old principle labels. It is the one non-document change.
- The Feature column carries the area as main does ("Documentation (Docs)"), because the grids read it.
- The principle sentence is plain text under its heading, not a blockquote (DOC-23 compares the words).
- Adoption is computed by the render from the Follows tags (adopted 1, adapted or own 0), so it differs from the draft's hand-read numbers; Confidence is blank.
- Follows cells carry links around their own words and no wording change; the links not already on main: Google re:Work OKR guide, GitHub managing releases, Kubernetes ResourceQuota, Kanban WIP limits (atlassian.com), GitGuardian, Agensi (agensi.io), Google SRE incident command, ESLint max-lines.
- "What this is" is rendered from DEL-19's text, with the owner's harness-engineering paragraph after it.
- Principles page: one diagram per principle section (the existing 01, 02, 05, 06, 07 and 08 files).
- How-to pages: the items of folded requirements moved to their survivors' pages as "Also (was ID)", and Delivery and Automation keep one line each naming `machine.py backup`/`restore` and `setup.py desk`.

## Owner records used

Owner words "yes build it" (o514) through records o569 to o655: revise and review of 26 requirements (o569 to o594, o613 to o638 and the later o645 to o655 for OPS-1, DEL-17, OPS-16 and GRD-20), DOC-26 (o595), and 21 retirements (o596 to o612 and o639 to o642). Additions approved by the owner (OPS-1 delays and platform limits, DEL-17 queue at full use) or by operation-top under owner delegation (DOC-2, o486: OPS-1 machine log, OPS-16 memory, GRD-20 20,480).
