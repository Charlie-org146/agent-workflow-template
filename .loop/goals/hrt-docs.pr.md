# hrt-docs: bring toys up to current behaviour (#5650 #5655 #5656 #5658 #5653 #5676)

Each toy was run outside the sandbox on this branch. Wall time is the final green run.

| Toy | Before (exit, FAIL) | After (exit, FAIL, secs) | What changed |
|---|---|---|---|
| dev/toy/test-apply-rerender.py | 1, 8 | 0, 0, 43 | The Settings block now lives on docs/wiki/Home.md (README keeps it only when marked), so the toy edits, hand-edits and checks that file instead of README.md. Every assertion kept; the block must still carry its marker, the hand-edit control still refuses. |
| dev/toy/test-docs-command.sh | 1, 2 | 0, 0, 27 | Fixture repaired to the DOC-19 rules: a System diagram on the How-to page, a Home diagram block, an in-repo milestone link, and no DEL-2 item the feature page lacks. A new control breaks each repaired part and requires release.docs_trouble to reject it again. |
| dev/toy/test-docs-format.sh | 1, 8 | 0, 0, 83 | Fixture Follows cells are tagged bullets (DOC-23); the principle section names and sentences follow the six-principle list. Controls kept, plus new ones for an unbulleted entry and an unknown tag. |
| dev/toy/test-docs.sh | 1, 0 | 0, 0, 40 | The host app's session id (CLAUDE_CODE_HOST_SESSION_ID) leaked into the toy and broke the flow run; it is now unset like the other LOOP_ ids (verified: the old toy passes with it unset). New control: goal.py record refuses a step flow.py did not run. |
| dev/toy/test-criteria.sh | 1, 0 | 0, 0, 84 | Same cause and fix as test-docs.sh, with the same new control. |
| dev/toy/test-stale-code-page.py | 1, 3 | 0, 0, 11 | Lane prep now records the re-stamp in a dedicated "Kept: my-goal" commit touching only .loop/kept/my-goal.tsv, not in the page. Assertions check that commit, its content and that the page text is untouched; fixture page uses the current Requirements format. The negative control also requires the page is not in the kept fragment. |

No product bug found; no product script, regression row, known list or setting changed.
