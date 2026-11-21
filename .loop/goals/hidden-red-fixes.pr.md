# hidden-red-fixes: every hidden-red toy back to green, run by ten grouped defect rows

29 toys are green on this branch. Wall times are standalone, one toy at a time, outside any sandbox, from a Claude app session (so the host session variables were set). Only toys, their fixtures, the new rows and the re-rendered Tests page changed; no product script, check, known list, setting or `.loop/config.json` changed.

## Defect rows

Each row runs its group in one command, links every issue it covers (space-separated links), and was seen red then green. Red: `regression.py red ID --break "git checkout <main sha> -- dev/toy/<toy>"` restores the named toy as it was on main, and the row failed. Green: `regression.py run ID` on this branch, wall time below (every row under 200 s; an earlier grouping that ran 175 to 200 s was split to leave margin).

| Row | Toys | Issues | Green wall s | Red by restoring |
|---|---|---|---|---|
| `defect-hidden-red-flow-budget` | test-budget.sh, test-tokens.sh, test-milestones.sh, test-status-graph.sh, test-wiki.sh | #5652 #5678 #5667 #5677 #5681 | 95 | test-status-graph.sh |
| `defect-hidden-red-flow-prd` | test-delivery-prd.sh | #5654 | 98 | test-delivery-prd.sh |
| `defect-hidden-red-docs-pages` | test-apply-rerender.py, test-docs-command.sh, test-docs.sh, test-stale-code-page.py | #5650 #5655 #5658 #5676 | 81 | test-apply-rerender.py |
| `defect-hidden-red-docs-format` | test-docs-format.sh | #5656 | 51 | test-docs-format.sh |
| `defect-hidden-red-docs-criteria` | test-criteria.sh | #5653 | 80 | test-criteria.sh |
| `defect-hidden-red-health` | test-health-judge.sh, test-health-report.sh | #5661 #5662 | 120 | test-health-judge.sh |
| `defect-hidden-red-monitor` | test-govern.sh, test-lanes.sh, test-machine-status.py, test-narrow.sh, test-monitoring.sh, test-operate-fit-3.sh, test-machine-log.py, test-platform-limits.py | #5659 #5664 #5666 #5669 #5668 #5670 #5665 #5671 | 122 | test-platform-limits.py |
| `defect-hidden-red-regression-rows` | test-regression.sh | #5672 | 143 | test-regression.sh |
| `defect-hidden-red-release` | test-release.sh, run-goal.sh | #5673 #5649 | 109 | test-release.sh |
| `defect-hidden-red-settings-guard` | test-settings-table.sh, test-docs-issues.sh, test-home-stale.sh, test-guard-enforce.sh | #5675 #5657 #5663 #5660 | 77 | test-settings-table.sh |

## Toys

