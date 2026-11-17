# changelog-v design (DOC-13, #4660)

## Problem
`audit.py release_trouble` looks for a CHANGELOG heading with the regex `^## \[?<tag>\b`, where `<tag>` is the git tag
including its leading `v`. A CHANGELOG written as `## [1.2.3]` (Keep a Changelog style) never matches tag `v1.2.3`, so
every such tag falls through to `gh release view`, a network call, and is flagged RELEASE if gh is missing or offline.

## Approaches
1. Strip the `v` from the tag and match `^##\s+\[?v?<version>\b`. One-line change, no new dependency. Risk: `\b` after
   `1.2.3` also matches `1.2.3.4` or `1.2.3-rc1`; acceptable, the old regex had the same property.
2. Parse every heading into a set of versions first, then test membership. Exact, but more code for the same result.

## Chosen
Approach 1, with a lookahead `(?![\w.]*\d)`-free form kept simple: `\b` as today. The gh fallback stays untouched, so a
tag with no heading still calls `gh release view`.

## Done lines
1. `## [1.2.3]` with tag `v1.2.3`: the new regex matches, so `gh` is never run. Proved with a toy repo whose `gh` is
   absent from PATH (or a fake that logs calls) and an audit that prints no RELEASE line and no gh call.
2. A tag with no heading: regex misses, the existing `gh release view` fallback runs and the RELEASE line still appears
   (existing `release-note-found` behaviour).

## Open questions
None. Regression table is over its 1200-row cap, so new rows are paid for by merging duplicate rows.
