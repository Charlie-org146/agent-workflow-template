# Every diagram on the wiki's Principles page shows on the published GitHub wiki in Safari as in Chrome (owner o76 "approve and fix the principle pages")

- Slug: principle-diagrams-safari
- Touches: not declared
- ETA: 295 active minutes (estimate 234m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each image on the published Principles wiki page (the overview and the eight principle diagrams) loads in WebKit/Safari: its link resolves on the published wiki, not only in the repo's docs/wiki folder
2. A check with a negative control fails when a wiki page embeds an image path that will not resolve on the published wiki, naming the page, the path and the fix, and runs where the wiki checks already run
3. Nothing else changes; net test rows grow by at most 2

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
