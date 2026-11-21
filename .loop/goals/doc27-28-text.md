# Add DOC-27, the feature standard, and DOC-28, release kinds and the brief, to the template's Documentation page as new requirements, word for word from the owner's draft, both Unreviewed, plus the v1.1.0 brief marked not frozen, and turn full auto off (owner record o700; Operation TD658, TD659). Docs and config only

- Slug: doc27-28-text
- Touches: .loop/config.json, docs/wiki, docs, README.md
- ETA: 415 active minutes (estimate 331m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given this goal's first commit, then it sets full_auto and auto_approve to false in .loop/config.json, citing owner record o700
2. Given docs/wiki/Documentation.md, then DOC-27 and DOC-28 are added as new requirements through criteria.py's add path, both Unreviewed, each with its five functional requirements word for word from the owner's draft page
3. Given docs/, then the v1.1.0 brief is added as a file exactly as on the draft page, marked not frozen
4. Given this goal's diff, then the docs check and the private-name scan pass and no other file changes
5. Given the pull request, then it stops at the PR and its body comes from the goal file's PR notes section

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
