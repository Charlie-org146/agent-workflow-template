# trust-fail-closed plan

Checked against origin/main (977f4f067): `operate.untrusted` is at operate.py line 127; callers are sessions.py (bind line 234, assign) and worker.py line 312.

## Implementation plan

1. Move the trust-file reader out of the full script (operation's answer to B6, no docstring cutting): new `untrusted(folder)` in `skills/workflow-monitoring/scripts/machines.py` (19,919 bytes, was 18,927, under the 20,480 fail line, warns past 19,000 as the others do); `operate.py` `untrusted()` keeps its name and callers and delegates to it (20,019 bytes, was 20,455: 436 freed). The reader (a) fails closed: a missing, unreadable, unparseable or projects-less file trusts nothing, and the refusal names the file it looked at; (b) honours `CLAUDE_CONFIG_DIR` (else the home folder); (c) retries once on a parse error, since the app may be mid-write. Trusted-root and trusted-parent logic unchanged. No new file. Done lines 1 and 2.
2. `dev/toy/test-new-binds.py` ("trust" and "restart" cases): the negative control "no ~/.claude.json, bind goes through" becomes the refusal case; add cases for an empty file, invalid JSON, a directory in its place and a file with no `projects` key; each refuses with "ask the owner to trust" and the file is never written. Keep the trusted-root and trusted-parent cases as the control. selfcheck: with no file the folder is named MISSING folder trust. Done lines 1 and 2.
3. Every other toy that binds, assigns or starts a worker under a temporary HOME gets a trusting `.claude.json` in that HOME (found by running them), so it tests what it tested; no assert is loosened or removed. Done line 3.
4. B5: one sentence in docs/wiki/How-to-use-Guardrails.md under `sessions.py bind` (trust the folder first; no readable trust file means bind refuses and names it). `.loop/regression.tsv`: a row for the fail-closed case with `regression.py add`, then `red --break`. Docs: one sentence where FOLDER_TRUST is described, if a page names the missing-file case (grep first).
5. Run docs, package and private-name checks; confirm no new file under skills/ and operate.py <= 20,480.

### Test for each done line
1. new toy cases (missing, empty, garbage, directory, no projects key) each refuse; 2. trusted root and trusted parent still bind; 3. checks green, git diff shows no new path under skills/.

### What could break
- Machines with no ~/.claude.json can no longer bind (intended; nothing is trusted).
- Toys relying on the fail-open default; found by running them in the lane. machines.py warns past 19,000 bytes (19,919).
- Merging pc-path-trust (#5722): it edits the same function; its logic must be carried into machines.untrusted (stop and report if the bytes do not hold).

### Out of scope
- #5743 case folding. The ~/.claude.json file is read only and never written.

## Review record

### Hand review, DEPTH: full (autoplan refused by its hook, init_unbindable; fallback per the goal order)

**CEO review.** Premise: a security check that returns "trusted" when it cannot read its input is a fail-open hole (GRD-4, #5741, owner o723); fixing it in the one shared function is the right size. Alternatives weighed: keep fail-open for a missing file only (rejected: the owner's words say missing, unreadable or unparseable all close it); add a bypass setting (rejected: a new knob in a security check, and bytes). Risk named: the file's location. Claude Code reads its config from ~/.claude.json unless CLAUDE_CONFIG_DIR moves it; on such a machine every bind now refuses with a message that points at trusting a folder, not at the file. #5743 and this are separate; I record CLAUDE_CONFIG_DIR as a follow-up for the owner, not in this goal (done lines freeze the scope). Verdict: build as planned.

**DevEx review.** Who is hurt: an operator whose bind refuses. Today's line says "ask the owner to trust X (FOLDER_TRUST)", right for a missing entry and misleading for an unreadable file. Requirement: if it fits in 20,480 bytes, the line also says the file may be unreadable (shorten the docstring to pay for it); if not, keep today's line. Third caller found: board_log.restart_lines (selfcheck) now also names "MISSING folder trust" for running goals when the file is unreadable: intended, and covered by the "restart" toy case.

**Eng review.** Callers: sessions.py bind and assign, worker.py:312, board_log.py:37. Every exception path of the try is closed: bad JSON and empty file (ValueError), missing file or a directory (OSError), no "projects" key (KeyError), "projects" null or a list, or a non-dict entry (AttributeError or TypeError), a NUL byte in a key (ValueError). The trusted-root and trusted-parent paths are unchanged in logic, so done line 2's control holds. Byte cap 20,480: trial 20,467. Tests: test-new-binds.py trust and restart cases (negative control flips), five file shapes, file never written; other toys that bind under a temporary HOME may need a trusting file: they cannot be run in the worktree (worker rule), so they run in the lane, one at a time, when operation gives a slot. Merge pc-path-trust (#5722) up when it lands; stop and report if the bytes do not hold.

<!-- autoplan-accepted:eng -->
- operate.py stays at or under 20,480 bytes; the refusal covers missing, empty, invalid, directory and no-projects files; no assert in any toy is loosened; no new file under skills/.
<!-- /autoplan-accepted:eng -->

### Red-team answers (plan-record taken; five BREAK lines)
- B1 (principle 1): accepted and stated. The flipped controls are the point of done line 1: each old assert that bind "goes through" with no file is replaced by its opposite and nothing is deleted or weakened; no other assert is touched. Fixtures gain a trusting file through ONE shared helper in the toy harness where a harness exists (the red team's cheaper path), not per-toy edits.
- B2 (principle 2): the new regression row is first run against the unfixed `untrusted()` (git stash is banned; the row runs in a lane clone detached at the parent commit with the new toy only) and must be seen red, then green at the fix.
- B3 (principle 3): no reformatting; only the one function's docstring wording changes, and only if the bytes need it.
- B5 (principle 5): goes to operation, not decided here: a machine with no trust file has no trust entry to create from this repo; Claude Code writes the entry when the owner trusts the folder, so the setup text should say so.
- B6 (principle 6): goes to operation: a message naming the unreadable file needs about 22 bytes against 13 spare; it fits only if the docstring is cut to one short line.
