# Fixes #5700 and #5671 (Operation TD604): dev/toy/test-platform-limits.py and dev/toy/test-machine-log.py pick up the Mac's live session state (host and session variables, the real HOME, the real git common dir), so their rows platform-sends-counted and machine-status-live-workers fail in qa lanes on the Mac while passing on CI. Both toys run hermetically: the host and session variables unset, a throwaway HOME and git common dir, the #5671 hunk taken from hidden-red-fixes. No check removed or loosened Also Fixes #5704 (owner o687 rule, Operation TD623): the rows platform-sends-counted and machine-status-live-workers fail when their toy exits non-zero. Re-frozen as toy-hermetic-2, carrying toy-hermetic's commits.

- Slug: toy-hermetic-2
- Touches: dev/toy/test-platform-limits.py, dev/toy/test-machine-log.py, .loop/regression.tsv, docs/wiki
- ETA: 375 active minutes (estimate 297m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each toy run with the Mac's real session state, then it fails as today; run hermetically by its own setup, then it passes, and its rows platform-sends-counted and machine-status-live-workers pass in a qa lane on the Mac
2. Given each changed toy, then every assertion is kept, no check is skipped, and a control proves the toy still fails when its own subject is broken
3. Given this goal's diff, then only the two toys, the two rows platform-sends-counted and machine-status-live-workers in .loop/regression.tsv (and their rendered Tests lines) and the goal's own records change, the docs check passes and the private scan is clean
4. Given each of the rows platform-sends-counted and machine-status-live-workers, when its toy exits non-zero while still printing the PASS lines the row greps, then the row fails, re-proven red by a recorded break with regression.py red, and it passes on this branch run alone

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

Fixes #5671, #5665 and #5704. Refs #5700, #5705 and #5706.

What changes: dev/toy/test-platform-limits.py and dev/toy/test-machine-log.py run hermetically (no host session, loop or git location variable, a throwaway HOME, fixture repositories that are checked to be their own repository, no git templates or inherited git config), clean up after themselves, keep every earlier assertion, and add controls: a decoy-repository pair that proves the scrub matters, a canary per scrubbed variable family, a verified guard on the checkout's own operation id file (hashed and never written), a sentinel check, followed-repository discovery with a disposable registry, and the two row-matched PASS lines printed last. The rows platform-sends-counted and machine-status-live-workers in .loop/regression.tsv are changed in place (no new row) so each also requires its toy to exit 0 (#5704).

Re-proof of done line 4: each row was re-proven red with the regression tool's red command on a recorded break: the toy's final exit line becomes an exit with status 3 (`sed -i.bak 's/^sys.exit(1 if fails else 0)$/sys.exit(3)/'` on the toy), so the toy prints its PASS lines and exits non-zero and the row fails; the proof is the rows' seen_red field. Run alone on this branch, both rows pass.

Carry-over disclosure: the idea and plan records for this goal are carried over from goal toy-hermetic (Operation ruling TD624), whose plan ran at full depth on the same commits up to 971ff2b3e; the idea record was condensed. The #5704 row change was not part of that plan review; the review step ran fresh and covered it.

Review: full depth and fresh: seven specialists, a Claude and a Codex adversarial pass, four QA probes, and a fresh re-review of the fix commit; an independent review of 73d5ba790 passed. The full plan and review reports are kept outside the repo, per the leak rule.

Follow-ups, filed separately: #5705 (audit the seven other toys that name operation.id) and #5706 (a common launcher for the toys). Known limit: the hash guard on the real operation id file can report a false failure if another session legitimately writes that file during a run; its message names the sentinel result.
