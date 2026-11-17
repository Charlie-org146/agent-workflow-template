# DOC-13: audit.py release_trouble finds CHANGELOG headings with or without a leading v, without calling gh (#4660)

- Slug: changelog-v
- Touches: skills/workflow-docs/scripts/audit.py
- ETA: 170 active minutes (estimate 133m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a CHANGELOG with ## [1.2.3] and tag v1.2.3, when release_trouble checks it, then it finds the note without calling gh
2. Given a tag with no CHANGELOG heading, when it checks, then it still falls back to gh release view

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
