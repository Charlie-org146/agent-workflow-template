# Add DOC-27, the feature standard, and DOC-28, release kinds and the brief, to the template's Documentation page as new requirements, word for word from the owner's pinned draft, both Unreviewed, plus the v1.1.0 brief marked not frozen (owner records o700, o701, o702; Operation TD658 to TD664). Re-frozen without the old config done line: full auto stays on, so this goal's two earlier config commits are reverted by new revert commits. Docs only

- Slug: doc27-28-text-2
- Touches: docs/wiki, docs, README.md, .loop/config.json
- ETA: 375 active minutes (estimate 297m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given docs/wiki/Documentation.md, then DOC-27 and DOC-28 are added as new requirements in the format the docs tool prints for the next ID, both Unreviewed, each with its five functional requirements word for word from the owner's draft page
2. Given docs/, then the v1.1.0 brief is added as a file exactly as on the draft page, marked not frozen
3. Given this goal's diff, then the docs check and the private-name scan pass and nothing changes beyond what adding DOC-27 and DOC-28 requires, with .loop/config.json identical to main
4. Given the pull request, then it stops at the PR and its body comes from the goal file's PR notes section

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
