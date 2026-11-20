# The docs tools accept exactly the README format the owner approved (owner record o514, "yes build it", covering README-final-draft.md as sent at 03:27; Operation TD362; DOC-25 and DEL-21). It is built on branch loop/doc-sections (pull request 5455, which adds the sections check sections.py and is not yet on main), so it merges after 5456 and 5455. The docs check, the sections check and the render accept: principle tables with the columns Requirement, Summary, Follows, Feature, Adoption, Confidence (no Version column, no Flow column); each requirement row links its own workflow figure inside the Requirement cell (DOC-25 as approved); README and Home sections in this order: What this is, System design, one section per principle, Requirements by feature, with How it works as a paragraph inside each principle section, not a section; What this is rendered from DEL-19's text; Adoption computed by the render from each row's Follows tags (adopted counts 1, adapted or own 0, averaged per principle), deterministic; Confidence a column whose blank cell passes the check for now (the principle 2 goal fills it later). The owner's text is not changed by this goal; readme-six then goes in as documents only on this machinery. If it adds a regression row it builds it but pushes only after rows-600-a is on main, with a red proof; lane prep and the caps guard before the push; no local lane

- Slug: docs-format-v2
- Touches: skills/workflow-docs/scripts/pageformat.py, skills/workflow-docs/scripts/sections.py, skills/workflow-docs/scripts/render.py
- ETA: 400 active minutes (estimate 320m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a README, Home and Principles page in the approved format (Requirement | Summary | Follows | Feature | Adoption | Confidence, the figure link inside the Requirement cell, the sections What this is, System design, one per principle, Requirements by feature), then the docs check and the sections check pass, and the old format still fails with a message naming the new one
2. Given the render, then it writes What this is from DEL-19's text and each row's Adoption from its Follows tags (adopted 1, adapted or own 0, averaged per principle), and a blank Confidence cell passes the check
3. Given this goal's diff, then only the docs tools (pageformat.py, sections.py, render.py and their toys), the pages they regenerate and the goal's own records change, no requirement text changes, each script stays under its size cap (real trims), and the docs check passes on main's current pages as migrated by the render

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