| Toy | Issue | Before (exit, FAIL lines) | After | Wall s | Change |
|---|---|---|---|---|---|
| `dev/toy/test-budget.sh` | #5652 | 1, 3 | 0, 0 FAIL | 19 | Host session id unset (hrt-flow) |
| `dev/toy/test-delivery-prd.sh` | #5654 | 1, 9 | 0, 0 FAIL | 110 | Hermetic env; owner record on a budget raise; per-goal touches (hrt-flow) |
| `dev/toy/test-tokens.sh` | #5678 | 1, 4 | 0, 0 FAIL | 9 | Hermetic env (hrt-flow) |
| `dev/toy/test-milestones.sh` | #5667 | 1, 1 | 0, 0 FAIL | 19 | Hermetic env; the empty milestones_source key is filtered, with two negative controls (hrt-flow) |
| `dev/toy/test-status-graph.sh` | #5677 | 1, 1 | 0, 0 FAIL | 7 | Hermetic env (hrt-flow) |
| `dev/toy/test-wiki.sh` | #5681 | 1, 8 | 0, 0 FAIL | 35 | Hermetic env (hrt-flow) |
| `dev/toy/test-apply-rerender.py` | #5650 | 1, 8 | 0, 0 FAIL | 36 | Settings block checked where it now lives, Home.md (hrt-docs) |
| `dev/toy/test-docs-command.sh` | #5655 | 1, 2 | 0, 0 FAIL | 24 | Fixture repaired to the DOC-19 rules, with controls (hrt-docs) |
| `dev/toy/test-docs-format.sh` | #5656 | 1, 8 | 0, 0 FAIL | 63 | Fixture uses DOC-23 tagged bullets (hrt-docs) |
| `dev/toy/test-docs.sh` | #5658 | 1, 0 | 0, 0 FAIL | 37 | Host session id unset, new control (hrt-docs) |
| `dev/toy/test-criteria.sh` | #5653 | 1, 0 | 0, 0 FAIL | 78 | Host session id unset, new control (hrt-docs) |
| `dev/toy/test-stale-code-page.py` | #5676 | 1, 3 | 0, 0 FAIL | 7 | Lane prep re-stamp in its own Kept commit (hrt-docs) |
| `dev/toy/test-health-judge.sh` | #5661 | 1, 3 | 0, 0 FAIL | 62 | Budget and rules-first drift, controls added (hrt-health) |
| `dev/toy/test-health-report.sh` | #5662 | 1, 3 | 0, 0 FAIL | 31 | Unread padding, preview lines, tag backfill, controls added (hrt-health) |
| `dev/toy/test-guard-enforce.sh` | #5660 | 1, 2 | 0, 0 FAIL | 61 | Host session id unset (hrt-health) |
| `dev/toy/test-govern.sh` | #5659 | 1, 7 | 0, 0 FAIL | 4 | This goal: a stand-in agent replaces the real claude call; no push (below) |
| `dev/toy/test-lanes.sh` | #5664 | 1, 3 | 0, 0 FAIL | 40 | Host session id unset plus a worker-not-session check (hrt-monitor) |
| `dev/toy/test-machine-status.py` | #5666 | 1, 3 | 0, 0 FAIL | 1 | Own floor and throwaway HOME (hrt-monitor) |
| `dev/toy/test-monitoring.sh` | #5668 | 1, 2 | 0, 0 FAIL | 37 | Fixture copies batch.py (hrt-monitor) |
| `dev/toy/test-operate-fit-3.sh` | #5670 | 1, 2 | 0, 0 FAIL | 17 | Comment-only change no longer stales a page; real function change used (hrt-monitor) |
| `dev/toy/test-narrow.sh` | #5669 | 1, 4 | 0, 0 FAIL | 7 | Fixture copies tiers.py and slots.py, new control (hrt-monitor) |
| `dev/toy/run-goal.sh` | #5649 | 1, 0 | 0, 0 FAIL | 0 | A helper: a bare run prints usage and exits 0 (hrt-misc) |
| `dev/toy/test-regression.sh` | #5672 | 1, 6 | 0, 0 FAIL | 142 | Numeric shard count, controls added (hrt-misc) |
| `dev/toy/test-release.sh` | #5673 | 1, 0 | 0, 0 FAIL | 127 | Asserts the MAJOR_GATE refusal (hrt-misc) |
| `dev/toy/test-settings-table.sh` | #5675 | 1, 2 | 0, 0 FAIL | 6 | This goal: the fixture README seeds the settings markers (below) |
| `dev/toy/test-docs-issues.sh` | #5657 | 1, 2 | 0, 0 FAIL | 19 | This goal: real code changes replace comment-only ones (below) |
| `dev/toy/test-home-stale.sh` | #5663 | 1, 1 | 0, 0 FAIL | 9 | This goal: sed -i.bak helper and a portable replacement newline (below) |
| `dev/toy/test-machine-log.py` | #5665 | 1, 1 | 0, 0 FAIL | 1 | This goal: host variables removed, throwaway HOME (below) |
| `dev/toy/test-platform-limits.py` | #5671 | 1, 2 | 0, 0 FAIL | 3 | This goal: host variables removed, throwaway HOME (below) |

