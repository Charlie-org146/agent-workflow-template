# A change to .loop/config.json counts a row as affected only when the row (or a script it runs) reads a changed, added or removed key (#4321)

- Slug: config-lane
- Touches: skills/workflow-regression/scripts/lanes.py, skills/workflow-regression/scripts/narrow.py, dev/toy

## Done lines

Frozen. A wrong done line needs a new goal.

1. A change to .loop/config.json counts a row as affected only when the row, or a script it runs, reads a changed, added or removed key, not all 891 of 906 rows; a toy removing a duplicate min_free_memory_gb key (the guard-fixes case) affects only the rows that read min_free_memory_gb, proven red.
2. Toy cases for added, removed and changed keys and for a script that reads the key are each proven red.
3. Every script touched stays at or under 19,000 bytes and the package stays at 98 files or fewer.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
