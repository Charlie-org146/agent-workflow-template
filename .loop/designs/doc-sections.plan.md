# doc-sections: plan (draft, pre-review)

Design: .loop/designs/doc-sections.md. Goal done lines 1 to 5 frozen. Review depth for this step is waiting on Operation (full pipeline vs condensed).

## Work list, in build order

A. Now, before principle-8-readme lands (no README.md or Home.md edits):
1. Figures: add docs/wiki/flows/<ID>.svg for DOC-24, DEL-21, HLT-2 (the three "none yet" rows) and for principle 8's rows (IDs taken from main once principle-8-readme is merged), same style as flows/DEL-1.svg; one new System design figure (C4 system context: the principle groups and who/what they touch), built from principles-overview.svg.
2. Section lists as data: one data file under skills/workflow-docs (ordered headings per page kind: README, Home, feature, How-to-use, Principles, Tests, Roadmap; a marker for a variable tail such as the per-requirement ### headings).
3. A new stdlib script in skills/workflow-docs/scripts that reads the data file and fails on a missing, extra, renamed or out-of-order heading, and on README and Home differing in sections, a principle's sentence or its table (reuses pageformat helpers; pageformat.py stays at or under its main size).
4. Toys (dev/toy): one new test-docs-sections.sh with five negative controls (missing, extra, renamed, README and Home out of sync, a row with no figure) each seen failing on the bad page and passing on the good; no existing row is weakened or removed.
B. After principle-8-readme is on main (merge main with the floor step):
5. README.md and Home.md: remove per-principle diagrams, add the System design section, move Home's Settings and Automation to the Setup and Automation How-to-use pages, same section list on both.
6. DOC-25: criteria.py revise with owner record o483, once per requirement row, text word for word from the approved draft; Follows names MD043 (adapted) and C4 system context; add the row to Documentation.md, Principles.md, README and Home principle 1 tables.
7. Wire the new check into the docs check (docs.py gate) and re-render Tests tables.
C. Then qa lane, ship, hold for the chain; no goal.py pr before.

## Constraints and checks per done line
- Line 1: criteria.py revise text compared with the approved draft by diff, quoted in the PR body.
- Line 2: section lists compared README vs Home by the new check; Principles page keeps its diagrams.
- Line 3: the existing flow-link check (frontdoor) passes on every Part 1 row, none-yet rows included.
- Line 4: five negative controls; md043 try result recorded in design.
- Line 5: wc -c on each touched script against main; regression.tsv row delta = the new controls only.

## Open for review
- The variable-tail marker in the section data file.
- Whether the new script or an existing one holds the check, decided by byte counts at build.
