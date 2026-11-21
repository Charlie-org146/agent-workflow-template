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

## PR notes

Fixes the Adoption counter, not the README text (Operation TD531, TD569; Refs #5631).

Root cause: `follows()` and `adoption()` in `skills/workflow-docs/scripts/sections.py` read one tag per Follows bullet. A bullet that names two sources, each with its own tag (`[A](url): adapted; [B](url): adopted`), counted one tag for both, so the Adoption share was wrong for HLT-2, REG-4 and MCH-1 since #5631.

Fix: `follows()` splits a bullet at `; ` (outside brackets, parentheses and code spans, after a complete `source: tag` pair) and each source counts with its own tag; the share stays adopted only (adapted, planned and own count 0) and a principle's headline is still the average of its rows. A bullet that cannot be read cleanly stays one source, exactly as on main. The scan is one linear pass.

Changed Adoption cells, produced by `criteria.py render` (README, Home, Principles; no requirement text, tag or Follows line changes): HLT-2 33 to 25 percent and MCH-1 25 to 20 percent; the headlines of principle 2 (43 to 42 percent) and principle 5 (45 to 44 percent). The published figures drop on purpose; Operation ruled that MCH-1's requirement text stays unchanged.

Tests: `dev/toy/test-follows-adoption.py` gains the two-source case, edge cases (three sources, untagged and half-tagged bullets, trailing and doubled semicolons, unbalanced brackets, escapes, code spans, leading space, empty name, a long bullet), an independent count of every Follows cell of the README (27 cells, 0 mismatches) with negative controls, and five hand-counted cells.

Review: full review at depth full, one fix cycle and a final pass with no edits; 0 critical, 8 informational notes. The review replies are in `.loop/runs/adoption-count-fix.plan.txt` and `.loop/runs/adoption-count-fix.review.txt`. The plan file's "Test plan artifact" paragraph was removed (Operation TD601); the eng-review summary lives in the plan file's Review record and in the plan reply.

Follow-ups: a docs-check finding for Follows bullets the counter cannot read (one `source: tag` pair per line), and the review notes (a literal tag-length bound, a double space after a semicolon, multi-backtick code spans, a colon inside a link label).
