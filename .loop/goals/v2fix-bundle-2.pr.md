# v2fix-bundle-2: six reviewed fixes, the toys' reads headers and four defect rows

One bundle, as the coordinator asked (Operation TD585). Each fix passed its own Claude review before it joined and keeps its own defect row. To undo one fix, revert its commits (listed below); each revert needs `criteria.py render` afterwards for Tests.md and Delivery.md. To undo everything, revert the merge commit with `git revert -m 1`.

Fixes #5344
Fixes #5308
Fixes #5078
Fixes #5359
Fixes #5346
Fixes #5317
Fixes #5635
Fixes #5638
Fixes #5702

Refs #5679 (the rerun-fraction part stays with #5694; the header part is #5702).

## What each fix does
- #5344, `pool.py`: a pr-queue goal with no recorded touches takes them from its branch diff (renames at both ends; an unreadable diff still overlaps everything). Commits 8d031134c, 65c5e848b, 6e5e938bf. Row `pr-no-touches-from-diff`. The review of this branch added a guard: a base from the goal's own `.loop/config.json` that starts with `-` or is not a string is ignored (it reached `git diff` as an option and could write a stray file), and the diff ends with `--`; three cases in the toy.
- #5308: the DOC-1 sync pointer check reads the pointer by requirement ID, not by one sentence. Commits 945f3c697, faaafbdac, 552f4f290. Row `doc1-sync-pointer-by-id`.
- #5078, `prdcopy.py`: an own-repo GitHub image (blob, raw or raw.githubusercontent.com) for a file that exists in the repo counts as inside; another repo's image and a missing path are still reported. Commits 6c715436a, 9ace8ec4a, 87bb4854b. Row `defect-5078-own-repo-image`.
- #5359, `flow.py`: the end-of-step token write merges through `goal.save` and no longer wipes fields the operation session set in between. Commit 7fe22add7. Row `worker-save-5359`.
- #5346, `merge.py` and `graph.py`: a waiter behind the merge lock is refused past `LOOP_MERGE_LOCK_SECONDS` and the holder is named (pid, goal, age). Commits 1e67fa5d1, 7431f21e2. Row `merge-lock-wait-refused`.
- #5317, `wiki.py`: `prepare --commit` commits the START.md, CLAUDE.md and AGENTS.md that the audit regenerates, and only those. Row `defect-5317-wiki-start`; its row now requires the toy's whole result (exit status and no FAIL line), not its first PASS line.
- #5702 (the header part of #5679): the toys' `# reads:` headers, so `lanes_cli.py check` is clean. Row `defect-5679-reads-headers`.
- Defect rows for work that was fixed elsewhere: `defect-5635-settings-default` (#5635, already fixed on main; this adds its defect row) and `defect-5638-reconcile-wording` (#5638, already fixed on main; this adds its defect row); each is proven by its recorded break. `defect-88-closing-keywords` is linked to the merged pull request 88 (a pull request, not an issue, so nothing closes it) and proves the closing-keyword behaviour that pull request built.

## #5317: picked, reverted, re-picked
It was picked at the start of this bundle, then reverted while its own review was still open, at the coordinator's word. After its final Claude review passed (tip 153fde437 on its own branch), its ten work, row and Kept commits were cherry-picked again with `-x`. Content check done: wiki.py, test-wiki-start.sh and its Kept record are identical to that reviewed tip, and the row line was byte-identical before the row was strengthened here. The earlier pick and revert commits stay in the history.

## What is not fixed, and why
- `dev/toy/test-tree.sh` still has one FAIL, the rerun fraction (a change to one file reruns too many rows). It needs a product redesign (#5694), so it is out of scope; #5679 stays open for it.
- `lanes-headers` and the other known rows are untouched.
- pool.py (20,215 bytes), prdcopy.py (20,223) and wiki.py (20,426) are over the 19,000-byte warning line and under the 20,480 fail line (GRD-20); no script reaches the fail line, and none was trimmed. wiki.py has 54 bytes left; a follow-up to split cohesive parts out of these three is not filed here.
- #5350 stays separate (not carried).

## How it was checked
- The full autoplan plan review (CEO and Eng phases, each with a native and a Codex reviewer) ran under the retired goal v2fix-bundle on the same commit range, 48ac06e7d..df10c7b98, before this goal took the same commits over; the plan is `.loop/goals/v2fix-bundle-2.plan.md`. Its idea and plan steps were recorded here from that run on Operation's ruling (TD612). The review of this goal ran fresh: six specialists, a native and a Codex adversarial pass, three smoke probes.
- Every carried row passes with the session's CLAUDE*, ANTHROPIC* and LOOP_* variables unset (they otherwise bind the toy goals to the session); the rows changed in this goal were seen failing again on a recorded break.
- A merge commit keeps every carried commit message, and two of them (3e99eefac and 60396593a) carry a closing phrase for issue 5679: after the merge, confirm 5679 is still open.
