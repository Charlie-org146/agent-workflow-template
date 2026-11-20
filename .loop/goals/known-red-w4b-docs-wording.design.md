# Design: known-red-w4b-docs-wording

**Problem.** Two rows are red on main since the v2 rewrite of the pages. `milestone-wording-unreviewed` (dev/toy/test-milestone-wording.sh) demands that HLT-4's text say "on no milestone", but the r1 rewrite of HLT-4 (2026-11-18) dropped the phrase. `doc1-sync-pointer` greps DOC-1 for the `docs.py sync` pointer, but DOC-1's revision r2 (2026-11-18) removed that sub-bullet; the sync behaviour now lives in DOC-17.

**Approaches.**
1. Change the requirement pages to bring the wording back. Cost: edits Reviewed or owner-worded text; needs the owner's words. Rejected.
2. Fix the toy and the row, no page text change: drop the stale HLT-4 phrase check from the toy (the defect-on-no-milestone behaviour is covered by rows hlt4-feature-milestones and backlog-defect-home), and remove the `doc1-sync-pointer` row, whose behaviour (DOC-1 carries the pointer) no longer exists, with that evidence in the PR.

**Chosen:** 2. The toy keeps its other checks, including that no requirement says an issue or pull request must have a milestone. DOC-1 keeps its other rows; DOC-17's rows cover the sync behaviour.

**Done lines.** 1: `milestone-wording-unreviewed` passes (its two python blocks print CLEAN locally; CI is the proof); `doc1-sync-pointer` is removed with the evidence above. 2: no row is added to regression-known.tsv; net rows are -1.

**Open questions.** None for the owner: no requirement or Reviewed text changes.
