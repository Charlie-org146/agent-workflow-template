# ci-affected-rows plan

I checked these against the code at d2adcaae:
- `skills/workflow-regression/scripts/lanes_cli.py` `affected()` lines 100-129: the DELETED branch, lines 108-112, ends in `continue`
  without setting `real`, and line 127 adds the root runners only `if real`.
- `dev/toy/test-merge-guard.sh` line 16 exports a temp `HOME` with no git identity; lines 81-84 hold the root-runner check.
- The 7 rows are at `.loop/regression.tsv` lines 473-476 and 485-487, each `bash dev/toy/test-merge-guard.sh 2>&1 | grep -qF "PASS: ..."`.

## Build steps
1. `lanes_cli.py`: in `affected()`'s DELETED branch, set `real = True` before `continue`. That branch only takes paths that
   aren't NO_EFFECT, so a deleted VERSION never gets there. The file stays at or under 19,000 LF bytes (18,488 now).
2. `test-merge-guard.sh`: after `export HOME=...`, export `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME` and
   `GIT_COMMITTER_EMAIL` (Toy, t@example.test). After line 84, add one check: with `src/b.txt` deleted in the working tree,
   `affected src/b.txt` lists `tc`, and `affected VERSION` with VERSION deleted lists no rows. Then restore the tree.
   Add `lanes_cli.py` to its `# reads:` lines if missing.
3. Add a defect row, `affected-deleted-root-runner` (category defect, linked to #4554, level land), for the new check, and see it
   red with `red --break` that removes the `real = True`.
4. Re-render the Tests tables. Add one clause to the Regression page's affected-rows text (unreviewed part) if it describes
   the DELETED rule. Fill in Verify by hand.

## Test per done line
1. The 7 existing rows run on CI in the PR's affected-rows job (regression-pr.yml), because the toy and lanes_cli.py change.
   Locally, a temporary copy of the toy with the Windows skip removed runs every check, and the trace shows real commits.
2. `affected-deleted-root-runner`, seen red, plus the existing `affected-quiet-release` for the NO_EFFECT half.

## What could break
- More rows on a PR that deletes a real file. That's intended: root runners read the whole repo.
- Other toys are untouched.

## Out of scope
A shared toy git identity in reap.sh (filed at ship, with the 32 toys that move HOME without one).
