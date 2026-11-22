# Fix #5797: audit.py restamp-own makes no commit and appends no rows when nothing is stale (Operation TD969)

- Slug: restamp-own-idempotent
- Touches: skills/workflow-docs, dev/toy, .loop/regression.tsv, docs/wiki
- ETA: 355 active minutes (estimate 282m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a repo whose stamps are all current, then audit.py restamp-own <slug> run twice makes no commit and appends no rows on either run
2. Given one really stale stamp, then restamp-own restamps exactly that page and appends only its rows, once, and a second run makes no commit
3. Given a toy, then it covers lines 1 and 2 with a negative control (break the fix, and the second-run-no-commit check fails), as one regression row under the requirement restamp-own serves; no existing row or check is loosened and nothing is trimmed (no file newly crosses 19,000 bytes)
4. Given the whole change, then the docs, package and private-name checks pass, and the goal stops at a pull request

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
