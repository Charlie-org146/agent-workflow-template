# A kept marker re-stamps a guide page (such as Principles) the way it does a How-to page, so a goal that legitimately changes code a guide page maps to can pass docs.py check without editing the page (issue #5605; unblocks #5286). Today audit.py relock and restamp-own skip a page with no Review line, so 'STALE Principles: 1 commits since the page' cannot clear

- Slug: guide-page-stamp
- Touches: skills, dev/toy
- ETA: 485 active minutes (estimate 387m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal branch whose code commit touches code Principles maps to, when the goal keeps a marker for Principles, then docs.py check passes with no edit to Principles.md, and without the marker it still prints STALE Principles (negative control)
2. Given the pull request, then it closes issue #5605, a toy proves both cases, its row is SEEN RED with the change reverted, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
