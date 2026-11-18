# merge.py's wiki step stops refusing a repo whose PRD pages are link-form: the unmigrated-Revisions NOTE counts only local pages and never blocks a merge (TOP-DECISION 26; found by an adopter repo's docs migration)

- Slug: link-form-note
- Touches: not declared
- ETA: 295 active minutes (estimate 234m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. release.docs_trouble ignores NOTE lines, as it already ignores UNTESTED, SKIP, MILESTONE and DOCS lines
2. criteria.py's 'page(s) have no Revisions section (unmigrated)' NOTE counts only local pages, never link-form pages (a PRD line pointing at a linked document)
3. A test row with a fixture repo holding link-form pages and one migrated local page shows merge.py's wiki step passing with the new code and refusing the same fixture with the old code (its negative control)
4. Nothing else changes; net test rows grow by at most 2

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
