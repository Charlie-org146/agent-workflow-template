# The principle tables' Follows cell becomes a bullet list of the industry standards or tools the requirement adopts or plans to adopt, one per line, each tagged adopted, adapted or planned; Adoption is computed from those tags, and Confidence from the requirement's regression tests on main's latest full run, so nobody types either (o291, o293)

- Slug: follows-adoption
- Touches: skills/workflow-docs/scripts/sections.py, skills/workflow-docs/scripts/pageformat.py, skills/workflow-docs/scripts/render.py, skills/workflow-docs/references/commands.md, README.md, docs/wiki/Home.md, docs/wiki/Principles.md, dev/toy/test-follows-adoption.py, .loop/regression.tsv
- ETA: 285 active minutes (estimate 228m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a requirement row in a principle table, then its Follows cell is a bullet list, one standard or tool per line, each line tagged adopted, adapted or planned, and docs check (Health) refuses a row with no list or a line with no tag
2. Given a row's Follows list, then its Adoption is the adopted lines over all its lines, a principle's score is the average of its measured rows, and a row with no lines shows 'not measured'
3. Given a requirement and .loop/regression.tsv with .loop/regression-runs.tsv, then its Confidence is the share of that requirement's tests passing on main's latest full run, 'not measured' when it has no tests, computed by render and checked by docs check, never typed
4. Given the README, the wiki Home and Principles, when render runs, then every existing Follows cell is migrated to the bullet form keeping each source's tag (own becomes planned), and the template docs and commands.md describe the format
5. Given a toy for the three rules above, when it runs, then it passes, and with a negative control (an untagged line, a lowered tag count, a failing test) it fails
6. Given this goal's diff, then no shipped file is added, no touched script is over 19,000 bytes or larger than on main, and net regression rows are 1 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
