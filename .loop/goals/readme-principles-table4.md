# The template README keeps its title, the eight principles (owner's wording unchanged) and the Home link, and under each principle a table of every requirement that enforces it, each row with its own small flow diagram; the wiki Principles page carries the same tables; the README check follows the new shape; finished overnight and merged (owner 00:33-01:02; TOP-DECISIONs 81-83).

- Slug: readme-principles-table4
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. The README and docs/wiki/Principles.md cover every requirement on main, each under one best-fit principle (a few under two), plus a final Not yet covered table with a reason per row; columns Requirement (ID and title linked to its page), Feature, Release (version that introduced it, or v2.1 (planned)), Summary and Flow
2. Each row's Flow links its own 3-5 box SVG under docs/ (trigger, what the loop does, the check that proves it, the result, with the ID and title) that renders on GitHub in light and dark themes; the shipped package stays at 100 files
3. The README check in pageformat.py (from docs-readme-check) enforces the new shape with negative controls, docs, entry and wiki checks pass, DOC-23's next revision lands Unreviewed with its text sent to the operation for the owner, and net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
