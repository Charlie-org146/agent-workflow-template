# The template README keeps its title, the eight principles (owner's wording unchanged) and the Home link, and under each principle a table of the requirements that enforce it (Requirement, Feature, Release, Summary, Flow); the wiki Principles page carries the same tables; DOC-23 and docs.py follow the new README shape.

- Slug: readme-principles-table
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A full principle-to-requirement mapping table (every cited requirement exists on a feature page, or is marked v2.1 (planned) for release-readiness, release-eta, merge-queue, ops-findings, plan-red-team or develop-staging) is sent to the operation for operation-top's review before any diagram is made
2. The README and docs/wiki/Principles.md show, under each of the eight principles, a table with columns Requirement (ID and title linked to its page), Feature, Release (version that introduced it), Summary (one line) and Flow (a small diagram per row, or the feature's How-to flow diagram with per-requirement diagrams filed as a v2.1 issue named in the PR); diagrams live under docs/ and the package stays at 100 files
3. A drafted DOC-23 next revision describing the new README shape is sent to the operation for the owner, applied only after the owner approves it; docs.py check enforces the approved shape with a negative control; net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
