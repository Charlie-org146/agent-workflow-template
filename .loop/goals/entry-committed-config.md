# entry.py renders START.md from the committed .loop/config.json, not a working copy carrying a local skip-worktree edit (o156)

- Slug: entry-committed-config
- Touches: not declared
- ETA: 240 active minutes (estimate 192m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a worktree whose config.json has a local skip-worktree edit (min_free_memory_gb 2.0 against committed 3.0), when entry.py write runs, then START.md shows the committed 3.0 and merge.py's stale check passes
2. The rule has a test row seen failing and passing, and the Documentation page states it with the new wording going to the owner for review

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