## What this goal changed itself

- **#5675 settings table (a stale toy, not a product bug):** commit 8bb298294 moved Settings and Automation to the How-to-use pages; render fills a README only where it already holds the `settings:begin` and `settings:end` markers. The fixture README now seeds them, and the toy still requires the README block to carry `parallel` (without the markers it still FAILs). Re-rendering from settings.py cannot help, since the real README no longer carries the block.
- **#5663 BSD sed (toy only, no product script):** the toy used `sed -i` with no suffix, which BSD sed rejects, and a GNU-only `\n` in a replacement. It now uses a `sedi` helper (`sed -i.bak`, then removes the backup) and a backslash-newline. No product script uses it.
- **#5657:** the toy's appended commits were comment lines, and comment-only changes no longer stale a page. They are real assignments now; every assertion is unchanged and passes.
- **#5665, #5671:** the host session id, the real `~/.claude.json` (FOLDER_TRUST) and `~/.workflow-loop` leaked in. Both toys now drop `LOOP_*` and `CLAUDE*` variables and use a throwaway HOME. No assertion changed.
- **#5659 test-govern.sh (TD586):** it ran two real headless claude agents. It now builds each goal with a stand-in agent script (it writes the module and test, commits, opens the pull request through the faked gh and marks the goal done). The push to the fixture's origin is removed: after the fixture's last commit the origin is rebuilt with `git clone --bare --single-branch --branch main`. Same starting state as the push left: origin holds `refs/heads/main` only, at the fixture's HEAD, origin HEAD is `refs/heads/main`, and main tracks origin/main. All 14 checks are unchanged and pass. Seen red on main: the real agents ended with a usage-limit error and 8 checks FAILed; now ALL PASS in 4 s.

## Still red, not in this change

- `dev/toy/test-scan-sites.sh` (#5674): a real product bug, 8 push or GitHub-write sites have no private-name scan. It has its own goal. No Fixes line.
- `dev/toy/test-tree.sh` (#5679): needs `# reads:` headers in about 20 other toys and the defect rows for #88, #5635 and #5638; moved to the v2fix-bundle goal. No Fixes line.

## Notes

- The flaky docs-pages run: one grouped run of the `defect-hidden-red-docs-pages` row failed once after 44 s in an earlier grouping. The same toys passed alone and the row passed on rerun. It was not reproduced, and the final row is green.
- test-health-report.sh prints FAIL-bearing lines (`FAIL requirements REL-1`, `FAIL docs Ghost`) that are the product's output on its deliberately failing fixtures; its exit is 0. Likewise `FAIL flag` in test-regression.sh and `FAIL a` in test-lanes.sh are fixture output.
- Checks: `criteria.py render` re-rendered docs/wiki/Tests.md; `docs.py check` DOCS OK (16 pages, no restamp needed); `criteria.py render --check` TABLES OK; `dev/package.py --static` PASS; the private-name scan of the diff found nothing.

## How this file was written

The push hook refused the Bash command that wrote this file, because it matched prose in the text (the sentence about the fixture's origin), not a real push. Nothing was pushed. This file was then written with the file tool under the owner's ruling o685: "workers may write documentation text with the file tool when the push hook matches only prose".

Counts: 29 "Fixes #N" lines below, one for each issue whose toy is green. #5674 and #5679 are excluded and have no Fixes line.

## Fixes

Fixes #5652
Fixes #5654
Fixes #5678
Fixes #5667
Fixes #5677
Fixes #5681
Fixes #5650
Fixes #5655
Fixes #5656
Fixes #5658
Fixes #5653
Fixes #5676
Fixes #5661
Fixes #5662
Fixes #5660
Fixes #5659
Fixes #5664
Fixes #5666
Fixes #5668
Fixes #5670
Fixes #5669
Fixes #5649
Fixes #5672
Fixes #5673
Fixes #5675
Fixes #5657
Fixes #5663
Fixes #5665
Fixes #5671
