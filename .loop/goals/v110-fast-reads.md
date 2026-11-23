# Repair the test rows' reads declarations so a change selects only the rows it reaches (v1.1.0 task 5, DEL-26.2's prerequisite)

- Slug: v110-fast-reads
- Touches: dev/toy, .loop/regression.tsv, skills/workflow-regression, docs/wiki
- ETA: 380 active minutes (estimate 303m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a change to one leaf script, then the real lanes_cli.py affected --level land on the real table selects only the rows that read it, directly or through imports, plus the declared always-rows; a toy asserts bounded counts for three named leaf scripts (board_page.py, wiki.py and one release script), with today's counts as the red baseline.
2. Given main, then lanes_cli.py check reports zero declaration problems.
3. Given every row, then its declared reads cover what its command runs (never fewer): the reads-coverage check passes and no existing row turns red.
4. Given the always-rows, then each states why it reads the whole tree, and there are no more than today's 48.
5. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
