# v2fix-bundle: five reviewed fixes, the toys' reads headers, and four defect rows

Each carried fix kept its own defect row and its own Kept record. Each passed its Claude review before it joined.
#5317 was carried and then held at the coordinator's word (reverted with `git revert`); #5350 is not carried yet.

## #5344: a pr-queue goal with no touches
- What: a goal with no recorded touches took its pr turn behind every earlier goal and made every later one wait on it. It now takes its touches from its branch diff, with renames and an error fallback.
- Root cause: pool.py treated "no touches" as "touches everything".
- Row: `pr-no-touches-from-diff` (toy `dev/toy/test-pr-parallel.py`), seen failing then passing.
- Review: PASS.

## #5308: the DOC-1 sync pointer
- What: the check reads the sync pointer by requirement ID, not by one sentence of DOC-1.
- Root cause: the row matched DOC-1's wording, so rewording DOC-1 broke it.
- Row: `doc1-sync-pointer-by-id` (toy `dev/toy/test-doc1-sync-pointer.py`), seen red recorded, with a harder meaning check.
- Review: PASS.

## #5078: DOC-19 own-repo images
- What: an own-repo GitHub image (blob, raw or raw.githubusercontent.com) for a file that exists in the repo counts as inside; another repo's image and a missing path are still reported. One extension list, so the gap-wave1 break applies.
- Root cause: prdcopy.py read every GitHub image URL as outside the repo.
- Row: `defect-5078-own-repo-image` (toy `dev/toy/test-stands-alone.py`; `test-gap-wave1.py` still passes).
- Review: PASS.

## #5359: flow.py's token write
- What: flow.py's end-of-step token write merges through goal.save instead of saving the whole run record.
- Root cause: the whole-record save wiped fields the operation session set between the read and the write (a budget set by goal.py).
- Row: `worker-save-5359` (toy `dev/toy/test-worker-save.sh`).
- Review: PASS. The reviewer's wording note: the How-to-use-Delivery "Writes:" line should also say the `updated` stamp is written (not changed here; for the page's owner).

## #5346: merge.py waiting on the merge lock
- What: merge.py refuses past LOOP_MERGE_LOCK_SECONDS and names the merge-lock holder. A stuck holder is still taken over at 1800 s (main's rule); this adds the refusal, not a new takeover. merge.py is 18,996 B and graph.py 18,982 B, at their limits.
- Root cause: the wait loop on graph.merge_lock never gave up and never said who held it.
- Row: `merge-lock-wait-refused` (`bash dev/toy/test-pods.sh lock`).
- Review: PASS.

## #5679: the toys' reads headers, and the three missing defect tests
- What: `lanes_cli.py check` is clean. Headers moved into the leading comment block (6 toys); folders the toys glob declared (5); the two unbacked `skills/` lines removed (docs-link, prd-copy); `test-govern.sh` got a header; `skills/` is declared only by the toys that really read all of it (cp -R, grep -r, a glob over every skill, or an agent given the whole skills folder: body-file, portable, guards-null-report, health-prd, machine, merge-batch, merge-guard, migration, govern). The row `defect-4375-toys-fake-machine` named a script that does not exist (`test-x.sh`) as a stand-in `$0`; it now uses `toy-x.sh`. test-tree.sh's full-clone check matched `.github/` as a path inside `.git`; it now matches `.git/` exactly.
- Root cause: headers drifted as toys grew, and nothing ran `lanes_cli.py check` where a failure blocked.
- Rows: `defect-5679-reads-headers`, and for test-tree's three missing defect tests: `defect-88-closing-keywords`, `defect-5635-settings-default`, `defect-5638-reconcile-wording`. #5635 and #5638 were fixed on main (#5636, #5639); each row has a recorded `regression.py red --break` proof. #88 is a merged pull request, not an issue; the adopt-closing-keywords goal uses "#88" as an example, so its row proves the closing-keywords behaviour that goal built.
- Not fixed: test-tree's "one-file change reruns fewer than half the land rows" (634 of 646 rows for a change to batch.py; the Python import graph links the skills; it fails on main too and is a known row, lanes-headers).

Fixes #5344, #5308, #5078, #5359, #5346

Refs #5679: `lanes_cli.py check` is clean, but `dev/toy/test-tree.sh` still has one FAIL (`lanes-headers`), which needs a `narrow.py` or `lanes.py` change that is out of scope here, so the issue stays open.
Refs #5635 and #5638: already fixed on main (#5636, #5639); each new defect row (`defect-5635-settings-default`, `defect-5638-reconcile-wording`) is proven by its recorded break.
#88 is a merged pull request, not an issue: no closing line.
#5317 was picked, then reverted with `git revert` at the coordinator's word, and is not part of this change.
