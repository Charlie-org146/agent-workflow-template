# The session, operate and memory-floor regression rows pass again on main, and rows that already pass leave the known list

- Slug: known-red-sessions
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Rows session-assign, session-rename, session-reuse, session-reports, session-fallback, steps-in-session, session-board-issue98, record-in-session, session-answer, session-quiet, session-ended-waiting, session-tool-timeout, session-tool-helper, operate-all and no-token-dry-run pass: the test scripts that start goals (test-session-workers, test-operate, test-regression, test-criteria and any other the rows need) set min_free_memory_gb to 0 in their fixtures, operate-all uses a worktree instead of goal.py new --here in the main checkout, and no-token-dry-run no longer calls gh auth status in no-token mode
2. Rows format-frontdoor, adopt-set-1, adopt-set-2, narrow-root-172, del8-session-tokens, grd3-hook-bypass, no-prompts and every-row-described leave .loop/regression-known.tsv with the evidence that they pass or test a retired requirement (del8 and grd3 are rewritten to what DEL-7 and GRD-3 now require, or removed with the requirement's revision cited)
3. Every row this goal fixes leaves .loop/regression-known.tsv; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
