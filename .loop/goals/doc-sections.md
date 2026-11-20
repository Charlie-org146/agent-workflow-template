# Every wiki page and the README have the same fixed sections, and README and Home match (new requirement DOC-25 under principle 1, owner words o483, 21:46 PT 2026-11-19, TD258): README and Home have exactly the same sections in the same order, one System design section replaces the per-principle diagrams on both, Home's System diagram becomes that section and its Settings and Automation sections move to the Setup and Automation How-to-use pages, every Part 1 requirement row links to its own workflow figure, and the docs check enforces the section lists. Source draft: doc-sections-draft.md in the Operation session's readme-drafts folder (the worker is sent its text). Builds on principle-8-readme's result and merges after it and after the merge-queue chain

- Slug: doc-sections
- Touches: README.md, docs/wiki, skills/workflow-docs/scripts, dev/toy, .loop/requirements, .loop/flows
- ETA: 360 active minutes (estimate 288m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. DOC-25 is on the Documentation page and in principle 1's table with its Follows cell, with the four approved bullets word for word (owner record o483); Follows names markdownlint MD043 and C4 system context; the next free ID is used if DOC-25 is taken at build
2. README.md and docs/wiki/Home.md have exactly the same sections in the same order (title and introduction, System design, one section per principle with its sentence and table and no diagram of its own, Requirements by feature); one new System design figure shows how the principles connect; Home's Settings and Automation sections move to the Setup and Automation How-to-use pages; the Principles page keeps each principle's own diagram
3. Every Part 1 requirement row, including the rows that say none yet and principle 8's rows, links to its own workflow figure
4. Given a page with a missing, extra, renamed or out-of-order section, or a README and Home that differ in sections, a principle's sentence or its table, or a requirement row with no figure, when the docs check runs, then it fails; each of these has a negative control; the plan first tries adopting PyMarkdown's md043 rule and says which it chose and why (DEL-21)
5. Given this goal's diff, then net regression rows are 0 apart from the new controls, no touched script is over 19,000 bytes or larger than on main, and no requirement text changes except DOC-25 and its Follows cell

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `bash dev/toy/test-docs-sections.sh | tail -2`.
   Expect: the last line is `ALL PASS`.
2. Run `python3 skills/workflow-docs/scripts/docs.py check | grep -c "^FORMAT"`.
   Expect: it prints 0.
3. Run `diff <(grep "^## " README.md) <(grep "^## " docs/wiki/Home.md)`.
   Expect: no output; both list System design, the eight principles and Requirements by feature, in that order.
4. Open `docs/wiki/system-design.svg` in a browser.
   Expect: one diagram of the owner, the loop's parts and the outside systems it uses.
5. Rename `## Non-goals` to `## Out of scope` in docs/wiki/Delivery.md and run `python3 skills/workflow-docs/scripts/docs.py check | grep Delivery`.
   Expect: a Sections line naming Delivery, DOC-25 and Non-goals. Undo the rename afterwards.
