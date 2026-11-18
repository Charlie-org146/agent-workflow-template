# CI's runner can commit release files in the toys, so merge-failed-retry (#4862), review-recorded-merges (#4428) and sync-propose (#4967) pass on Linux CI as they do on the Mac and the PC

- Slug: ci-release-commit-identity
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the regression workflow on a GitHub runner, when merge-failed-retry, review-recorded-merges and sync-propose run, then each passes, and the three lane issues close with the run as evidence.
2. Only the runner's commit identity (or the toys' own setup) changes; no row is removed or marked known, no cap changes, and net rows added are zero (deleting the sync-propose known row once it passes is allowed).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
