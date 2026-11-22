# The folder-trust check fails closed when the trust file can't be read (security patch for GRD-4; fixes #5741; owner o723)

- Slug: trust-fail-closed
- Touches: skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a trust file that is missing, unreadable or unparseable, then untrusted() treats every worktree as untrusted and bind refuses with a plain reason
2. Given a readable trust file that trusts the root, then binds work as after pc-path-trust (negative control)
3. Given the change, then checks green (docs, package, private-name), no existing row turns red, no test loosened, no new file under skills/

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. On a machine where the repository folder is trusted in Claude Code, bind a new goal to a worker session with `python3 skills/workflow-monitoring/scripts/sessions.py bind SLUG SESSION`.
   Expect: the bind goes through and prints BOUND with the session name.
2. Rename the trust file in your home folder (`.claude.json`) to another name, then bind another goal the same way, then rename it back.
   Expect: the bind prints `REFUSED: ask the owner to trust` followed by the worktree folder, `(FOLDER_TRUST)`, and the trust file name with "must be readable"; the trust file is not created by the bind.

## PR notes

What this changes: `untrusted()` in the operation script now fails closed (fixes #5741, security patch for GRD-4, owner record o723). A trust file that is missing, empty, unparseable, a directory, or without a `projects` map trusts nothing, so bind, assign and worker start refuse with `REFUSED: ask the owner to trust FOLDER (FOLDER_TRUST): open it once in Claude Code; PATH must be readable.` It reads the trust file where Claude keeps it: `$CLAUDE_CONFIG_DIR/.claude.json` when that variable is set, else `~/.claude.json` (top's TD884); the refusal names the file it read. A worker controls its own environment, so a worker that sets `CLAUDE_CONFIG_DIR` to a file it wrote can point the check there: the same same-user boundary as a worker's own HOME. The path logic from pc-path-trust (#5750) is kept. The owner's rule (o727), also written under `sessions.py bind` in docs/wiki/How-to-use-Guardrails.md: "a fresh machine must trust the repo once in the app before workers can start".

Deviations from the gated plan, stated plainly:
- Reader kept in operate.py (20,466 bytes after merging pc-path-trust, under the 20,480 fail line) instead of moved to machines.py, to stay under the 19,000 newly-crossing rule (test-pods.sh): moving it took machines.py from 18,927 to 19,912 bytes.
- Retry dropped, so a trust file caught mid-write now refuses the bind (fail closed) instead of retrying once after 0.2 s. Follow-up: #5751.
- Headroom: operate.py has 14 bytes left; machines.py 73 below its 19,000 line.

Upgraders trust once: a repo that bound before this lands has no trust entry the check can read, so its first bind is refused with the folder and the trust file named; open the folder once in Claude Code, then binds work. Nothing creates trust for the owner (o727). Toy cases for a new repo and an upgraded one are in test-new-binds.py (the refusal names the step, then bind goes through after it). The stray .loop/regression-runs.tsv change from the toy-setup commit is reverted (not in touches).

Red team: three fresh reviews, each recorded verbatim with `notify.py plan-record`. Autoplan was refused by its hook (init_unbindable, then "Existing restore does not match this initialization"), so the hand fallback ran at full depth. The six breaks (principles 1 to 6) are accepted as stated under owner record o727 ("trust-fail-closed may accept the red team's breaks as stated; a fresh machine must trust the repo once in the app before workers can start"). They include: writes to the trust file are out of scope (anything running as the same user can still write the file; this closes the read side only); a worker's own HOME can still redirect the read, the same trust boundary as before; the Windows path is unverified beyond pc-path-trust's simulation; a stale home file is not read when `CLAUDE_CONFIG_DIR` is set (only that directory's file counts); and a fresh machine has no trust file until the repo is trusted once in the app.

Tests, assert counts (main at 977f4f067 against this branch, by `check(` call lines):
- dev/toy/test-new-binds.py: 33 to 36. Three flipped, none dropped: "negative control: with no ~/.claude.json nothing is known, so bind goes through" now expects a readable trusting file; "negative control: with no ~/.claude.json no folder is called untrusted" likewise, plus a new "with no ~/.claude.json the bound session's worktree is MISSING folder trust, with its slug"; pc-path-trust's "wintrust a non dict entry and a malformed file give an empty answer without raising" now reads "... are refused without raising" (the row win-trust-prefix's grep text moved with it). Added: one helper, a loop of five unreadable shapes (missing, empty, garbage, directory, no projects), each asserting the whole refusal line and that the file is never written (10 runs).
- dev/toy/test-board-held.sh 74 to 74 and dev/toy/test-monitoring-prd.sh 77 to 77: one line each writes a trusting file into the toy's temporary HOME.
- New defect row defect-5741-trust-fail-closed (goal line 1, #5741): seen failing with the reader broken to fail open in a fresh clone, passing at the head.

- Windows path separator: operate.py prints the trust file as `expanduser("~/.claude.json")`, which keeps a slash on Windows (`C:\x\repo/.claude.json`), while the toy builds it with `os.path.join` (a backslash). The five unreadable-shape checks in dev/toy/test-new-binds.py now turn `/` into the platform separator on both the expected and the actual text, so the whole reason line must still match exactly except that one character; operate.py is unchanged.

Toys that fail identically on main at 977f4f067 (same counts at this branch; the lane's own run decides): test-board-held.sh 8 FAILED, test-monitoring-prd.sh 29 FAILED, test-operate.sh 14 FAILED (and a timeout), test-session-workers.sh 30 FAILED, test-workers.sh one failure ("pid: unbound variable"), test-defects-a.py ("no case", it needs a case argument), test-who-merges.py (mailbox.py starts merge.py). Without the one-line trusting file, board-held failed 14 and monitoring-prd 32 on this branch.

Checks at the build head: docs.py check --own DOCS OK (16 pages; Tests re-rendered, six pages restamped); private-name scan clean; test-new-binds.py and test-pods.sh pass. No lane had run when these notes were written.
