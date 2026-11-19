# The template README keeps its title, the eight principles (owner's wording unchanged) and the Home link, and under each principle a table of the requirements that enforce it (Requirement, Feature, Release, Summary, Flow); the wiki Principles page carries the same tables; DOC-23 and docs.py follow the new README shape. Fast-tracked by the owner (TOP-DECISION 77): pure documentation, merged directly, fixes later.

- Slug: readme-principles-table2
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The README and docs/wiki/Principles.md show, under each of the eight principles, a table with columns Requirement (ID and title linked to its page), Feature, Release (version that introduced it, or v2.1 (planned) for the queued v2.1 goals), Summary (one line) and Flow (the feature's How-to flow diagram); every cited requirement exists or is marked planned; the package stays at 100 files
2. The same PR updates docs.py's README check to the new shape, with a negative control, so docs check stays green on main; net regression rows are 0 or fewer
3. DOC-23's next revision describing the new README shape lands Unreviewed and its text is sent to the operation for the owner's review; the mapping table is sent to the operation (no pre-review wait); per-requirement diagrams and any mapping fixes are filed as v2.1 issues named in the PR

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
