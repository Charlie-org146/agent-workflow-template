# Design: requirements-consolidate

## Problem
161 requirements across the feature pages overlap and some conflict. The README's principles table names 43 consolidated requirements (the condensed set); the pages must match it.

## Decisions (owner, via operation-mac; TOP-DECISIONS 89 to 115, records o190 to o193 and later)
- Keep today's IDs. 43 survive; each surviving ID gets a new revision carrying everything it absorbs, tagged with the absorbed ID in brackets.
- Absorbed IDs are retired as `moved:SURVIVOR`; GRD-2 is cut; OPS-13 goes to OPS-1; DOC-23 goes to DOC-1. Revision history is kept, nothing is deleted, no ID is reused.
- Every regression row, test, How-to item, runbook and README reference is repointed to the survivor. Net rows stay at or below zero and no test is dropped.
- Planned work reads "(v2.0 planned)". HLT-2 also holds the principle checks and red-team bullets; OPS-1 holds the OPS-25 finding bullets.
- Wording approval is delegated to operation-top (DOC-2); safety classes still need the owner's words.

## Approach
A. Edit pages by hand: rejected, it breaks Reviewed seals and history.
B. Drive every change through `criteria.py revise|retire|review` with the owner record named for each ID, then repoint rows and re-render (chosen; minimal and keeps the append-only history).
C. Rewrite pages from condensed.json: rejected, it loses revision tables.

## Verification
`docs.py check` clean, `criteria.py guard` OK against main, `entry.py check` OK, the toys that read the pages pass or fail identically on the base, and the affected regression rows run in the qa lane.

## Risks
Main moves under the branch (merged three times; revision conflicts resolved as main's row plus ours renumbered). Four requirements (DOC-2, HLT-4, HLT-2, OPS-1) await operation-top's read before their Reviewed marks.
