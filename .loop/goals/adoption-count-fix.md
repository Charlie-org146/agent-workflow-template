# Fix the Adoption counter, not the README text (Operation TD531, TD569, after #5631): in skills/workflow-docs/scripts/sections.py, follows() and adoption() read one tag per Follows bullet, so a bullet that names two sources, each with its own tag (for example HLT-2, REG-4 and MCH-1 since #5631: '[A](url): adapted; [B](url): adopted'), counts one tag for both. Each source on a bullet counts with its own tag; the share stays adopted only (adapted, planned and own count 0) and the principle headline stays the average of its rows, adopted only. Re-render the front pages with criteria.py render so the cells show the corrected numbers. No requirement text, tag or Follows line changes

- Slug: adoption-count-fix
- Touches: skills/workflow-docs/scripts/sections.py, README.md, docs/wiki
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a Follows cell with one bullet naming two sources tagged adapted and adopted, then adoption() counts two tags and returns 50, and a cell of single-source bullets returns the same value as on main (toy for both forms)
2. Given the counter on this branch, then criteria.py render rewrites only Adoption cells and Adoption headline lines in the front pages, HLT-2, REG-4 and MCH-1 show each source's own tag counted, and docs check and render --check pass
3. Given this goal's diff, then only sections.py (no larger than 19,000 bytes), the re-rendered front pages, the toy and the goal's own records change, no requirement text, tag or Follows line changes, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
