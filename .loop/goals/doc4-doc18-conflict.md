# DOC-4 and DOC-18 conflict: the Home page rule wants README How to use headings that DOC-18 removed, so wiki publish refuses (#4809; owner "start these", 2026-11-17)

- Slug: doc4-doc18-conflict
- Touches: not declared
- ETA: 270 active minutes (estimate 216m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the README with the DOC-18 links-only layout, when wiki.py publish runs, then DOC-4's Home check passes and the wiki publishes; DOC-4's wording matches DOC-18, with a test row and a negative control.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `bash dev/toy/test-docs-format.sh 2>&1 | grep "DOC-4"`.
   Expect: a PASS line for the links-only README (DOC-18) case and one for the negative control, and no FAIL line.
2. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints DOCS OK with no DOC-4 line.
