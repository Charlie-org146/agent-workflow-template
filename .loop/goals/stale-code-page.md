# A page made stale only by a code change no longer fails a goal's ship lane before the re-stamp can run (#4442)

- Slug: stale-code-page
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a goal whose code change stales its own feature page, when ship runs, then the page is re-stamped on the branch before the docs rows run and ship passes
2. Given a page stale for a real text reason, when ship runs, then it still fails

## Verify by hand

<!-- Numbered steps a person can follow, each with an Expect: line. -->
