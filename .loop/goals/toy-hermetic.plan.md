# Plan: toy-hermetic

## Implementation plan

Checked against the code: the two toys are `dev/toy/test-platform-limits.py` (row `platform-sends-counted`, land) and `dev/toy/test-machine-log.py` (row `machine-status-live-workers`, land), both in `.loop/regression.tsv`. The build is already committed (cfbcd143a and 6b10f26c7); this plan reviews and verifies that build and adds the small additions listed under Remaining build.

What the build does, per toy:

1. `test-machine-log.py`: before importing anything it drops every `CLAUDE*`, `ANTHROPIC*` and `LOOP_*` variable and `GIT_DIR`, `GIT_COMMON_DIR`, `GIT_WORK_TREE`, and points HOME and USERPROFILE at a throwaway directory. `run_loop` changes into the fixture directory so the wait loop's operation-session claim follows the fixture repo, never the checkout. New checks: no session id reaches the wait loop so it claims nothing; a negative control that a host session id left in the environment makes the wait loop claim, and the claim lands only in the fixture; the checkout's own `.git/loop/operation.id` hashes the same before and after.
2. `test-platform-limits.py`: `run()` builds the child environment without `LOOP_*`, `CLAUDE*`, `ANTHROPIC*` and the three git location variables, and with a throwaway HOME. New checks: with a host session id and GIT_DIR set in the parent environment the fixture still counts its send; the checkout's own operation id file is unchanged before and after.
3. Both toys keep every earlier assertion; nothing is skipped or loosened.

Test for each done line:

- Done line 1: with the Mac's real session state in the environment, each toy prints its OK line (`PLATFORM LIMITS TOY OK`; machine-log exits 0 with every PASS) and its row passes in a qa lane on the Mac. The "fails as today" half is shown by the negative controls: a leaked host session id changes the outcome unless the scrub is there.
- Done line 2: `git diff origin/main...HEAD -- dev/toy` removes no assertion line and adds no skip; each toy keeps its original negative controls and gains the controls above.
- Done line 3: `git diff origin/main...HEAD --stat` lists only the two toys and this goal's records (`.loop/goals/toy-hermetic.*`, `.loop/kept/`, `.loop/lane-results/`); `docs.py check --own` passes; the private scan is clean.

What could break:

