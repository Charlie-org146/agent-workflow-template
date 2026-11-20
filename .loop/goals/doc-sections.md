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

## Package size and hosts: an owner override for this PR only

- This pull request also lands principle 8's README text (approved 20:53 PT 2026-11-19), because this branch is built on principle-8-readme.
- It adds one shipped file, `skills/workflow-docs/scripts/sections.py` (the DOC-25 section check), as the 105th. The owner said "Yes" to "Push the documentation fix with a 105th file this once?" (Operation TD332), recorded as the owner's 02:13 override of GRD-22 (record o504); the file cap and `listing.network` are not touched.
- `python3 dev/package.py` refuses on main and on this branch. Main: `FAIL Size: 104 files, at most 100 allowed` and `REFUSED: 40 rule failure(s); no ZIP built`. This branch: `FAIL Size: 105 files, at most 100 allowed` and `REFUSED: 45 rule failure(s); no ZIP built`.
- The five extra lines are `FAIL Disclosure: host en.wikipedia.org is not in listing.network`, and the same for `blogs.eclipse.org`, `research.google`, `standards.ieee.org` and `www.joelonsoftware.com`.
- The size-trim goal brings the package back to 100 files or fewer and declares the five hosts before any release is cut.

## System design figure

Two grids, `docs/wiki/system-design-by-principle.svg` (a row per principle, a column per feature) and `docs/wiki/system-design-by-feature.svg` (a row per feature grouped by area, a column per principle), each cell the number of that principle's requirements on the feature (92 requirement links today, a requirement naming two features counts for both), read from the Feature column of the README's principle tables. Rebuild it with `python3 dev/system-design.py`; `python3 dev/system-design.py --check` covers both and fails when either is stale. The generator is under dev/, so it is not shipped and the package file count is unchanged.

Principles was kept by audit.keep, not restamp, because the README change is image lines only.
