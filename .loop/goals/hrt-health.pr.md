# hrt-health: bring toys up to current behaviour (#5661 #5662 #5674 #5679 #5660)

Three toys are updated and green. Two are left unchanged: one shows a product gap, one fails on things outside the listed toys.
Wall time is the final run of each toy, measured with `/usr/bin/time -p`, in seconds.

| Toy | Before (exit, FAIL) | After (exit, FAIL) | Wall s | What changed, or why unchanged |
|---|---|---|---|---|
| dev/toy/test-health-judge.sh | 1, 3 | 0, 0 | 84.69 | Updated (two drifts, see below) |
| dev/toy/test-health-report.sh | 1, 3 `FAIL:` lines (8 FAIL-bearing lines by a plain grep) | 0, 0 `FAIL:` | 37.95 | Updated (three drifts, see below) |
| dev/toy/test-guard-enforce.sh | 1, 2 | 0, 0 | 80.59 | Updated (environment gate, see below) |
| dev/toy/test-scan-sites.sh | 1, 1 | 1, 1 | 0.82 | Product gap: left unchanged |
| dev/toy/test-tree.sh | 1, 8 | 1, 4 `FAIL:` lines | 92.70 | Left unchanged: needs edits outside the listed toys |

## test-health-judge.sh

- Drift 1, "no budget set": setup now writes a default `time_budget_minutes` (240), so a fresh toy repo has a budget and the INFO row never appears. The toy now removes both budget keys first and asserts the same INFO row. Stricter: a control sets a budget and asserts the INFO row is gone.
- Drift 2, "rules first": `health check` now prints a FINDINGS table after the header and PRINCIPLE lines before the verdict; `health judge` prints the header, rule rows and verdict only, then the judge section. The toy still compares the judge output with the check output line for line, minus those two check-only blocks (the old whole-text equality is gone). Controls: a changed rule row and a missing verdict are each caught.
- Product note for the owner: `report.py cmd_judge` says "The check report, then the judge section", yet omits the FINDINGS table and PRINCIPLE lines. If that is unintended, it is a product fix, not a toy change.

## test-health-report.sh

- "unread padding": when regression.py is missing, three rules (rows, proof, done) are UNREAD and the independent principle-map rule passes. The toy asserts exactly that, line by line, no PASS row for any of the three, plus a control per rule that rewrites its UNREAD to PASS and must be rejected.
- "preview lines": preview rows now carry `feature:` tags and their destination (`as defect` or `as backlog on Backlog: Other`). The toy matches whole lines (`grep -qx`) with tag, feature and destination; controls strip or change each feature tag and must be rejected.
- "tag backfill": the update line now names group and feature tags. The toy matches the whole line, then reads the fake GitHub store and asserts both labels are on issue #2; controls corrupt each tag.
- The printed `FAIL requirements REL-1 ...` and `FAIL docs Ghost ...` lines are the product's output on the toy's deliberately failing fixtures, not toy failures. REL-1's "323 days" is only echoed; no assertion depends on the date.

## test-guard-enforce.sh

- The merge-refusal check runs `test-delivery-release.sh private`, which makes goals with `goal.py new`. With `CLAUDE_CODE_HOST_SESSION_ID` set (any Claude app session), new goals now bind to that session, `flow.py` prints IN SESSION and waits for a reply, and no pull request is made. The toy now unsets that variable at the top. The assertion is unchanged (it still needs the sub-toy's PASS line that merge.py refuses and nothing merged), so it is as strict as before.

## test-scan-sites.sh (left unchanged: product gap)

The toy fails the way it is meant to. Eight functions pushed or write to GitHub with no call to the private-name scan:
`fit.py:pr_open` (its caller `goal.py` runs `pr_text`, which scans, first), `autorelease.py:label_part`, `merge.py:merge_pr`, `review.py:promote` (pushes main, a tag and a branch; its release notes hold closed-issue titles and are not scanned), `review.py:revert`, `machines.py:batch_assemble`, `machines.py:batch`, `operate.py:apply` (pushes re-stamped wiki pages).
Some are plausibly covered by the git pre-push hook or carry fixed text, but `promote`'s notes file and the batch and re-stamp pushes are not shown to be scanned. Allow-listing them in the toy would loosen the control, so nothing changed. Owner decision: scan these sites in the product, or record each as exempt with its reason.

## test-tree.sh (left unchanged)

Four `FAIL:` lines remain:
1. `lanes_cli.py check` reports `# reads:` header findings (misplaced, missing, or undeclared `skills/` reads) in other toys: test-body-file, test-docs-link, test-docs-split, test-govern, test-guards-null-report, test-health-listing, test-health-prd, test-local-schedule, test-machine, test-merge-batch, test-merge-guard, test-migration, test-owner-words, test-portable, test-pr-tries and more. Fixing them edits toys outside this goal's list.
2. and 3. The two reach-analysis assertions that depend on those headers (rerun fewer than half the land rows; a script naming `.git/`).
4. Repo health: `FAIL traceability` for #88, #5635 and #5638 (closed with no defect test; needs regression rows, which this goal may not change) and `FAIL hygiene eta-unmarked` for another goal's ledger.
