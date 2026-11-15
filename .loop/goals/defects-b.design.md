# defects-b design

Three open defects of the release and lane tooling. Checked against main (v0.28.58) before building.

- 3870: release-head-status (v0.28.40) already stops the lane-posted failure from asking for a manual merge. A release PR blocked by a red required check that the lane did not post (Cloudflare Pages) still fell through to "gh pr merge". Fix: autorelease.status_held also reads the PR's own check rollup and, when a required check is red, refuses naming it (RELEASE_CHECKS_FAILED), with no merge advice. Approach B (reword the one message) rejected: it still advises a merge in the generic branch.
- 3876: the rows review-findings-skill-lines and settings-render-fresh run `docs.py check --own`, which already moves a STALE page the goal's diff does not touch to a FINDING (stale-blocks-all, test-stale-own.py, and the own-diff-from-branch fix of v0.28.58). So a stale page on main no longer fails a goal. Nothing in the rows to change; what was missing is a row that keeps every STALE-grepping row on --own. Added: lane-rows-judge-own-diff, seen red.
- 3468: goal.py new --here already refuses in the main checkout when worker worktrees exist (fit.main_here, test-new-here.py, row del1-new-here-main-refused, commit 009a8328). Closed with that proof; no change.

Done lines: 1 by the new check and toy legs, 2 by the new row plus the existing toy, 3 by the existing toy and row run now. Open questions: none.
