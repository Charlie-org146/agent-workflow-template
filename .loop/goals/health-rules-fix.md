# Health's rules are right on main (TD521): the requirements-per-page rule does not count DOC-N moved to X forwarding lines (the Documentation page has 3 live requirements, not 26), and the migration control fires on a fixture made to break it. No README or page text changes

- Slug: health-rules-fix
- Touches: skills, dev/toy
- ETA: 295 active minutes (estimate 234m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a page with 3 live requirements and 23 moved-to lines, then requirements-per-page counts 3 and passes, and a page with 25 live requirements still fails (negative control); given the migration fixture made to break it, then controls.py run migration reports it
2. Given the pull request, then each changed rule's row is SEEN RED first, health.py check on main no longer prints the Documentation and migration FAIL lines, no page text changes, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