- A state source the scrub does not cover (another variable family, another dotfile under HOME) would leak again; the controls fail only when the scrub is bypassed, not for a new source.
- The hash check reads the checkout's operation id file; it must only read it, never write or print it.
- Running either toy against the real operation id file from any other checkout is outside this goal (operator ban: run the toys only from this goal's worktree).

Frozen done lines, quoted: (1) "Given each toy run with the Mac's real session state, then it fails as today; run hermetically by its own setup, then it passes, and its rows platform-sends-counted and machine-status-live-workers pass in a qa lane on the Mac". (2) "Given each changed toy, then every assertion is kept, no check is skipped, and a control proves the toy still fails when its own subject is broken". (3) "Given this goal's diff, then only the two toys and the goal's own records change, the docs check passes and the private scan is clean".

Remaining build (CEO phase additions, autoplan-accepted; not yet in the code, one commit in the two toys, no assertion removed or loosened):

4. Cleanup: each toy defines `cleanup()` that removes its throwaway HOME and, in `test-platform-limits.py`, its fixture directory `top` as well (`shutil.rmtree(..., ignore_errors=True)`), registers it with `atexit`, and calls it once explicitly after the last existing check and before the `PLATFORM LIMITS TOY OK/FAILED` print (and, in `test-machine-log.py`, before `sys.exit`). It is followed by a check that the path is gone, placed after cleanup() and before that tally, so the cleanup itself is asserted and counted: `check(not os.path.exists(HOME), "...")` in `test-machine-log.py` (its `check(ok, text)` order) and `check("...", not os.path.exists(HOME))` in `test-platform-limits.py` (its `check(name, ok)` order), and in `test-platform-limits.py` a second one for `top` (a path-specific check, immune to other sessions' runs). Safety (Eng voices): `cleanup()` removes only a path it created itself with `tempfile.mkdtemp` (kept in a dedicated constant, never recomputed from `HOME` after the scrub), and refuses unless `os.path.realpath(path)` lies under `os.path.realpath(tempfile.gettempdir())` and is neither the real HOME nor the current directory; the toy changes into a safe directory before `cleanup()`, and the path-gone checks use `os.path.lexists`.
5. Operation-id guard, `test-machine-log.py` only (the sentinel `host-probe` can really reach an operation id file there, through `CLAUDE_SESSION_ID` and the wait loop's claim; `sends add` in `test-platform-limits.py` never writes operation.id, so that toy keeps only the byte-hash gate): `real_id_hash()` stays the gate, but it must be a verified guard (Eng voices): the common-directory discovery must succeed with a non-empty result (a failing `git rev-parse` is a FAIL line, not "absent"), the path is resolved once by `real_id_path()`, and only a missing file at a successfully discovered path hashes as "absent" (an unreadable file is a FAIL line); the parser comment pins the one-id-per-line format. A new `real_id_path()` helper returns the checkout's operation id file path and `real_id_hash()` calls it. `sentinel_in_real_id(path)` takes the path of an operation id file, reads it as one id per line (the format `operation_ids()` reads at `skills/workflow-monitoring/scripts/govern_hook.py:127`) and returns a boolean for whether `host-probe` is a line of it; an absent or unreadable file returns False; it never prints the file. The toy checks it against the checkout's real file (expect False) and, as its negative control, against the fixture's `operation.id` that the claim wrote: `run_loop` calls it on `os.path.join(common, "loop", "operation.id")` inside its `finally` block, before the temporary directory is removed, and returns that boolean beside `ids` (expect True for the host-probe run). When the byte-hash check fails, its message adds the sentinel result, so a toy leak (sentinel present) is told apart from another session's legitimate write (sentinel absent, or the file absent); both stay red. Taste: this is diagnosis only.
6. Scrub-matters control in `test-platform-limits.py` (taste; revised by the Eng voices to exercise a real cross-repository redirect): build a second disposable repository `decoy` exactly as `top` is built (`clean_env()` for `git init`, `.git/loop/runs`, `.loop/config.json`), set the parent `GIT_DIR` to `decoy/.git` inside `try/finally` (restored on every path), make the scrubbed `run(top, unattended, "sends", "add", "w")` call, then the same command by a direct `subprocess.run` with `cwd=top` and the environment `clean_env()` returns plus only that `GIT_DIR`. Assertions: after the scrubbed call `count(top)` is the previous count plus one and `count(decoy)` is unchanged (the scrub holds); after the unscrubbed call `count(decoy)` is its previous count plus one and `count(top)` is unchanged (the redirect really lands in the other repository, which is the hazard the scrub prevents). Both repositories live in the throwaway area, never the real checkout. Observables are the two counts (not the exit code); no fallback observable: if the unscrubbed call does not land in the decoy, the build stops and the plan is reopened. The existing control with the real `GIT_DIR` stays. (Read in the plan phase: `unattended.py:34-36` `common()` follows `git rev-parse --git-common-dir`, which honours `GIT_DIR`.)

8. Isolate every subprocess and in-process import in `test-platform-limits.py` (found by the Codex CEO voice, verified at `dev/toy/test-platform-limits.py:57` and `:117-118`): the build scrubs only the child environment `run()` builds, but `git init` (line 57) and the two warning probes (`probe`, lines 117-118) call `subprocess.run` with the inherited environment, so a host `GIT_DIR` could make `unattended.lines()` write `warned=True` into the repository the host variable names. The toy gets one `clean_env()` (the environment `run()` already builds, with the throwaway HOME) used by `run()`, by the `git init`, and by both probes (`env=clean_env()`); the toy itself then runs no subprocess with the inherited environment, and `test-platform-limits.py` has no in-process import of a skill module (only the `-c` probes, which are subprocesses). `clean_env()` also covers the size check's `git show origin/main:...` (`:143`, which otherwise falls back silently to a 20,000-byte baseline when a poisoned `GIT_DIR` makes it fail; a failed baseline retrieval prints a NOTE line) and the hash-discovery subprocess in both toys, and sets `GIT_CONFIG_NOSYSTEM=1` so a throwaway HOME does not change git behaviour. No assertion changes.
7. Scrub list (taste): both toys also drop `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` beside the three git location variables they already drop; no assertion changes.

9. Scrub checked against what the subject reads, plus a canary (taste; the allowlist alternative the native Eng voice proposed is recorded and deferred with C10): before building, the builder greps the environment variable names `govern_hook.py`, `unattended.py`, `operate.py` and `board.py` read, and the scrub drops every one of them; each toy also sets one canary variable per dropped family (`CLAUDE_TOY_CANARY`, `ANTHROPIC_TOY_CANARY`, `LOOP_TOY_CANARY`, `GIT_INDEX_FILE`) and asserts through a child that prints only booleans that none reaches it.
10. Row visibility in `test-machine-log.py` (taste, Eng Codex voice): the two `PASS:` lines `.loop/regression.tsv:661` greps are printed after every other check and cleanup have succeeded; if any check failed they print as `FAIL:` instead, so the existing row (which ignores the exit status) can no longer stay green while a later check fails. No check is removed; only when two lines are printed changes.
11. Followed-repository discovery in `test-machine-log.py` (taste, Eng Codex voice): in the `host-probe` run the toy writes the throwaway HOME's `~/.workflow-loop/repos` (the file `board.repo_file()` at `skills/workflow-monitoring/scripts/board.py:91` names, one path per line) with the path of a second disposable repository, and asserts the claim lands in both disposable repositories and the real operation id file stays unchanged.

Throwaway git common dir: it is the fixture repo's own `.git` that each toy already builds; the scrub of `GIT_DIR`, `GIT_COMMON_DIR` and `GIT_WORK_TREE` is what makes git resolve it.

Done line 1 is not claimed until the qa-lane result for both rows exists in `.loop/lane-results/`, and that evidence records each toy's own exit code and full output (the rows ignore the exit status). If the hold never lifts, done line 1 is reported partial with the controls evidence, never claimed. Its "fails as today" half is met only by the negative controls (session id in the environment; unscrubbed GIT_DIR) and the qa-lane row check on the Mac is run by this goal's qa step from this goal's worktree, after the operation session releases the hold; the plan step never runs the toys (operator ban).

Done line 3 is re-checked after the build: `git diff origin/main...HEAD --stat` must list only the two toys and `.loop/goals/toy-hermetic.*`, `.loop/kept/`, `.loop/lane-results/`.

Out of scope: any script under skills/, the regression table, any other toy, the toys' CI behavior. In particular seven other toys that name `operation.id` are not audited here (`dev/toy/test-delegated-records.py`, `test-govern-notes.py`, `test-monitoring-prd.sh`, `test-new-binds.py`, `test-pods.sh`, `test-restart-tick.py`, `test-token-diet.py`); they go to the final report as a follow-up, since this repo has no TODOS.md. The final report also lists, as the tracked follow-ups the owner or operation files (this goal files nothing): (a) an allowlist or common isolated launcher for all toys instead of per-toy denylists, (b) the same audit for the seven toys, (c) tightening the two rows (`.loop/regression.tsv:656` and `:661` check two PASS lines and ignore the toy's exit status, so later checks, including the new ones, cannot fail the row), which needs its own goal because done line 3 allows only the two toys and the goal's records.

PENDING: none for the owner.


<!-- autoplan-accepted:ceo -->
- Done lines 1 to 3 stay frozen (quoted in the plan) and are met by the two toys and the goal's records only; done line 3's diff check is re-run after the build.
- Remaining build item 4: each toy removes its throwaway HOME (and the platform-limits fixture) through `cleanup()` (atexit plus one explicit call before the OK/FAILED tally) and asserts the path is gone; no assertion is removed or loosened. Verify: the toy's own path-gone check passes and is counted.
- Remaining build item 5 (test-machine-log.py only, taste): `sentinel_in_real_id(path)` returns only a boolean (False for an absent or unreadable file); the checkout's real file must be False, the fixture file the claim wrote must be True (negative control); the byte-hash check stays the gate and its failure message adds the sentinel result.
- Remaining build item 6 (taste): in `test-platform-limits.py`, with the parent `GIT_DIR` set to a non-repository path, the scrubbed `sends add` counts the send and the unscrubbed direct call leaves the count unchanged, in the throwaway HOME against the fixture only. Verify: the control fails if the scrub of GIT_DIR is removed from `run()`.
- Remaining build item 7 (taste): both toys also drop `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES`; no assertion changes.
- Remaining build item 8: `test-platform-limits.py` uses one `clean_env()` for `run()`, the `git init` and both warning probes, so no subprocess inherits the host environment. Verify: with `GIT_DIR` set to a non-repository path in the parent, the toy's fixture setup and probes still pass and the byte-hash guard shows no real file changed.
- The seven other toys that name `operation.id` are not touched; they are in Out of scope and the final report, with the three tracked follow-ups (launcher, audit, row tightening).
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:eng -->
- Remaining build item 4 (safety): `cleanup()` removes only a `mkdtemp`-created path held in a dedicated constant, refuses unless it is under the real temp directory and is neither the real HOME nor the current directory, runs after a chdir to a safe directory, and the path-gone checks use `os.path.lexists`.
- Remaining build item 5 (verified guard): the common-directory discovery must succeed non-empty, an unreadable file is a FAIL line, only a missing file at a discovered path is "absent", and the path comes from one `real_id_path()`.
- Remaining build item 6 (revised, taste): `test-platform-limits.py` builds a second disposable repository `decoy`; with the parent `GIT_DIR` set to `decoy/.git` (try/finally) the scrubbed call counts in `top` and leaves `decoy` unchanged, and the unscrubbed direct call counts in `decoy` and leaves `top` unchanged. Verify: the control fails if the scrub of `GIT_DIR` is removed from `run()`.
- Remaining build item 8 (extended): `clean_env()` also covers the size check's `git show`, the hash-discovery subprocess in both toys and sets `GIT_CONFIG_NOSYSTEM=1`; `test-platform-limits.py` has no in-process import of a skill module.
- Remaining build item 9 (taste): the scrub drops every environment name the subject scripts read, and each toy asserts one canary per dropped family does not reach a child (booleans only).
- Remaining build item 10 (taste): `test-machine-log.py` prints the two row-matched `PASS:` lines only after all checks and cleanup succeed, otherwise `FAIL:`.
- Remaining build item 11 (taste): `test-machine-log.py` exercises followed-repository discovery with a disposable HOME registry and a second disposable repository, claim lands in both and the real file is unchanged.
- Done line 1 evidence records each toy's exit code and full output in `.loop/lane-results/`; if the hold never lifts, done line 1 is reported partial.
<!-- /autoplan-accepted:eng -->
## Review record

<!-- autoplan-baseline-edits:ceo {"sourceSha256":"c9fe5d7f14b818c66e8a00cd4c1f3fce62adece8678b174d90ddea8835df319e","replacements":[{"oldText":"this plan reviews and verifies it, it does not rewrite it.","newText":"this plan reviews and verifies that build and adds the small additions listed under Remaining build."},{"oldText":"Review additions (CEO phase, autoplan-accepted, all inside the two toys and the frozen done lines):\n\n4. Both toys remove their throwaway HOME directory when they finish (`atexit` + `shutil.rmtree(..., ignore_errors=True)`), so a run leaves nothing under the temp directory. No assertion changes.\n5. The operation-id guard in both toys also asserts that no sentinel session id the toy itself injected (`host-probe`) appears in the checkout's real `.git/loop/operation.id`; it reads the file and prints only booleans, never its contents. The byte-identical hash check stays as it is.\n6. `test-platform-limits.py` gains one control that proves the scrub matters (the \"fails as today\" half of done line 1): the same `sends add` call made with `GIT_DIR` pointing at a path that is not a repository (taken from the parent environment, not scrubbed) does not count its send, while the scrubbed call does. It runs in the throwaway HOME against the fixture only and never touches the real operation id file.\n\nOut of scope: any script under skills/, the regression table, any other toy, the toys' CI behavior.\n\n","newText":"Frozen done lines, quoted: (1) \"Given each toy run with the Mac's real session state, then it fails as today; run hermetically by its own setup, then it passes, and its rows platform-sends-counted and machine-status-live-workers pass in a qa lane on the Mac\". (2) \"Given each changed toy, then every assertion is kept, no check is skipped, and a control proves the toy still fails when its own subject is broken\". (3) \"Given this goal's diff, then only the two toys and the goal's own records change, the docs check passes and the private scan is clean\".\n\nRemaining build (CEO phase additions, autoplan-accepted; not yet in the code, one commit in the two toys, no assertion removed or loosened):\n\n4. Cleanup: each toy defines `cleanup()` that removes its throwaway HOME and, in `test-platform-limits.py`, its fixture directory `top` as well (`shutil.rmtree(..., ignore_errors=True)`), registers it with `atexit`, and calls it once explicitly after the last existing check and before the `PLATFORM LIMITS TOY OK/FAILED` print (and, in `test-machine-log.py`, before `sys.exit`). It is followed by a check that the path is gone, placed after cleanup() and before that tally, so the cleanup itself is asserted and counted: `check(not os.path.exists(HOME), \"...\")` in `test-machine-log.py` (its `check(ok, text)` order) and `check(\"...\", not os.path.exists(HOME))` in `test-platform-limits.py` (its `check(name, ok)` order), and in `test-platform-limits.py` a second one for `top` (a path-specific check, immune to other sessions' runs). Safety (Eng voices): `cleanup()` removes only a path it created itself with `tempfile.mkdtemp` (kept in a dedicated constant, never recomputed from `HOME` after the scrub), and refuses unless `os.path.realpath(path)` lies under `os.path.realpath(tempfile.gettempdir())` and is neither the real HOME nor the current directory; the toy changes into a safe directory before `cleanup()`, and the path-gone checks use `os.path.lexists`.\n5. Operation-id guard, `test-machine-log.py` only (the sentinel `host-probe` can really reach an operation id file there, through `CLAUDE_SESSION_ID` and the wait loop's claim; `sends add` in `test-platform-limits.py` never writes operation.id, so that toy keeps only the byte-hash gate): `real_id_hash()` stays the gate, but it must be a verified guard (Eng voices): the common-directory discovery must succeed with a non-empty result (a failing `git rev-parse` is a FAIL line, not \"absent\"), the path is resolved once by `real_id_path()`, and only a missing file at a successfully discovered path hashes as \"absent\" (an unreadable file is a FAIL line); the parser comment pins the one-id-per-line format. A new `real_id_path()` helper returns the checkout's operation id file path and `real_id_hash()` calls it. `sentinel_in_real_id(path)` takes the path of an operation id file, reads it as one id per line (the format `operation_ids()` reads at `skills/workflow-monitoring/scripts/govern_hook.py:127`) and returns a boolean for whether `host-probe` is a line of it; an absent or unreadable file returns False; it never prints the file. The toy checks it against the checkout's real file (expect False) and, as its negative control, against the fixture's `operation.id` that the claim wrote: `run_loop` calls it on `os.path.join(common, \"loop\", \"operation.id\")` inside its `finally` block, before the temporary directory is removed, and returns that boolean beside `ids` (expect True for the host-probe run). When the byte-hash check fails, its message adds the sentinel result, so a toy leak (sentinel present) is told apart from another session's legitimate write (sentinel absent, or the file absent); both stay red. Taste: this is diagnosis only.\n6. Scrub-matters control in `test-platform-limits.py` (taste; revised by the Eng voices to exercise a real cross-repository redirect): build a second disposable repository `decoy` exactly as `top` is built (`clean_env()` for `git init`, `.git/loop/runs`, `.loop/config.json`), set the parent `GIT_DIR` to `decoy/.git` inside `try/finally` (restored on every path), make the scrubbed `run(top, unattended, \"sends\", \"add\", \"w\")` call, then the same command by a direct `subprocess.run` with `cwd=top` and the environment `clean_env()` returns plus only that `GIT_DIR`. Assertions: after the scrubbed call `count(top)` is the previous count plus one and `count(decoy)` is unchanged (the scrub holds); after the unscrubbed call `count(decoy)` is its previous count plus one and `count(top)` is unchanged (the redirect really lands in the other repository, which is the hazard the scrub prevents). Both repositories live in the throwaway area, never the real checkout. Observables are the two counts (not the exit code); no fallback observable: if the unscrubbed call does not land in the decoy, the build stops and the plan is reopened. The existing control with the real `GIT_DIR` stays. (Read in the plan phase: `unattended.py:34-36` `common()` follows `git rev-parse --git-common-dir`, which honours `GIT_DIR`.)\n\n8. Isolate every subprocess and in-process import in `test-platform-limits.py` (found by the Codex CEO voice, verified at `dev/toy/test-platform-limits.py:57` and `:117-118`): the build scrubs only the child environment `run()` builds, but `git init` (line 57) and the two warning probes (`probe`, lines 117-118) call `subprocess.run` with the inherited environment, so a host `GIT_DIR` could make `unattended.lines()` write `warned=True` into the repository the host variable names. The toy gets one `clean_env()` (the environment `run()` already builds, with the throwaway HOME) used by `run()`, by the `git init`, and by both probes (`env=clean_env()`); the toy itself then runs no subprocess with the inherited environment, and `test-platform-limits.py` has no in-process import of a skill module (only the `-c` probes, which are subprocesses). `clean_env()` also covers the size check's `git show origin/main:...` (`:143`, which otherwise falls back silently to a 20,000-byte baseline when a poisoned `GIT_DIR` makes it fail; a failed baseline retrieval prints a NOTE line) and the hash-discovery subprocess in both toys, and sets `GIT_CONFIG_NOSYSTEM=1` so a throwaway HOME does not change git behaviour. No assertion changes.\n7. Scrub list (taste): both toys also drop `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` beside the three git location variables they already drop; no assertion changes.\n\n9. Scrub checked against what the subject reads, plus a canary (taste; the allowlist alternative the native Eng voice proposed is recorded and deferred with C10): before building, the builder greps the environment variable names `govern_hook.py`, `unattended.py`, `operate.py` and `board.py` read, and the scrub drops every one of them; each toy also sets one canary variable per dropped family (`CLAUDE_TOY_CANARY`, `ANTHROPIC_TOY_CANARY`, `LOOP_TOY_CANARY`, `GIT_INDEX_FILE`) and asserts through a child that prints only booleans that none reaches it.\n10. Row visibility in `test-machine-log.py` (taste, Eng Codex voice): the two `PASS:` lines `.loop/regression.tsv:661` greps are printed after every other check and cleanup have succeeded; if any check failed they print as `FAIL:` instead, so the existing row (which ignores the exit status) can no longer stay green while a later check fails. No check is removed; only when two lines are printed changes.\n11. Followed-repository discovery in `test-machine-log.py` (taste, Eng Codex voice): in the `host-probe` run the toy writes the throwaway HOME's `~/.workflow-loop/repos` (the file `board.repo_file()` at `skills/workflow-monitoring/scripts/board.py:91` names, one path per line) with the path of a second disposable repository, and asserts the claim lands in both disposable repositories and the real operation id file stays unchanged.\n\nThrowaway git common dir: it is the fixture repo's own `.git` that each toy already builds; the scrub of `GIT_DIR`, `GIT_COMMON_DIR` and `GIT_WORK_TREE` is what makes git resolve it.\n\nDone line 1 is not claimed until the qa-lane result for both rows exists in `.loop/lane-results/`, and that evidence records each toy's own exit code and full output (the rows ignore the exit status). If the hold never lifts, done line 1 is reported partial with the controls evidence, never claimed. Its \"fails as today\" half is met only by the negative controls (session id in the environment; unscrubbed GIT_DIR) and the qa-lane row check on the Mac is run by this goal's qa step from this goal's worktree, after the operation session releases the hold; the plan step never runs the toys (operator ban).\n\nDone line 3 is re-checked after the build: `git diff origin/main...HEAD --stat` must list only the two toys and `.loop/goals/toy-hermetic.*`, `.loop/kept/`, `.loop/lane-results/`.\n\nOut of scope: any script under skills/, the regression table, any other toy, the toys' CI behavior. In particular seven other toys that name `operation.id` are not audited here (`dev/toy/test-delegated-records.py`, `test-govern-notes.py`, `test-monitoring-prd.sh`, `test-new-binds.py`, `test-pods.sh`, `test-restart-tick.py`, `test-token-diet.py`); they go to the final report as a follow-up, since this repo has no TODOS.md. The final report also lists, as the tracked follow-ups the owner or operation files (this goal files nothing): (a) an allowlist or common isolated launcher for all toys instead of per-toy denylists, (b) the same audit for the seven toys, (c) tightening the two rows (`.loop/regression.tsv:656` and `:661` check two PASS lines and ignore the toy's exit status, so later checks, including the new ones, cannot fail the row), which needs its own goal because done line 3 allows only the two toys and the goal's records.\n\n"}]} -->

### CEO phase (autoplan, SELECTIVE EXPANSION, run 2026-11-20 by the toy-hermetic worker)

Provenance: mode set by /autoplan's override (SELECTIVE EXPANSION); no question was asked of the owner, every scope answer below is an authorized auto-decision (principles P1 to P6). Source: `.loop/goals/toy-hermetic.md` (frozen done lines), `.loop/goals/toy-hermetic.design.md`, `dev/toy/test-machine-log.py`, `dev/toy/test-platform-limits.py`, `skills/workflow-monitoring/scripts/operate.py`, `skills/workflow-monitoring/scripts/board.py`.

#### Decision ledger

| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| C1 scope: the fix lives in the two toys | done line 3; design Premises 1 to 3; `operate.py:277-296` reads cwd repo and env, so the leak is the toys' | scrub inside each toy (build 6b10f26c7) | unchanged | approved | auto-decision P3/P5, whole plan |
| C2 shared scrub helper | design Approach B; done line 3 allows only two toys | none | a third file | declined | auto-decision P4/P3: a third file breaks done line 3 |
| C3 remove the throwaway HOME at exit (serves the frozen done line 3's clean-run intent and the hermetic goal; cited as hygiene, optional) | both toys call `tempfile.mkdtemp` and never remove it (`test-machine-log.py` HOME line, `test-platform-limits.py` HOME line) | leaks one temp dir per run | `atexit` rmtree | approved | auto-decision P2/P1, additions 4; S, blast radius, no assertion change |
| C4 sentinel-absent guard on the real operation id | `real_id_hash()` only compares bytes; a hash mismatch cannot say whether the toy or another session wrote | hash only | hash plus sentinel check, booleans only | approved | auto-decision P1, addition 5; S |
| C5 control that the scrub matters (done line 1, "fails as today") | plan Test for done line 1 argues it only through leaked session id; no unscrubbed call exists in platform-limits | none | unscrubbed GIT_DIR control | approved (TASTE) | auto-decision P1, addition 6; surfaced at the final gate |
| C6 other toys name `operation.id` (7 files) | `grep -ln operation.id dev/toy/*` lists test-delegated-records.py, test-govern-notes.py, test-monitoring-prd.sh, test-new-binds.py, test-pods.sh, test-restart-tick.py, test-token-diet.py | untouched | audit them for the same leak | deferred | auto-decision P3: outside done line 3 and the plan's Out of scope; written to Out of scope and the final report (no TODOS.md exists in this repo) |
| C7 keep `LOOP_ROLE=worker` in the hermetic env | `operate.py:283-285` refuses a claim for a worker; the scrub drops LOOP_ROLE, so the refusal no longer protects, only the fixture cwd does | scrubbed | keep as scrubbed | approved (TASTE) | auto-decision P5: the control must be able to claim; the protection is the fixture cwd and the throwaway HOME, proven by C4 |

| C8 isolate git init and probes (Codex CEO voice, High) | `dev/toy/test-platform-limits.py:57,117-118` call subprocess with the inherited environment | only `run()` scrubbed | `clean_env()` everywhere | approved | auto-decision P1/P2, build item 8; in blast radius, a defect in the built toy |
| C9 tighten the two regression rows (Codex CEO voice, High) | `.loop/regression.tsv:656,661` grep two PASS lines and ignore the exit status | untouched | require exit 0 | deferred | auto-decision P3: done line 3 allows only the two toys and the goal's records; follow-up (c) in the final report |
| C10 allowlist or common launcher instead of denylists (native CEO voice, High) | plan 'What could break' admits new sources leak | denylist per toy | allowlist | deferred (TASTE) | auto-decision P3/P4: needs a shared contract and more than two files; follow-up (a) |
| C11 track the seven-toy follow-up (native and Codex, Medium) | no TODOS.md | final-report line | filed issue | deferred | this goal files nothing outward; the final report lists three follow-ups for the operation to file |

Approval readiness: PASS for rows C1 to C11 (each cites an auto-decision above; none needs the owner except as TASTE at the final gate).

#### 0A Premise challenge

Real problem: two regression rows fail in qa lanes on the Mac because the toys inherit the owner's live session state; the pain is a wasted try per goal. The plan fixes it directly (the toys stop reading that state) rather than a proxy (skip or retry). Do-nothing cost: every goal that touches these rows loses a try on the Mac and a false red teaches people to ignore the rows.

| premise | claim | file:line receipt | verdict |
|---|---|---|---|
| P-1 | the leak is in the toys, not in the scripts they test | `skills/workflow-monitoring/scripts/operate.py:277-296` (`cmd_claim` reads `os.environ`, cwd's git common dir and `board.followed()`), `skills/workflow-monitoring/scripts/board.py:95-107` (`followed` reads the cwd repo and `repo_file()`) | verified |
| P-2 | a scrub inside each toy is enough | `dev/toy/test-machine-log.py` (scrub block, `run_loop` chdir) and `dev/toy/test-platform-limits.py` (`run()` env) | verified for the known sources; unknown future sources unverified |
| P-3 | the rows and their commands stay as they are | `.loop/regression.tsv:656` and `:661` commands call the toys with no env wrapper | verified |
| P-4 | "fails as today" is shown by negative controls | plan Test for done line 1 | partly: shown for the session-id channel only; C5 closes the GIT_DIR channel |
| P-5 | the two toys are the only holders of the leak | `grep -ln operation.id dev/toy/*` lists nine files | unverified for the other seven (deferred, C6) |

unverified=2

#### 0B Existing code leverage and reality rows

| sub-problem | existing code | reuse |
|---|---|---|
| drop live session state | none shared; each toy builds its own env/os.environ scrub | per-toy copy (a helper is declined, C2) |
| fixture repo with its own common dir | `fixture()` in `test-machine-log.py` and `top` in `test-platform-limits.py` already exist | reused |
| hash the real operation id | `real_id_hash()` written in both toys | duplicated twice on purpose (done line 3 forbids a third file); noted as a 12-line duplicate, not extracted |

REALITY: premise-table finding premise table above, `unverified=2` (P-2 future sources, P-5 other toys) `dev/toy/test-machine-log.py:1`
REALITY: already-done pass `git fetch origin main` then `git log origin/main --since=2026-11-19 -- dev/toy/test-platform-limits.py dev/toy/test-machine-log.py` lists only older commits (c8f73ff07, 81775e2ad, f1e4889dd, 938d3e9f6); no hermetic fix is on main `dev/toy/test-platform-limits.py:1`
REALITY: surface-check pass every command the plan names exists: `docs.py check --own` (`skills/workflow-docs/scripts/docs.py`), `git diff origin/main...HEAD`, `flow.py` `skills/workflow-delivery/scripts/flow.py:1`
REALITY: binding-decisions pass the decision search over the last 50 branch decisions printed none for this branch and the plan has no Binding decisions section `.loop/goals/toy-hermetic.plan.md:1`
REALITY: numbers pass 2 live workers [measured: dev/toy/test-machine-log.py:86] `dev/toy/test-machine-log.py:86`
REALITY: numbers pass 7 stale busy records and 9 counted by the blind control [measured: dev/toy/test-machine-log.py:94] `dev/toy/test-machine-log.py:94`
REALITY: numbers pass 60 s heartbeat bound [measured: dev/toy/test-machine-log.py:170] `dev/toy/test-machine-log.py:170`
REALITY: deferred-asks pass no linked issue text was read in this run; #5671 and #5700 are named only by the goal title, the plan leaves out nothing the title asks `.loop/goals/toy-hermetic.md:1`
REALITY: pr-count pass one PR for the whole goal (two toys plus records) `.loop/goals/toy-hermetic.md:5`

#### 0C Dream state

```
  CURRENT STATE                      THIS PLAN                         12-MONTH IDEAL
  two toys read the Mac's    --->    each toy scrubs its own     --->  every toy under dev/toy runs from one
  live session state; rows           environment and proves it         hermetic harness (one scrub, one fixture
  go red only on the Mac             (controls, hash, sentinel)        factory); a lint fails any toy that reads
                                                                       HOME, host variables or the real common dir
```

The plan moves one step toward the ideal and deliberately stops at two toys (done line 3). The 12-month step (a shared hermetic harness) needs a goal of its own, so it is deferred, not built.

#### 0D alternatives

Settled by the design: A (scrub inside each toy) chosen; B (shared helper) declined (C2); C (`env -i` in the rows) declined because it edits the table and hides the leak; D (skip on the Mac) declined (removes checks). No new approach choice was needed.

#### 0E mode

`plan-ceo-review-mode: SELECTIVE EXPANSION` (autoplan override). Changed files: 2 toys plus the goal's records (estimate 2 toys, 5 record files). Fix/refactor would recommend HOLD SCOPE; /autoplan fixes the mode to SELECTIVE EXPANSION, so the expansion candidates below are neutral cherry-picks, each decided by the principles.

#### 0F/0G candidates (SELECTIVE EXPANSION)

HOLD checks: complexity (2 files, 0 classes: pass); minimum change is already built; nothing deferrable without losing a done line.

10x: a hermetic toy harness for every toy; delight scan: (a) remove the leaked temp HOME, (b) tell a failure apart (sentinel check), (c) prove the scrub matters, (d) one shared helper, (e) audit the other seven toys.

| # | Proposal | Effort | Decision | Reasoning |
|---|----------|--------|----------|-----------|
| 1 | remove the throwaway HOME at exit (C3) | S | ACCEPTED | in blast radius, one `atexit` line per toy, no new file |
| 2 | sentinel-absent guard (C4) | S | ACCEPTED | tells a toy leak from a legitimate write by another session |
| 3 | unscrubbed GIT_DIR control (C5) | S | ACCEPTED (TASTE) | closes the "fails as today" half of done line 1 |
| 4 | shared helper (C2) | M | SKIPPED | done line 3 allows two toys only |
| 5 | audit the other seven toys (C6) | M | DEFERRED | outside the frozen scope; recorded in NOT in scope |

#### 0I temporal interrogation

HOUR 1: the implementer must know the build is done and this is review plus three small additions; they need `real_id_hash()` and the HOME `mkdtemp` lines. HOUR 2-3: ambiguity: `atexit` order with the toys' own `sys.exit`; use `atexit.register` once at the top. HOUR 4-5: surprise: the control for C5 must not run the unscrubbed child with the real HOME (it must use the throwaway HOME) or it reads the owner's files. HOUR 6+: they will wish the sentinel check had a negative control (a fixture that writes the sentinel to a fixture operation id file and shows the check reports it). Effort: human ~1h / CC ~10min.


<!-- autoplan-accepted:ceo -->
- Done lines 1 to 3 stay frozen (quoted in the plan) and are met by the two toys and the goal's records only; done line 3's diff check is re-run after the build.
- Remaining build item 4: each toy removes its throwaway HOME (and the platform-limits fixture) through `cleanup()` (atexit plus one explicit call before the OK/FAILED tally) and asserts the path is gone; no assertion is removed or loosened. Verify: the toy's own path-gone check passes and is counted.
- Remaining build item 5 (test-machine-log.py only, taste): `sentinel_in_real_id(path)` returns only a boolean (False for an absent or unreadable file); the checkout's real file must be False, the fixture file the claim wrote must be True (negative control); the byte-hash check stays the gate and its failure message adds the sentinel result.
- Remaining build item 6 (taste): in `test-platform-limits.py`, with the parent `GIT_DIR` set to a non-repository path, the scrubbed `sends add` counts the send and the unscrubbed direct call leaves the count unchanged, in the throwaway HOME against the fixture only. Verify: the control fails if the scrub of GIT_DIR is removed from `run()`.
- Remaining build item 7 (taste): both toys also drop `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES`; no assertion changes.
- Remaining build item 8: `test-platform-limits.py` uses one `clean_env()` for `run()`, the `git init` and both warning probes, so no subprocess inherits the host environment. Verify: with `GIT_DIR` set to a non-repository path in the parent, the toy's fixture setup and probes still pass and the byte-hash guard shows no real file changed.
- The seven other toys that name `operation.id` are not touched; they are in Out of scope and the final report, with the three tracked follow-ups (launcher, audit, row tightening).
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:eng -->
- Remaining build item 4 (safety): `cleanup()` removes only a `mkdtemp`-created path held in a dedicated constant, refuses unless it is under the real temp directory and is neither the real HOME nor the current directory, runs after a chdir to a safe directory, and the path-gone checks use `os.path.lexists`.
- Remaining build item 5 (verified guard): the common-directory discovery must succeed non-empty, an unreadable file is a FAIL line, only a missing file at a discovered path is "absent", and the path comes from one `real_id_path()`.
- Remaining build item 6 (revised, taste): `test-platform-limits.py` builds a second disposable repository `decoy`; with the parent `GIT_DIR` set to `decoy/.git` (try/finally) the scrubbed call counts in `top` and leaves `decoy` unchanged, and the unscrubbed direct call counts in `decoy` and leaves `top` unchanged. Verify: the control fails if the scrub of `GIT_DIR` is removed from `run()`.
- Remaining build item 8 (extended): `clean_env()` also covers the size check's `git show`, the hash-discovery subprocess in both toys and sets `GIT_CONFIG_NOSYSTEM=1`; `test-platform-limits.py` has no in-process import of a skill module.
- Remaining build item 9 (taste): the scrub drops every environment name the subject scripts read, and each toy asserts one canary per dropped family does not reach a child (booleans only).
- Remaining build item 10 (taste): `test-machine-log.py` prints the two row-matched `PASS:` lines only after all checks and cleanup succeed, otherwise `FAIL:`.
- Remaining build item 11 (taste): `test-machine-log.py` exercises followed-repository discovery with a disposable HOME registry and a second disposable repository, claim lands in both and the real file is unchanged.
- Done line 1 evidence records each toy's exit code and full output in `.loop/lane-results/`; if the hold never lifts, done line 1 is reported partial.
<!-- /autoplan-accepted:eng -->

<!-- autoplan-baseline-edits:eng {"sourceSha256":"c9f686811afacc798299c50dfc9bcf377afff80aeb7e4b92770b16e36273c662","replacements":[{"oldText":"4. Cleanup: each toy defines `cleanup()` that removes its throwaway HOME and, in `test-platform-limits.py`, its fixture directory `top` as well (`shutil.rmtree(..., ignore_errors=True)`), registers it with `atexit`, and calls it once explicitly after the last existing check and before the `PLATFORM LIMITS TOY OK/FAILED` print (and, in `test-machine-log.py`, before `sys.exit`). It is followed by a check that the path is gone, placed after cleanup() and before that tally, so the cleanup itself is asserted and counted: `check(not os.path.exists(HOME), \"...\")` in `test-machine-log.py` (its `check(ok, text)` order) and `check(\"...\", not os.path.exists(HOME))` in `test-platform-limits.py` (its `check(name, ok)` order), and in `test-platform-limits.py` a second one for `top` (a path-specific check, immune to other sessions' runs).\n5. Operation-id guard, `test-machine-log.py` only (the sentinel `host-probe` can really reach an operation id file there, through `CLAUDE_SESSION_ID` and the wait loop's claim; `sends add` in `test-platform-limits.py` never writes operation.id, so that toy keeps only the byte-hash gate): `real_id_hash()` stays the gate; a new `real_id_path()` helper returns the checkout's operation id file path and `real_id_hash()` calls it. `sentinel_in_real_id(path)` takes the path of an operation id file, reads it as one id per line (the format `operation_ids()` reads at `skills/workflow-monitoring/scripts/govern_hook.py:127`) and returns a boolean for whether `host-probe` is a line of it; an absent or unreadable file returns False; it never prints the file. The toy checks it against the checkout's real file (expect False) and, as its negative control, against the fixture's `operation.id` that the claim wrote: `run_loop` calls it on `os.path.join(common, \"loop\", \"operation.id\")` inside its `finally` block, before the temporary directory is removed, and returns that boolean beside `ids` (expect True for the host-probe run). When the byte-hash check fails, its message adds the sentinel result, so a toy leak (sentinel present) is told apart from another session's legitimate write (sentinel absent, or the file absent); both stay red. Taste: this is diagnosis only.\n6. Scrub-matters control in `test-platform-limits.py` (taste): order: set the parent `GIT_DIR` to a path that is not a repository; make the scrubbed `run(top, unattended, \"sends\", \"add\", \"w\")` call (it must still count, proving the scrub); make the same command by a direct `subprocess.run` with `cwd=top` and the environment `run()` builds plus only that `GIT_DIR` (so the throwaway HOME stays and `CLAUDE*`/`LOOP_*` stay dropped; `sends add` then finds no common dir and records nothing, the early exit at `skills/workflow-monitoring/scripts/unattended.py:367`, which the builder confirms by reading it; read in the plan phase: `unattended.py:34-36` `common()` returns \"\" when `git rev-parse --git-common-dir` fails and `unattended.py:367` then exits with `REFUSED: not inside a git repository. Nothing was written.`, so the call records nothing); assert `count(top)` after the scrubbed call is the previous count plus one and after the unscrubbed call is unchanged; restore the parent environment. All in the throwaway HOME against the fixture, never the real one. The observable is fixed (the count, not the exit code); there is no fallback observable, and if the count does change the build stops and the plan is reopened. The existing control with the real `GIT_DIR` stays.\n\n8. Isolate every subprocess and in-process import in `test-platform-limits.py` (found by the Codex CEO voice, verified at `dev/toy/test-platform-limits.py:57` and `:117-118`): the build scrubs only the child environment `run()` builds, but `git init` (line 57) and the two warning probes (`probe`, lines 117-118) call `subprocess.run` with the inherited environment, so a host `GIT_DIR` could make `unattended.lines()` write `warned=True` into the repository the host variable names. The toy gets one `clean_env()` (the environment `run()` already builds, with the throwaway HOME) used by `run()`, by the `git init`, and by both probes (`env=clean_env()`); the toy itself then runs no subprocess with the inherited environment. No assertion changes.\n7. Scrub list (taste): both toys also drop `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` beside the three git location variables they already drop; no assertion changes.\n\nThrowaway git common dir: it is the fixture repo's own `.git` that each toy already builds; the scrub of `GIT_DIR`, `GIT_COMMON_DIR` and `GIT_WORK_TREE` is what makes git resolve it.\n\nDone line 1 is not claimed until the qa-lane result for both rows exists in `.loop/lane-results/`. Its \"fails as today\" half is met only by the negative controls (session id in the environment; unscrubbed GIT_DIR) and the qa-lane row check on the Mac is run by this goal's qa step from this goal's worktree, after the operation session releases the hold; the plan step never runs the toys (operator ban).\n\n","newText":"4. Cleanup: each toy defines `cleanup()` that removes its throwaway HOME and, in `test-platform-limits.py`, its fixture directory `top` as well (`shutil.rmtree(..., ignore_errors=True)`), registers it with `atexit`, and calls it once explicitly after the last existing check and before the `PLATFORM LIMITS TOY OK/FAILED` print (and, in `test-machine-log.py`, before `sys.exit`). It is followed by a check that the path is gone, placed after cleanup() and before that tally, so the cleanup itself is asserted and counted: `check(not os.path.exists(HOME), \"...\")` in `test-machine-log.py` (its `check(ok, text)` order) and `check(\"...\", not os.path.exists(HOME))` in `test-platform-limits.py` (its `check(name, ok)` order), and in `test-platform-limits.py` a second one for `top` (a path-specific check, immune to other sessions' runs). Safety (Eng voices): `cleanup()` removes only a path it created itself with `tempfile.mkdtemp` (kept in a dedicated constant, never recomputed from `HOME` after the scrub), and refuses unless `os.path.realpath(path)` lies under `os.path.realpath(tempfile.gettempdir())` and is neither the real HOME nor the current directory; the toy changes into a safe directory before `cleanup()`, and the path-gone checks use `os.path.lexists`.\n5. Operation-id guard, `test-machine-log.py` only (the sentinel `host-probe` can really reach an operation id file there, through `CLAUDE_SESSION_ID` and the wait loop's claim; `sends add` in `test-platform-limits.py` never writes operation.id, so that toy keeps only the byte-hash gate): `real_id_hash()` stays the gate, but it must be a verified guard (Eng voices): the common-directory discovery must succeed with a non-empty result (a failing `git rev-parse` is a FAIL line, not \"absent\"), the path is resolved once by `real_id_path()`, and only a missing file at a successfully discovered path hashes as \"absent\" (an unreadable file is a FAIL line); the parser comment pins the one-id-per-line format. A new `real_id_path()` helper returns the checkout's operation id file path and `real_id_hash()` calls it. `sentinel_in_real_id(path)` takes the path of an operation id file, reads it as one id per line (the format `operation_ids()` reads at `skills/workflow-monitoring/scripts/govern_hook.py:127`) and returns a boolean for whether `host-probe` is a line of it; an absent or unreadable file returns False; it never prints the file. The toy checks it against the checkout's real file (expect False) and, as its negative control, against the fixture's `operation.id` that the claim wrote: `run_loop` calls it on `os.path.join(common, \"loop\", \"operation.id\")` inside its `finally` block, before the temporary directory is removed, and returns that boolean beside `ids` (expect True for the host-probe run). When the byte-hash check fails, its message adds the sentinel result, so a toy leak (sentinel present) is told apart from another session's legitimate write (sentinel absent, or the file absent); both stay red. Taste: this is diagnosis only.\n6. Scrub-matters control in `test-platform-limits.py` (taste; revised by the Eng voices to exercise a real cross-repository redirect): build a second disposable repository `decoy` exactly as `top` is built (`clean_env()` for `git init`, `.git/loop/runs`, `.loop/config.json`), set the parent `GIT_DIR` to `decoy/.git` inside `try/finally` (restored on every path), make the scrubbed `run(top, unattended, \"sends\", \"add\", \"w\")` call, then the same command by a direct `subprocess.run` with `cwd=top` and the environment `clean_env()` returns plus only that `GIT_DIR`. Assertions: after the scrubbed call `count(top)` is the previous count plus one and `count(decoy)` is unchanged (the scrub holds); after the unscrubbed call `count(decoy)` is its previous count plus one and `count(top)` is unchanged (the redirect really lands in the other repository, which is the hazard the scrub prevents). Both repositories live in the throwaway area, never the real checkout. Observables are the two counts (not the exit code); no fallback observable: if the unscrubbed call does not land in the decoy, the build stops and the plan is reopened. The existing control with the real `GIT_DIR` stays. (Read in the plan phase: `unattended.py:34-36` `common()` follows `git rev-parse --git-common-dir`, which honours `GIT_DIR`.)\n\n8. Isolate every subprocess and in-process import in `test-platform-limits.py` (found by the Codex CEO voice, verified at `dev/toy/test-platform-limits.py:57` and `:117-118`): the build scrubs only the child environment `run()` builds, but `git init` (line 57) and the two warning probes (`probe`, lines 117-118) call `subprocess.run` with the inherited environment, so a host `GIT_DIR` could make `unattended.lines()` write `warned=True` into the repository the host variable names. The toy gets one `clean_env()` (the environment `run()` already builds, with the throwaway HOME) used by `run()`, by the `git init`, and by both probes (`env=clean_env()`); the toy itself then runs no subprocess with the inherited environment, and `test-platform-limits.py` has no in-process import of a skill module (only the `-c` probes, which are subprocesses). `clean_env()` also covers the size check's `git show origin/main:...` (`:143`, which otherwise falls back silently to a 20,000-byte baseline when a poisoned `GIT_DIR` makes it fail; a failed baseline retrieval prints a NOTE line) and the hash-discovery subprocess in both toys, and sets `GIT_CONFIG_NOSYSTEM=1` so a throwaway HOME does not change git behaviour. No assertion changes.\n7. Scrub list (taste): both toys also drop `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` beside the three git location variables they already drop; no assertion changes.\n\n9. Scrub checked against what the subject reads, plus a canary (taste; the allowlist alternative the native Eng voice proposed is recorded and deferred with C10): before building, the builder greps the environment variable names `govern_hook.py`, `unattended.py`, `operate.py` and `board.py` read, and the scrub drops every one of them; each toy also sets one canary variable per dropped family (`CLAUDE_TOY_CANARY`, `ANTHROPIC_TOY_CANARY`, `LOOP_TOY_CANARY`, `GIT_INDEX_FILE`) and asserts through a child that prints only booleans that none reaches it.\n10. Row visibility in `test-machine-log.py` (taste, Eng Codex voice): the two `PASS:` lines `.loop/regression.tsv:661` greps are printed after every other check and cleanup have succeeded; if any check failed they print as `FAIL:` instead, so the existing row (which ignores the exit status) can no longer stay green while a later check fails. No check is removed; only when two lines are printed changes.\n11. Followed-repository discovery in `test-machine-log.py` (taste, Eng Codex voice): in the `host-probe` run the toy writes the throwaway HOME's `~/.workflow-loop/repos` (the file `board.repo_file()` at `skills/workflow-monitoring/scripts/board.py:91` names, one path per line) with the path of a second disposable repository, and asserts the claim lands in both disposable repositories and the real operation id file stays unchanged.\n\nThrowaway git common dir: it is the fixture repo's own `.git` that each toy already builds; the scrub of `GIT_DIR`, `GIT_COMMON_DIR` and `GIT_WORK_TREE` is what makes git resolve it.\n\nDone line 1 is not claimed until the qa-lane result for both rows exists in `.loop/lane-results/`, and that evidence records each toy's own exit code and full output (the rows ignore the exit status). If the hold never lifts, done line 1 is reported partial with the controls evidence, never claimed. Its \"fails as today\" half is met only by the negative controls (session id in the environment; unscrubbed GIT_DIR) and the qa-lane row check on the Mac is run by this goal's qa step from this goal's worktree, after the operation session releases the hold; the plan step never runs the toys (operator ban).\n\n"}]} -->

#### Scope summary (CEO)

Plan under review: `.loop/goals/toy-hermetic.plan.md`. Vision: hermetic toys now, a shared harness later. Accepted scope: items 1 to 3 above. Deferred: item 5 (audit other seven toys), no TODOS.md exists so it goes to the final report as a follow-up. Skipped: item 4. Reviewer concerns: none yet.

#### CEO dual voices

Native CEO subagent: completed (INPUT: ceo f913e3d9...). Codex outside voice: completed (provider codex, model gpt-6-astra, OUTSIDE_STATUS completed, verdict FINDINGS, P1). VERDICT: claude-native: FINDINGS. VERDICT: codex: FINDINGS.

```
CEO DUAL VOICES — CONSENSUS TABLE:
  Dimension                             Claude                         Codex                         Consensus
  1. Premises valid?                    NO (denylist assumed complete) NO (scrubbed helper != isolation) CONFIRMED: plan premise P-2 too weak; fixed by item 8
  2. Right problem to solve?            YES (narrow, real)             YES (needs a durable path)    CONFIRMED yes
  3. Scope calibration correct?         partly (tracking out of scope) partly (row gate, tracking)   CONFIRMED: follow-ups listed, code scope kept
  4. Alternatives sufficiently explored?NO (allowlist, env -i)         NO (common launcher)          CONFIRMED: deferred follow-up (a)
  5. Competitive/market risks covered?  N/A (internal tooling)         N/A (internal tooling)        N/A
  6. 6-month trajectory sound?          NO (copies of a denylist)      NO (duplicated scrub lists)   CONFIRMED: follow-up (a)
```

Findings and dispositions: native 1 (denylist) deferred TASTE C10; native 2 and Codex 3 (tracking) deferred C11; native 3 (Mac qa gate) applied as plan text; native 4 (read line 367 now) applied; native 5 (item 5 machinery) kept as TASTE, surfaced at the gate; native 6 (cleanup mechanism) kept, hard-kill leak accepted; native 7 (wrapper idea) recorded as follow-up (a). Codex 1 (inherited-environment subprocesses) ACCEPTED as item 8 (C8); Codex 2 (rows ignore exit status) deferred C9. Single-voice criticals: Codex 1 was found by one voice only and verified by reading the toy.

#### Sections 1 to 11 (SELECTIVE EXPANSION)

Current scope: mode SELECTIVE EXPANSION (autoplan override); governing rows C1 to C11 (accepted: C1, C3, C4, C5, C7, C8; declined: C2; deferred: C6, C9, C10, C11).

**Section 1: Architecture.** Two independent toys, each a fixture plus a subject plus a guard; no new component, no shared code.

```
 parent env (host session vars, GIT_*, real HOME)
        |
   +----+-----------------------------+
   | toy process                      |
   |  scrub / clean_env() -> throwaway HOME, no CLAUDE*/ANTHROPIC*/LOOP_*/GIT_*loc
   |  fixture repo (tempdir) <--- subject (unattended.py / operate.py) cwd=fixture
   |  guard: real_id_hash() (read-only) + sentinel_in_real_id (machine-log)
   +----------------------------------+
        real .git/loop/operation.id  <-- only READ, never written
```

Data flow paths: happy (fixture counts or claims, guard unchanged); nil (no host session id: wait loop claims nothing, `ids == []`); empty (operation id file absent: hash is "absent", sentinel False); error (subject exits non-zero: toy check fails, row red). Scaling: n/a (fixtures per run). Single point of failure: the guard reads one file path computed from `git rev-parse --git-common-dir` run with GIT_* removed; if that fails the hash is "absent" before and after, a weaker guard (noted: the fixture cwd and throwaway HOME remain the protection). Rollback: revert two toy files, minutes. Security: no new endpoint; the toy must never print the operation id contents. Value test: the guard artifact is consumed by the row's pass or fail and retires if a shared launcher lands. Platform potential: a shared launcher (follow-up a).

**Section 2: Error and rescue map.**

```
  METHOD/CODEPATH            | WHAT CAN GO WRONG               | EXCEPTION CLASS
  ---------------------------|---------------------------------|------------------
  real_id_hash/real_id_path  | git missing or fails            | OSError, CalledProcess (returncode ignored)
                             | file unreadable                 | OSError
  sentinel_in_real_id        | absent/unreadable file          | OSError
  cleanup()                  | rmtree fails                    | OSError (ignore_errors)
  scrubbed git init (item 8) | git init fails                  | none raised (capture_output)
  unscrubbed-GIT_DIR control | sends add records unexpectedly  | assertion
  --------------------------------------------------------------------------
  EXCEPTION CLASS | RESCUED? | RESCUE ACTION                         | USER SEES
  OSError (id)    | Y        | return "absent"/False                 | guard still compares equal; documented weaker guard
  OSError (rmtree)| Y        | ignore_errors, then asserted gone     | FAIL line if the dir remains
  git init fails  | N ← GAP  | fixture has no .git, later checks fail| FAIL lines (noisy but not silent)
  assertion       | Y        | FAIL line, exit 1                     | row red
```

One GAP: a failing `git init` is not checked directly; follow-on checks fail loudly, so it is not silent. Accepted (P3), listed in the failure modes registry.

**Section 3: Security and threat model.** Attack surface: none added (test-only). Input validation: the sentinel is a fixed literal. Authorization: the toys must not write the real operation id file; the hash guard and cwd=fixture protect it; the operator ban stands. Secrets: the toy never prints environment variables or the id file; the control reads booleans only. Dependencies: stdlib only. Injection: the probe string embeds `scripts` through `%r`, a path the toy itself computes. Audit: none needed. Findings: 1 (Low likelihood, High impact): a hole that lets the toy write real state (the inherited-environment subprocesses), mitigated by item 8. 1 High-severity finding, mitigated.

**Section 4: Data flow and interaction edge cases.** Flow: `INPUT(env) -> VALIDATION(scrub) -> TRANSFORM(fixture run) -> PERSIST(fixture only) -> OUTPUT(PASS/FAIL lines)`; shadow paths: nil/empty env (fine), wrong type (n/a), exception/timeout (subprocess `timeout` not set in the toy: a hung subject hangs the row; the row has the lane's timeout), conflict (concurrent runs: the cleanup assertion is path-specific, the hash guard can be tripped by another session's legitimate claim, diagnosis added in item 5), stale/partial/encoding (n/a). Async ordering: none (single process). Edge cases: 6 mapped (host id present, GIT_DIR a file in a linked worktree, operation id absent, two sessions racing the real file, rmtree failure, hard kill leaves temp dirs), 1 unhandled (hard kill, accepted).

**Section 5: Code quality.** 12-line `real_id_hash` is duplicated in both toys by design (a third file breaks done line 3); naming fine; no method over 5 branches except `run_loop` (3). Over-engineering: item 5 is the thinnest value (TASTE, surfaced). Under-engineering: the inherited-environment subprocesses (fixed by item 8). Issues found: 2.

**Section 6: Test review.** Diagram of what the plan adds:

```
  NEW THING                         TEST TYPE   HAPPY                       FAILURE                          EDGE
  scrub + throwaway HOME            integration scrubbed run passes         host id left in env => claim     GIT_DIR file in worktree
  cleanup() (item 4)                unit        path gone check             rmtree fails => FAIL line        hard kill (accepted)
  sentinel_in_real_id (item 5)      unit        real file False             fixture file True (control)      absent file False
  clean_env() everywhere (item 8)   integration fixture setup + probes pass GIT_DIR non-repo in parent       -
  unscrubbed GIT_DIR pair (item 6)  integration scrubbed counts, unscrubbed unchanged  count changed => build stops  -
  GIT_INDEX_FILE etc. (item 7)      integration child never sees them     -                                -
```

Gaps: none within the accepted scope; each behaviour has an assertion, a wrong result it rejects and a `no_claim`: the toys prove hermeticity against the variable families they scrub, `no_claim=unknown future state sources`. 2am-Friday test: the byte-hash guard plus qa-lane run; hostile QA: host `GIT_DIR` and `CLAUDE_SESSION_ID` set (items 6, 8); chaos test: parallel runs (cleanup assertion is path-specific). Pyramid: all integration by nature. Flakiness: the byte-hash check can fail on another session's real write (diagnosis added); no time or network dependence. No LLM or prompt change.

**Section 7: Performance.** One extra `git init`/temp dir per run; negligible; no queries, caches or pools. 0 issues.

**Section 8: Observability.** The toy's own PASS/FAIL lines are the signal; the failure message adds the sentinel result; no logs or metrics needed for a toy. Runbook: if the hash guard fails, read the sentinel result: present => this toy leaked, stop and report; absent => another session wrote the file, rerun. 0 gaps.

**Section 9: Deployment.** No migration or flag; ships through the normal PR; rollback is a revert; post-merge check: both rows green in the next nightly (which runs on CI where none of the Mac state exists) and in a qa lane on the Mac. 0 risks.

**Section 10: Long-term trajectory.** Debt: per-toy denylists (code debt, follow-up a), rows that ignore exit status (testing debt, follow-up c), seven unaudited toys (operational debt, follow-up b). Reversibility 5/5. 1-year question: obvious if the Remaining build items stay commented. Retrospective: the accepted cherry-picks were right (item 8 was load-bearing); the rejected shared helper turned out to be the real fix, deferred honestly.

**Section 11: Design.** SKIPPED (no UI scope).

#### NOT in scope

- Shared scrub helper or common launcher (declined C2, deferred C10): done line 3 allows two toys only.
- Audit of the seven other toys (deferred C6) and tracking them as filed issues (deferred C11): outside the frozen scope; the final report carries them.
- Tightening the two regression rows (deferred C9): `.loop/regression.tsv` is outside done line 3.
- Allowlist environment (deferred C10, TASTE).

#### What already exists

`fixture()` and `top` fixtures (reused), `real_id_hash()` (reused and extended), `unattended.common()` early refusal (reused as the control's observable), `check()` helpers (reused). Nothing is rebuilt.

#### Dream state delta

The plan makes two toys hermetic and proves it; the 12-month ideal (one hermetic harness, a lint over every toy, rows that enforce exit status) stays three follow-ups away.

#### Error and rescue registry and failure modes

See Section 2's table. Failure modes registry:

```
  CODEPATH                  | FAILURE MODE                | RESCUED? | TEST? | USER SEES?        | LOGGED?
  real_id_hash              | git fails -> "absent" twice | Y (weak) | N     | nothing (guard weaker) | N  <- noted, no critical gap: cwd+HOME still protect
  cleanup() rmtree          | dir remains                 | Y        | Y     | FAIL line         | Y
  scrubbed git init         | git init fails              | N        | Y (follow-on checks) | FAIL lines | Y
  sentinel_in_real_id       | file absent/unreadable      | Y        | Y     | False             | Y
  unscrubbed GIT_DIR pair   | observable differs          | Y        | Y     | build stops       | Y
```

Critical gaps: 0 (the first row is RESCUED=Y, USER SEES=nothing, but it is the pre-existing weak guard, covered by the fixture cwd and throwaway HOME).

#### Diagrams, stale diagram audit

Produced: system architecture, data flow with shadow paths, error flow (tables), test diagram. State machine, deployment sequence and rollback flowchart: N/A (no stateful object, deploy is a normal merge, rollback is `git revert`). Stale diagram audit: the toys carry no ASCII diagrams; the plan file's diagrams are new. 0 stale.

#### Implementation tasks

- [ ] **T1 (P1, human: ~1h / CC: ~10min)**: dev/toy/test-platform-limits.py: `clean_env()` for `run()`, `git init` and both probes (item 8); scrub list (item 7); cleanup (item 4); the GIT_DIR control pair (item 6). Surfaced by: Codex CEO voice finding 1; CEO 0I. Files: dev/toy/test-platform-limits.py. Verify: toy prints `PLATFORM LIMITS TOY OK` from this worktree with `GIT_DIR` set to a non-repository path in the parent.
- [ ] **T2 (P1, human: ~45min / CC: ~10min)**: dev/toy/test-machine-log.py: cleanup (item 4), `real_id_path()`/`sentinel_in_real_id` (item 5), scrub list (item 7). Surfaced by: CEO 0F candidates 1 and 2. Files: dev/toy/test-machine-log.py. Verify: toy exits 0 with every PASS from this worktree.
- [ ] **T3 (P2, human: ~15min / CC: ~3min)**: final report lists the three follow-ups (launcher/allowlist, seven-toy audit, row tightening). Surfaced by: both CEO voices. Files: none. Verify: the report names them.

Reality check, Completion Summary and the report follow after the Eng phase (single terminal report).

```
  +====================================================================+
  |            MEGA PLAN REVIEW — COMPLETION SUMMARY                   |
  +====================================================================+
  | Mode selected        | SELECTIVE EXPANSION                         |
  | System Audit         | 2 toys, 7 others name operation.id, no TODOS.md |
  | Step 0               | SELECTIVE EXPANSION; 4 accepted, 1 skipped, 1 deferred (+3 from voices) |
  | Section 1  (Arch)    | 1 issue found                               |
  | Section 2  (Errors)  | 6 error paths mapped, 1 GAP (git init)      |
  | Section 3  (Security)| 1 issue found, 1 High severity (mitigated)  |
  | Section 4  (Data/UX) | 6 edge cases mapped, 1 unhandled            |
  | Section 5  (Quality) | 2 issues found                              |
  | Section 6  (Tests)   | Diagram produced, 0 gaps                    |
  | Section 7  (Perf)    | 0 issues found                              |
  | Section 8  (Observ)  | 0 gaps found                                |
  | Section 9  (Deploy)  | 0 risks flagged                             |
  | Section 10 (Future)  | Reversibility: 5/5, debt items: 3           |
  | Section 11 (Design)  | SKIPPED (no UI scope)                       |
  +--------------------------------------------------------------------+
  | NOT in scope         | written (4 items)                           |
  | What already exists  | written                                     |
  | Dream state delta    | written                                     |
  | Error/rescue registry| 6 rows, 0 CRITICAL GAPS                     |
  | Failure modes        | 5 total, 0 CRITICAL GAPS                    |
  | TODOS.md updates     | 0 (no TODOS.md; follow-ups in the report)   |
  | Scope proposals      | 6 proposed, 4 accepted (EXP + SEL)          |
  | CEO plan             | written (the CEO scope summary, outside the repo) |
  | Outside voice        | codex completed                             |
  | Lake Score           | N/A (no scored questions asked)             |
  | Diagrams produced    | 4 (architecture, data flow, error flow, test) |
  | Stale diagrams found | 0                                           |
  | Unresolved decisions | 0                                           |
  | Reality rows         | 7/7 rows (PLAN_REALITY), 2 unverified       |
  +====================================================================+
```

#### Phase 2 and Phase 2.5 skip records

Phase 2 (Design Review) skipped: no UI scope detected (`scope.uiRequired` false: the matches "row" and "list" are not UI evidence). Phase 2.5 (DX Review) skipped: no developer-facing scope detected (`dxRequired` false, 0 term matches, not a developer tool, no agent as primary user). Neither is a completed review.

### Eng phase (autoplan, run 2026-11-20 by the toy-hermetic worker)

Native eng subagent: completed (INPUT: eng b8a2b7cc...). Codex outside voice: completed (gpt-6-astra, OUTSIDE_STATUS completed, FINDINGS P1). VERDICT: claude-native: FINDINGS. VERDICT: codex: FINDINGS. Dual voices and sections all ran at full depth (`review_depth: full`); `Scope challenge: never reduce (P2)`.

#### Step 0 Scope Challenge

Complexity: changed files 2 toys (plus goal records), 0 new classes or services: below 8 files and 2 classes, so complexity questions B are skipped; result `scope accepted as-is` (MODE FULL_REVIEW). What already solves each sub-problem: `fixture()`/`top` fixtures, `real_id_hash()`, `unattended.common()` (`unattended.py:34`), `board.followed()` (`board.py:95`), the toys' `check()` helpers; nothing new is built that exists. Minimum change: the build is done; the additions are small and inside the toys. Search check: no new architectural pattern (stdlib `tempfile`, `shutil`, `atexit`, `subprocess`) [Layer 1]. TODOS cross-reference: this repo has no TODOS.md; nothing blocks this plan. Distribution check: no artifact, no CI/CD change (toys are not in the package).

REALITY: premise-table pass premises P-1..P-5 from the CEO phase hold; new: `platform-limits has no in-process import of a skill module` verified `dev/toy/test-platform-limits.py:8`, `unverified=1` (the `GIT_DIR`-lands-in-decoy behaviour of the unscrubbed call, confirmed by reading `skills/workflow-monitoring/scripts/unattended.py:34-36` but not run) `dev/toy/test-platform-limits.py:93`
REALITY: already-done pass `git log origin/main --since=2026-11-19 -- dev/toy/test-platform-limits.py dev/toy/test-machine-log.py` shows no hermetic fix on main `dev/toy/test-machine-log.py:1`
REALITY: surface-check pass named commands and flags exist: `git rev-parse --git-common-dir`, `git show origin/main:<path>`, `os.path.lexists`, `tempfile.mkdtemp`, `unattended.py sends add` `skills/workflow-monitoring/scripts/unattended.py:34`
REALITY: binding-decisions pass no binding decisions are recorded for this branch (the decision search printed none) and the plan has no Binding decisions section `.loop/goals/toy-hermetic.plan.md:1`
REALITY: numbers pass 20 send cap and 15-of-20 warning threshold [measured: dev/toy/test-platform-limits.py:112] `dev/toy/test-platform-limits.py:112`
REALITY: numbers pass 20,000-byte fallback baseline [measured: dev/toy/test-platform-limits.py:145] `dev/toy/test-platform-limits.py:145`
REALITY: deferred-asks pass no linked issue text was read; #5671 and #5700 appear only in the goal title and the plan leaves out nothing it asks `.loop/goals/toy-hermetic.md:1`
REALITY: pr-count pass one PR for the goal (two toys plus records) `.loop/goals/toy-hermetic.md:5`

#### Eng dual voices

```
ENG DUAL VOICES — CONSENSUS TABLE:
  Dimension                           Claude                          Codex                             Consensus
  1. Architecture sound?              YES, denylist weak (allowlist)  NO (guard can pass vacuously)    DISAGREE-in-part: both found a guard weakness; fixed by items 5, 9
  2. Test coverage sufficient?        NO (control can pass wrongly)   NO (rows ignore new checks)      CONFIRMED: items 6, 10, 11 and follow-up (c)
  3. Perf risks + budget named?       N/A (no hot path)               N/A                              N/A
  4. Security threats covered?        NO (rmtree safety)              NO (cross-repo write path)       CONFIRMED: items 4, 6, 11
  5. Error paths handled?             NO (cwd, unreadable file)       NO (discovery failure = absent)  CONFIRMED: items 4, 5
  6. Deployment risk manageable?      YES (revert)                    YES                              CONFIRMED yes
```

Dispositions (auto-decided; each a row in the ledger below): native 1 accepted (item 4 safety); native 2 accepted in its cheap form (item 9: drop every name the subject reads, canary), allowlist deferred (C10); native 3 resolved (verified no in-process import, stated in item 8); native 4 accepted in part (item 5 verified guard; hash stays the gate per the design, sentinel is diagnosis); native 5 accepted (item 6 revised to the decoy repository, an assertion that cannot pass vacuously); native 6 accepted (item 4 ordering, lexists, safe cwd); native 7 deferred to follow-up (c) plus evidence text under done line 1; native 8 accepted (`GIT_CONFIG_NOSYSTEM=1`); native 9 accepted (partial-claim fallback text); native 10 accepted (canary). Codex 1 accepted (item 5); Codex 2 accepted as item 10 (TASTE); Codex 3 accepted (item 8 extended); Codex 4 accepted (item 6 decoy); Codex 5 accepted as item 11 (TASTE). Single-voice criticals: native 1 (`rmtree` safety) and Codex 3 (`git show` fallback) were each raised by one voice and verified by reading the toy.

| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| E1 cleanup safety (native, High) | `shutil.rmtree` is destructive; plan item 4 | bare rmtree | guarded rmtree | approved | auto-decision P5/P1, item 4 |
| E2 verified guard (Codex, High) | `real_id_hash()` treats a failed git call as "absent" twice | weak guard | verified guard | approved | auto-decision P1, item 5 |
| E3 scrub scope (native, High) | subject reads only LOOP_*/CLAUDE_* names plus HOME (`grep os.environ` over four scripts) | denylist | drop all names read + canary | approved (TASTE) | auto-decision P3/P5, item 9; allowlist stays deferred (C10) |
| E4 cross-repo control (native 5, Codex 4) | control could pass vacuously | non-repo GIT_DIR | decoy repository pair | approved (TASTE) | auto-decision P1, item 6 |
| E5 `git show` and discovery env (Codex 3) | `:143` inherits env | inherited | clean_env | approved | auto-decision P1, item 8 |
| E6 row visibility (Codex 2) | `.loop/regression.tsv:661` ignores later checks | row green on later FAIL | PASS lines printed last | approved (TASTE) | auto-decision P1, item 10 |
| E7 followed-repo discovery (Codex 5) | `board.followed()` reads `~/.workflow-loop/repos` | untested | disposable registry control | approved (TASTE) | auto-decision P1, item 11 |
| E8 hash flake (native 4) | another session's legitimate write turns it red | byte hash gate | gate + diagnosis | approved | auto-decision P3, item 5 (design keeps the hash) |
| E9 git config under throwaway HOME (native 8) | no identity or safe.directory | unspecified | `GIT_CONFIG_NOSYSTEM=1` | approved | auto-decision P5, item 8 |
| E10 done line 1 fallback (native 9) | depends on the hold lifting | unspecified | partial claim fallback | approved | auto-decision P5, plan text |

Approval readiness: PASS for rows E1 to E10 (each cites an auto-decision above).

#### Section 1: Architecture

Dependency graph (new and existing):

```
  test-platform-limits.py ──subprocess(clean_env)──> unattended.py ──> common() ──> git rev-parse (GIT_DIR honoured)
        │  fixtures: top, decoy (disposable repos, mkdtemp)        └─> sends.json in the repo git resolves
        └─ guard: real_id_hash/real_id_path (read-only) ──> real .git/loop/operation.id
  test-machine-log.py ──in-process(import operate, layers)──> operate.cmd_claim ──> board.followed() ──> ~/.workflow-loop/repos (throwaway HOME)
        │  fixture repo + second disposable repo; cwd = fixture; claim lands only in disposable repos
        └─ guard: same read-only operation id check + sentinel_in_real_id
  cleanup(): mkdtemp-created paths only, under realpath(tempdir), never HOME or cwd
```

Coupling: none new between toys (two copies of a 12-line guard, by design). Scaling: n/a. Single points of failure: the guard's discovery subprocess (now verified, not "absent"). Security: the toys can only write disposable repositories; the real operation id file is read-only. Production failure: another session claims during the run (hash red, diagnosis names it). Rollback: revert two files. Design-twice: no new module, service or boundary: one line, skipped. Red flags: 5 split ownership: none; 6 two ways to do one task: two copies of the guard (accepted, done line 3); 8 hand-synced list: the scrub family list lives in two toys (item 9 makes a canary assert it, follow-up (a) removes it). Issues found: 2 (denylist coverage, guard verification), both resolved by items 5 and 9.

#### Section 2: Code quality

DRY: the guard and scrub are duplicated across the two toys (two files, 12 and 6 lines); extraction would be a third file, declined by done line 3, so net: accepted debt with follow-up (a). Naming: `real_id_path`, `sentinel_in_real_id`, `clean_env`, `cleanup` describe what they do. Complexity: `run_loop` gains one return value (callers: 3 in one file, updated together); no new method over 5 branches. Error handling: item 4 and 5 specify the failure modes. Touched-file diagrams: the toys carry none. Issues found: 2 (the cleanup guard, the discovery-failure-as-absent defect), both resolved.

#### Section 3: Test review

```
CODE PATHS                                                  USER FLOWS (operator flows)
[+] dev/toy/test-platform-limits.py                         [+] qa lane on the Mac
  ├── clean_env()                                             ├── [GAP→ evidence] row run with real session state: result in .loop/lane-results/
  │   ├── [★★★ new] canary var per family dropped            └── [GAP] hold never lifts: done line 1 reported partial (text only)
  │   └── [★★ new] GIT_CONFIG_NOSYSTEM
  ├── decoy redirect pair (item 6)
  │   ├── [★★★ new] scrubbed: top+1, decoy unchanged
  │   └── [★★★ new] unscrubbed: decoy+1, top unchanged
  ├── git init / probes / git show under clean_env           [+] dev/toy/test-machine-log.py
  │   └── [★★ new] fixture setup passes with poisoned GIT_DIR  ├── [★★★ new] host-probe claim lands in fixture + registry repo
  ├── cleanup() (item 4)                                       └── [★★★ new] real file unchanged (hash) + sentinel False
  │   ├── [★★★ new] path gone (lexists) for HOME and top
  │   └── [★★ new] refuses outside tempdir (unit-style assert on the guard)
  └── real_id_hash: [★★★ new] discovery failure is a FAIL, not "absent"

[+] dev/toy/test-machine-log.py (continued)
  ├── sentinel_in_real_id(path): [★★★ new] real False, fixture True (negative control), absent file False
  ├── PASS-line gating (item 10): [★★★ new] a failing late check makes the two row-matched lines FAIL
  └── followed-repository discovery (item 11): [★★★ new]

COVERAGE (new paths): 14/16 tested by the plan (88%)  |  GAPS: 2 (the two operator flows, which are done-line-1 evidence, not code)
QUALITY: ★★★:9 ★★:5 ★:0  |  E2E: the qa-lane row run [→E2E]
```

Value cards (one per critical path and edge case, in the test plan artifact):

Value: protects=a host GIT_DIR cannot redirect the toy's sends into another repo; fails_when=the scrub of GIT_DIR is removed from clean_env; why_new=the build has only a non-redirect control; seam=none; no_claim=other state sources (only the names the subject reads are proven)
Value: protects=the toy deletes only paths it created; fails_when=cleanup targets HOME or cwd or a path outside tempdir; why_new=no cleanup exists in the build; seam=none; no_claim=a hard kill still leaves temp dirs
Value: protects=the operation id guard cannot pass vacuously; fails_when=git discovery fails and the guard still reports success; why_new=build returns "absent" on any OSError; seam=none; no_claim=a legitimate write by another session still turns it red (diagnosis names it)
Value: protects=the machine-log row goes red when any later check fails; fails_when=a late check fails and the two PASS lines still print; why_new=`.loop/regression.tsv:661` ignores the exit status; seam=none; no_claim=the row still ignores the exit status for other toys

Regression rule: the existing assertions are the preserved behaviour; each addition lists the wrong result it rejects above. LLM/eval scope: none (no prompt or LLM change). Tests made obsolete: none. Flakiness: the hash gate (diagnosis added); no time/network dependence besides the existing fake clock. Pyramid: integration by nature; no E2E beyond the qa-lane run. Test plan artifact: written (eng review test plan, 20261120-204538, outside the repo). Gaps: 2, both resolved by plan text. Issues found: 5 (E3, E4, E6, E7, E1), all dispositioned above.

#### Section 4: Performance

No hot path; each run adds two or three `git init` calls and a few temp directories (tens of milliseconds); no budget or bench step is needed for a toy that already runs in under a second. Memory: none. Caching: none. Slow paths: the qa-lane run is the existing row. Issues found: 0 (examined the added subprocess count, the temp directory footprint and the guard's single file read).

#### NOT in scope

Allowlist environment or common isolated launcher (deferred C10, follow-up a); audit of the seven other toys (deferred, follow-up b); tightening the two regression rows and their exit-status handling (deferred C9, follow-up c); any script under `skills/`; creating TODOS.md (none exists; the follow-ups go to the final report).

#### What already exists

`fixture()`/`top` fixtures, `real_id_hash()`, the toys' `check()` helpers, `unattended.common()` and `board.followed()` as the behaviours under test: reused, nothing rebuilt.

#### Failure modes registry

```
  CODEPATH                    | FAILURE MODE                         | RESCUED? | TEST? | USER SEES?                 | LOGGED?
  cleanup() rmtree            | wrong path (HOME or cwd)             | Y (guard)| Y     | refuses, FAIL line         | Y
  real_id_hash discovery      | git rev-parse fails                  | Y        | Y     | FAIL line (was silent)     | Y
  real_id_hash unreadable file| OSError                              | Y        | Y     | FAIL line                  | Y
  decoy redirect control      | unscrubbed call does not land in decoy| Y       | Y     | build stops, plan reopened | Y
  clean_env git show          | git show fails under clean env       | Y        | Y     | NOTE line, 20,000 fallback | Y
  machine-log late FAIL       | row stays green                      | Y (item 10)| Y   | FAIL instead of PASS lines | Y
  git init under clean_env    | fails (no HOME config)               | Y        | Y     | follow-on checks FAIL      | Y
```

Critical gaps: 0.

#### Worktree parallelization strategy

Sequential implementation, no parallelization opportunity: both toys are independent files but one builder commit covers both and each change is under 100 lines.

#### TODOS.md updates

No TODOS.md exists and creating one would add a file outside done line 3. The three deferred follow-ups (allowlist or launcher, seven-toy audit, row tightening) are proposed to the operation in the final report; 0 items written.

#### Implementation tasks (aggregated with the CEO tasks)

- [ ] **T1 (P1, human: ~1.5h / CC: ~15min)** — test-platform-limits.py — `clean_env()` everywhere (`git init`, probes, `git show`, hash discovery), decoy redirect control, canaries, cleanup with safety. Surfaced by: Eng sections 1 and 3; Codex eng 3 and 4; native eng 1, 5, 6. Files: dev/toy/test-platform-limits.py. Verify: toy prints `PLATFORM LIMITS TOY OK` from this worktree, also with a non-repository `GIT_DIR` in the parent.
- [ ] **T2 (P1, human: ~1.5h / CC: ~15min)** — test-machine-log.py — verified guard, sentinel function, registry-discovery control, PASS-line gating, canaries, cleanup. Surfaced by: Eng sections 1 and 3; Codex eng 1, 2, 5. Files: dev/toy/test-machine-log.py. Verify: toy exits 0 with every PASS; a forced late failure turns the two row-matched lines into FAIL.
- [ ] **T3 (P2, human: ~20min / CC: ~5min)** — qa evidence — record each toy's exit code and full output in `.loop/lane-results/` at qa. Surfaced by: native eng 7 and 9. Files: .loop/lane-results/. Verify: the files exist before done line 1 is claimed.
- [ ] **T4 (P3, human: ~1h / CC: ~10min)** — final report — name the three follow-ups for the operation to file. Surfaced by: both CEO and both Eng voices. Files: none. Verify: the report lists them.

```
  +====================================================================+
  |             ENG REVIEW — COMPLETION SUMMARY                        |
  +====================================================================+
  | Step 0: Scope Challenge     | scope accepted as-is                |
  | Reality rows                | 7/7 emitted, 1 unverified premise    |
  | Architecture Review         | 2 issues found                       |
  | Code Quality Review         | 2 issues found                       |
  | Test Review                 | diagram produced, 2 gaps identified  |
  | Performance Review          | 0 issues found                       |
  | NOT in scope                | written                              |
  | What already exists         | written                              |
  | TODOS.md updates            | 0 items written (no TODOS.md)        |
  | Failure modes               | 0 critical gaps flagged              |
  | Unresolved decisions        | 0 in this review                     |
  | Outside voice               | codex completed                      |
  | Parallelization             | 1 lane, 0 parallel / 1 sequential    |
  | Lake Score                  | N/A (no scored questions asked)      |
  +====================================================================+
```

### Decision Audit Trail (autoplan)

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|----------------|-----------|-----------|----------|
| 1 | CEO | scrub inside each toy (C1) | Mechanical | P3/P5 | design Approach A | env -i in the rows, skip on the Mac |
| 2 | CEO | shared helper declined (C2) | Mechanical | P4 | done line 3 allows two toys | third file |
| 3 | CEO | cleanup of throwaway dirs (C3) | Mechanical | P1/P2 | blast radius, no assertion change | leave temp dirs |
| 4 | CEO | sentinel guard (C4, item 5) | Taste | P1 | diagnosis for a red hash | drop it |
| 5 | CEO | unscrubbed control (C5, item 6) | Taste | P1 | "fails as today" half of done line 1 | rely on the session-id control |
| 6 | CEO | audit of seven toys deferred (C6) | Mechanical | P3 | outside frozen scope | audit now |
| 7 | CEO | clean_env for git init and probes (C8, item 8) | Mechanical | P1 | inherited-environment hole found by Codex | leave |
| 8 | CEO | row tightening, allowlist, tracking deferred (C9, C10, C11) | Taste | P3/P4 | outside done line 3 | edit the table now |
| 9 | Eng | cleanup safety (E1) | Mechanical | P5 | destructive delete | bare rmtree |
| 10 | Eng | verified guard (E2) | Mechanical | P1 | vacuous pass | absent-on-error |
| 11 | Eng | denylist from reads plus canary (E3, item 9) | Taste | P3/P5 | subject reads only LOOP_*, CLAUDE*-style, HOME state | allowlist now |
| 12 | Eng | decoy-repository pair (E4, item 6 revised) | Taste | P1/P5 | cannot pass vacuously | non-repository GIT_DIR |
| 13 | Eng | clean_env for git show and discovery (E5) | Mechanical | P1 | silent 20,000 fallback | leave |
| 14 | Eng | PASS-line gating (E6, item 10) | Taste | P1 | row ignores exit status | leave blind |
| 15 | Eng | registry discovery control (E7, item 11) | Taste | P1 | cmd_claim follows repositories | skip |
| 16 | Eng | hash stays the gate (E8) | Mechanical | P3 | design keeps it | sentinel as gate |

## Review result (summary; the full autoplan report is kept outside the repo)

- CEO review (SELECTIVE EXPANSION): ran at full depth with the native and Codex voices; 6 proposals, 4 accepted, 1 deferred; 5 of 6 dimensions confirmed, 0 disagreements.
- Eng review: ran at full depth with the native and Codex voices; 11 issues, 0 critical gaps; 4 of 6 confirmed, 1 partial disagreement resolved as taste decisions.
- Design and DX reviews skipped by scope (no UI, no developer-facing scope).
- 16 decisions in all (10 auto-decided, 6 taste, 0 user challenges); the plan was amended with remaining build items 4 to 11 inside the two toys; depth: full.
- Open for the owner: approval of the amended plan.
- Deferred follow-ups (for the PR body): (a) a common toy launcher or allowlist, (b) an audit of the seven toys that name operation.id, (c) rows 656 and 661 ignore the toy's exit status.
