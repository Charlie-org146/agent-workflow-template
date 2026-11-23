# Plan: v110-fast-reads-decl (DEL-26.2's declaration repair; v1.1.0 task 5, part 1 of 2), lines 2 and 5 of the path C split

This goal carries the built work of v110-fast-reads-static, narrowed to its lines 2 and 5, under the owner's record o858 (relayed by top, top's o873). Line 1 of the static goal (a change to one leaf script selects only the rows that read it) moves to the goal split-import-component and is reported unmet here, not worked on. The static goal's plan, gate-reviewed over its rounds, is the text this plan narrows; its text is not copied again. Measured at main c2ce6460a. The work is already built: the commit cherry-picked from the static goal (authored Charlie) carries the 24 declaration fix lines and the one corrected row.

## Frozen lines, read literally
1. Given main, `lanes_cli.py check` reports zero declaration problems (the static goal's line 2). The 24 fix lines (8 TREE, 7 PLACE, 4 GLOB, 2 NONE, 2 FOLDER-UNBACKED, 1 FOLDER) are cleared by one-line string replacements in dev/toy headers; the one fix line that is not a header edit is cleared by the ruled row change (TD1217): the row `defect-4375-toys-fake-machine` gets its corrected command, with its one line in dev/toy/approved-row-changes.tsv; its Given/when/then text and assertion stay word for word, and it stays green.
2. Given the package, every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES, no test is loosened, no existing row turns red, and committed text never names the service repo (the static goal's line 5, now line 2 here). `dev/toy/test-narrow.sh` does not grow.

## Constraints
No new rows. No selector edit (narrow.py, regression.py and lanes_cli.py are not touched). No new file under skills/. Edits are one-line string replacements per file, LF kept, no reflow (GRD-20). Toys use a temporary HOME; deletes only of absolute mktemp paths. A touched toy that would pass 19,000 stops the build before any code moves.

## What is built, in order
The build is the cherry-picked commit, so the build step has no code to write: it is checked. Order: (1) `lanes_cli.py check` exits 0 at the goal's head; (2) the corrected row and the approved-row-changes line are read against the ruling (TD1217); (3) per-file LF byte counts before and after for every changed file, against the limits above; (4) `private.py check` and `scan` before any PR text; (5) a grep that committed text never names the service repo; (6) the row `lanes-headers` (and `repo-narrow-178`, `narrow-root-172`) run on the Mac, serially, in a fresh clone at the pushed sha with a temporary HOME, as a run done by assignment recorded in this goal's own record (GRD-4). No local full lane. No `regression.yml` dispatch without the operation's go.

## Test homes (no new rows)
Line 1 is `lanes_cli.py check` exit 0, already asserted in dev/toy/test-tree.sh. Line 2 is the package check (`dev/package.py`), the size toys the lane runs and the per-file byte counts in the PR. No new case is needed: the existing cases keep passing unchanged, and a red one stops the goal and is reported.

## Behavior changes (also listed under `## Behavior changes` in the PR body)
One row command changes, under the ruling TD1217 (TD1103), with its one line in dev/toy/approved-row-changes.tsv. File: .loop/regression.tsv, row `defect-4375-toys-fake-machine`. Old command: the two `bash -c ". dev/toy/reap.sh; echo $LOOP_MACHINE" dev/toy/test-x.sh` calls; `dev/toy/test-x.sh` is a placeholder path that no toy has. New command: the same two calls with `dev/toy/test-govern.sh`, an existing toy that sources reap.sh. Before and after: the command is `bash -c ". dev/toy/reap.sh; echo $LOOP_MACHINE" <toy path>`, which only sources reap.sh with the toy path as `$0` (reap.sh reads `$0` for its windows-ok marker and its label) and prints `$LOOP_MACHINE`; it never runs the toy. Before, `$0` named a path that no toy has, so the check of the Windows marker pointed at nothing; after, `$0` names an existing toy (test-govern.sh, which sources reap.sh itself), so it checks reap.sh's floor default against a real caller. Run at this goal's head, the new command prints `64,64,10,0,0`. The two expected values (`64,64,10,0,0` with LOOP_MACHINE unset and `1,1,1,0,0` when set) and the row's Given/when/then text are unchanged word for word, so the assertion is not weakened; the row must stay green or the goal stops.

## Where the other half of the old goal goes
Line 1 of the static goal (selection counts for the three leaf scripts and the 307-row floor) is owned by the goal split-import-component. The link is its row in the operation's queue (.loop/queue.md, on the operation's checkout; this worktree's copy does not carry it yet) and the v1.1.0 release brief, revision 3, where v110-fast names it as a goal. This goal does not claim line 1 and closing it does not deliver it: v1.1.0 task 5 is not complete until split-import-component lands. The PR body and the closing note say so in those words, and the closing note names the queue row.

## Not in this goal
Line 1 of the static goal (selection counts per leaf script), the 307-row floor and its cause (the import component of the shipped scripts) go to split-import-component; the trace-proved work stays in v110-fast-reads-trace. The release brief names both.

## Estimate
Text-checked work already built: the checks and the Mac row run are the cost, about 40 minutes plus one red team and one pair of leak reads, about 50; an estimate, not a measurement. The 480-minute cap (o805) applies.

## Gates
The Mac's gate on this plan; then review, qa and ship lanes at the pushed sha (TD1038 pre-pr: `git status --porcelain` empty and HEAD equal to the lane's .ok). A plan counts as approved only after a clean independent gate.
