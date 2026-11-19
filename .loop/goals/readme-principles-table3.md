# The template README keeps its title, the eight principles (owner's wording unchanged) and the Home link, and under each principle a table of the requirements that enforce it; the wiki Principles page carries the same tables. Shipped immediately on the owner's words (TOP-DECISIONs 77 and 78); the docs.py README check follows in docs-readme-check.

- Slug: readme-principles-table3
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The README and docs/wiki/Principles.md show, under each of the eight principles, a table with columns Requirement (ID and title linked to its page), Feature, Release (version that introduced it, or v2.1 (planned) for the queued v2.1 goals), Summary (one line) and Flow (the feature's How-to flow diagram); every cited requirement exists or is marked planned; the package stays at 100 files
2. DOC-23's next revision describing the new README shape lands Unreviewed and its text is sent to the operation for the owner's review; the mapping table is sent to the operation; per-requirement diagrams and mapping fixes are filed as v2.1 issues named in the PR
3. Only the docs and README check rows may fail on this PR's CI (accepted on the owner's 00:40 words); every other row is no worse than main; net regression rows are 0 or fewer; docs.py is not changed here

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
