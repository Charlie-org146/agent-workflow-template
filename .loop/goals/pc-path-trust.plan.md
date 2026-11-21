# Plan: Windows worktree paths are trusted under a trusted repo root (fixes #5722)

## Implementation plan

Goal: a patch for MCH-1. On Windows, binding a session to a new worktree is refused with FOLDER_TRUST even when the
repo root is trusted. The four done lines are frozen in the goal file.

Root cause. The trust test in the operation script (the function that reads the app's project list and decides if a
folder or a parent is trusted) builds both sides of its prefix test with a forward slash: the folder's resolved path
plus "/" against each trusted entry's resolved path with "/" stripped and "/" added. On Windows the resolved paths use
backslashes and may differ in drive-letter case, so the added "/" never lines up and no worktree ever matches. The
sessions script (bind and assign) and the unattended selfcheck all call this one function, so one fix covers them.

Decisions, taken as the routine answer:
1. Fix only that function. The edited text (measured, see decision 2) replaces the two inline path builders with one
   local lambda:
   `at = lambda p: os.path.normcase(os.path.realpath(p)).rstrip(os.sep)+os.sep`, then
   `... and at(folder).startswith(at(k)) ...`. It resolves, applies os.path.normcase (lowercase and backslashes on
   Windows, identity on macOS and Linux), strips trailing separators and adds os.sep. A folder is trusted when its form
   starts with a trusted entry's form. The trailing separator keeps a prefix-only sibling ("agent-workflow-template2"
   beside "agent-workflow-template") refused; an exact match of the root passes. Only os.sep is stripped (after normcase has unified the separators on Windows), so on POSIX a folder named with a trailing backslash
   (a sibling `/repo\` of a trusted `/repo`) stays refused; there is a case for it. The outside voice found the earlier
   both-kinds strip would have trusted that sibling.
2. Size: the script is 20,455 bytes and fails over 20,480 (dev/toy/size-check.py:14). The candidate text measured
   +11 bytes (20,466) with no spaces around the plus sign; a reviewer's different lambda measured +18 (20,473). The build re-measures the real file with
   size-check.py and trusts only that, and the acceptance line is strictly under 20,480 (dev/toy/test-tree.sh:16 uses
   `-lt 20480`), so at most 20,479, and the owner's ask is no growth beyond +12. The byte is found inside the new expression itself
   (no spaces around the plus sign); no docstring, comment or other code is touched. If the real file still measures
   over 20,479 the build stops and reports.
   No other script under skills/ is edited and no new file appears under skills/.
3. macOS and Linux behaviour is unchanged (normcase is the identity, os.sep is "/", and only "/" is stripped);
   the existing trust, restart and bind cases of the new-binds toy stay unedited and green.
4. The ~/.claude.json file stays read only and the refusal text is unchanged.
5. Item "resolve the folder once instead of per entry" is skipped (not decided in the build).

Steps:
1. Write the toy cases first (step 2 below), then do the red proof, then edit the function as in decision 1 and
   measure with size-check.py.
2. Toy cases in the new-binds toy, in a new section gated `only in ("", "wintrust")`, so `test-new-binds.py wintrust`
   runs it alone and the final PASS line stays reachable. To keep operate.py's import side effects (it updates the
   environment and may redirect stdin) out of the toy's process, the section runs a child python process (`python -I`,
   then an explicit sys.path insert of the scripts folder, which the flag drops) that imports operate.py by file, installs a shim, runs each case and prints
   one JSON object of results; the toy parent asserts on that JSON. In the child the shim is a `types.SimpleNamespace`
   standing in for `os` in the loaded module: every real os attribute except `sep` (set to a backslash) and `path`
   (another SimpleNamespace: realpath = ntpath.normpath, normcase = ntpath.normcase, join and expanduser real). The
   file read stays real: the child sets HOME and USERPROFILE to a temporary folder whose .claude.json holds
   Windows-style keys. The old function text
   is embedded in the toy as a literal and `exec`ed into a dict seeded from the module's globals (so it sees the same
   shim). Case names contain no quotes or backslashes (the unread-assert scan stops at a quote). Cases, each printing
   PASS: <name>:
   - wintrust windows worktree under a trusted root is trusted
   - wintrust drive letter case differs on either side
   - wintrust the root itself is trusted
   - wintrust an outside folder is refused
   - wintrust a prefix only sibling is refused
   (the last two must return the REFUSED text, which also proves the file was read, so a silent empty answer cannot pass)
   - wintrust a drive root entry trusts a path under it
   - wintrust a non dict entry and a malformed file give an empty answer without raising (the function's real failure
     paths: AttributeError and ValueError)
   - wintrust posix paths give the same answers as before, including that a sibling named with a trailing backslash
     stays refused (real os in the child; it runs on a host whose separator
     is a forward slash, and on a backslash host it prints PASS: wintrust posix paths give the same answers as before
     skipped on a backslash host, so the row's greps hold on every host)
   - wintrust negative control the old text refuses the windows worktree under its root
   - wintrust the child ran on a temporary HOME and USERPROFILE and never the real ones (the real trust file's size and
     modification time, read with a stat only and never opened, are the same before and after the run)
   - wintrust negative control the home check refuses a child whose HOME is the real home (run on made-up values, so
     the real file is never opened)
   UNC paths are not claimed.
   Red proof: after writing the cases and before editing operate.py, the build runs the real-function cases against the
   unedited file and saves the output (the Windows cases fail); then it edits. seen_red in the row is that date, so
   the row's red is the real tree's, not only the embedded copy's.
3. In the toy's existing trust section, set USERPROFILE as well as HOME for the bind and assign subprocesses (Windows
   expanduser reads USERPROFILE; assertions unchanged). The toy's `# reads:` header is left as it is: the narrow lane
   reads headers only of shell and extensionless files (narrow.py:176), so a header edit on this Python toy would map
   nothing; the new row is mapped widely, and the lane step checks the affected-row selection for operate.py with the
   planner instead of assuming a mapping.
4. One regression row of eight columns: id win-trust-prefix, level land, command `( out=$(python3
   dev/toy/test-new-binds.py wintrust 2>&1); ... grep -qF each PASS case name above ...; ! grep -q "^FAIL" )`, goal MCH-1, seen_red the
   date of the red proof in step 2, description `Given a trusted Windows root, when a worktree under it, a different
   drive-letter case, the root, an outside folder, a prefix-only sibling, a drive root, a non-dict entry and a POSIX
   sibling named with a trailing backslash are checked, then the trust test answers trusted, trusted, trusted, refused,
   refused, trusted, empty and refused, and the embedded old text refuses the first.`, category criterion, no link.
   The existing row that runs this whole toy without a grep keeps the unread-assert scan clean; the new row's greps are
   what pin each case name. Existing rows are byte-identical.
5. Regenerate the generated Tests tables with `python3 skills/workflow-docs/scripts/docs.py audit` (it fixes the
   mechanical Tests tables, `FIXED`; the new row changes them; `docs.py check` only reports staleness), reading its diff, then run: the wintrust and existing toy sections, `python3 dev/toy/size-check.py` on operate.py and the toy,
   `python3 skills/workflow-docs/scripts/docs.py check`, `python3 dev/package.py`, `python3
   skills/workflow-delivery/scripts/private.py check`, re-measure the toy (it grows by a literal and a child script and
   must stay under 20,480), then the regression lane on the committed head.

Limits, stated plainly. The Windows proof for MCH-1 is simulated: the cases run on the host's own operating system
with Windows path functions swapped in, never on Windows, so the string logic is proven and the Windows file system
(junctions, short names, long-path prefixes, drive substitutions) is not. The requirement's Confidence is not raised by
this change. There is no Windows runner and none is planned here. The refusal text is unchanged: it still names the
folder and FOLDER_TRUST but neither the trust file nor the entries it checked, because the done lines freeze the
behaviour and the script has no bytes to spare. A trust file that cannot be read still answers trusted, as it does
today; that is existing behaviour this goal does not change. One real check by a person on Windows remains the
owner's verify-by-hand step.

Out of scope, with their issue: the three other forward-slash prefix checks (lanes_cli.py:76, operate.py:328,
pool.py:312) are filed as issue 5740 and are not touched here; a shared path helper, a Windows runner, UNC paths, the
refusal text and the fail-open read are not part of this goal for the reasons above.

Estimate and per-step budget (a realistic one; the frozen ETA of 325 minutes stays the commitment on the goal and
this plan fits inside it): plan and its reviews, spent and recorded; build, 60 minutes (toy section 25, red proof 5,
edit and measure 10, row and docs 15, local checks 5); review, 30; qa and the one affected-row lane, 40 (the lane
itself is bounded by the repo's 5-minute lane target on a free machine); ship and pull request, 25; remaining about
155 minutes of the 325. A step past twice its budget is flagged to the operation session.

Test plan: the cases in step 2 plus the existing trust, restart and bind cases of the same toy. Failure modes: a
trusted entry that is the filesystem root (covered by the drive root case); a non-dict entry or malformed file
(covered, never raises); mixed-case drive letters (covered). Not in scope: changing what is trusted on Windows beyond this prefix test,
the app's own trust dialog, any other script under skills/, UNC paths (see Limits and Out of scope above).

## Review record

### Step 0 decision ledger (CEO, SELECTIVE EXPANSION by the autoplan override)

| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| D1 untrusted() prefix test (operate.py) | root cause per issue 5722 and operate.py:127-135 | "/" appended to resolved paths | helper: realpath, normcase, strip both separators, add os.sep | approved (auto, P1+P5) | decision 1 only |
| D2 size | operate.py 20,455 B, fails over 20,480 (dev/toy/size-check.py:14); measured edit +13 B | n/a | edit in place, no helper moved; stop if over | approved (auto, P3) | decision 2 only |
| D3 callers | worker.py:312, sessions.py:234, board_log.py:35 all call it | unchanged | unchanged, one fix covers all | approved (auto, P4) | no caller edited |
| D4 test method | no Windows runner in CI | none | ntpath-swapped simulation in the new-binds toy, with a control | approved (auto, P1) | step 2 only |

### 0A Premise challenge

Real problem: the trust check is a path-prefix test written for one separator, so on Windows it can never pass; no worker
can bind a new goal there. Do-nothing cost: Windows machines (MCH-1: "a Mac or Windows") cannot run the goal flow at all.
The plan fixes the cause (the separator and case handling), not a proxy such as skipping the check on Windows.

### 0B Existing code leverage

| Sub-problem | Existing | Reuse |
|---|---|---|
| Normalising paths | os.path.normcase, os.sep (standard library) | used |
| The trust test | operate.untrusted, three callers | edited in place |
| Trust test cases | test-new-binds.py trust section | extended |

REALITY: premise-table pass 6 premises, unverified=0 skills/workflow-monitoring/scripts/operate.py:133 and skills/workflow-monitoring/scripts/worker.py:312, skills/workflow-monitoring/scripts/sessions.py:234, skills/workflow-monitoring/scripts/board_log.py:35, dev/toy/size-check.py:14
REALITY: already-done pass git log origin/main since 2026-11-14 on operate.py shows only unrelated commits and none names 5722 or the trust prefix 977f4f067 skills/workflow-monitoring/scripts/operate.py:127
REALITY: surface-check pass no new command or flag; FOLDER_TRUST is a refusal code, unchanged skills/workflow-monitoring/scripts/operate.py:133
REALITY: binding-decisions pass the branch decision search printed nothing; no overruling default is reintroduced .loop/goals/pc-path-trust.plan.md:1
REALITY: numbers pass operate.py 20,455 B now; candidate edit +13 B, 20,468 B [measured: wc -c and a byte count of the edited function, 2026-11-21] dev/toy/size-check.py:14
REALITY: deferred-asks pass issue 5722 asks for os.sep, normcase on both sides and a toy with a Windows-style path; nothing left out .loop/goals/pc-path-trust.md:11
REALITY: pr-count pass one pull request; no ship-policy file .loop/goals/pc-path-trust.md:1

### 0C Dream state

```
  CURRENT STATE                THIS PLAN                       12-MONTH IDEAL
  "/"-only prefix test  --->   separator- and case-aware   ---> one path-contains helper every
  fails on Windows             test in one function             script shares, tested on a Windows runner
```

### 0D Alternatives

A) Current plan: fix the one function with a local helper (smallest, matches issue 5722's fix).
B) Skip the trust check on Windows. Rejected: removes a guard instead of fixing it.
C) Add a shared path helper module. Rejected: a new file under skills/ is forbidden by done line 4 and there is no
byte room in operate.py for an import. Dream-state path only.
Choice: A (P1, P5). Not close.

### 0E Mode

Autoplan override: SELECTIVE EXPANSION (the rule would say HOLD SCOPE). Files changed: operate.py, test-new-binds.py,
regression.tsv (3, estimate).

### 0G Candidate additions

1. Resolve the folder once instead of per entry (performance): skipped (P3), the cost is a few file-system calls per refused bind.
2. A Windows CI runner for the toy: defer (outside blast radius, new infrastructure).
3. Docs sentence: skip; FOLDER_TRUST has no prose in the docs to correct.

### 0I Temporal interrogation

Hour 1: the implementer must know the file is within 25 bytes of failing. Hours 2-3: the toy must not need Windows:
swap the module's path functions for ntpath ones. Hours 4-5: mixed case and a drive letter like "c:" vs "C:". Hour 6+:
they will wish for the old-text control and a prefix-sibling case.

### Accepted obligations

<!-- autoplan-accepted:ceo -->
- A worktree with Windows-style paths (backslashes, any drive-letter case, either side) under a trusted root is trusted by the trust test; verified by toy cases that run the real function with a Windows path shim (file read stays real) and by a control that runs the embedded old text and fails.
- A folder outside the trusted root, and a prefix-only sibling (agent-workflow-template2 beside agent-workflow-template), is still refused and the REFUSED text is returned (negative control); the root itself and a drive-root entry are trusted; a non-dict entry or a malformed trust file never raises (empty answer).
- macOS and Linux behaviour is unchanged: the existing trust, restart and bind cases of the new-binds toy stay green and unedited.
- operate.py stays at or under 20,480 bytes, measured with size-check.py on the real file; no other script under skills/ is edited; no new file under skills/. If the final edit would exceed it after the listed concessions, the build stops and reports.
- Checks green (docs, package, private-name); no existing regression row turns red; no test loosened.
<!-- /autoplan-accepted:ceo -->

### CEO review sections (hand run of the CEO review, SELECTIVE EXPANSION)

Spec review loop: 3 launches (scores 6, 7, 7); at the cap the last 7 issues were applied to the plan (issues verified: 7 of 7 applied, an edit check, not a verdict). Metrics line written: iterations 3, found 31, fixed 24, remaining 7. Outside voice (Codex, completed): 1 High, 1 Medium, both folded in (strip only os.sep so a POSIX folder named with a trailing backslash stays refused; set USERPROFILE as well as HOME in the existing trust section).

Section 1 Architecture. One function, three callers, one file read:
```
 sessions.py bind/assign (234) --\
 worker.py (312) ----------------+--> operate.untrusted(folder) --> ~/.claude.json  (read only)
 board_log.py selfcheck (35) ----/          |
                                            +--> "" (trusted or unknown)  |  "REFUSED ... (FOLDER_TRUST)"
```
No new coupling; the helper is local to the function. Data flow, four paths: happy (entry matches, ""), nil (no file or no "projects": OSError or KeyError, ""), empty (empty projects: no entry matches, REFUSED), error (malformed JSON or a non-dict entry: ValueError or AttributeError, ""). Rollback: revert the one commit. No state machine. Scaling: one realpath pair per entry, tens of entries. Single point of failure: the bare except returns "" (trusted) on any error: pre-existing fail-open behaviour, named below, not changed here.
Section 2 Error and rescue: OSError/ValueError/KeyError/TypeError/AttributeError are all rescued to "" (existing); realpath never raises on a missing path. GAP noted, not fixed: fail-open is deliberate (a repo with no trust file must still work; the negative control in the toy proves it). No catch-all added.
Section 3 Security: threats checked: prefix-only sibling (refused by the trailing separator, tested), case-folding on Windows (normcase; Windows folders are case-insensitive, so folding is correct), trailing-backslash POSIX sibling (found by the outside voice, fixed by stripping only os.sep, tested), symlinks and junctions (realpath, unchanged). Likelihood low, impact medium (a folder trusted that should not be); mitigated. No new secrets, inputs or dependencies.
Section 4 Data flow and edge cases: INPUT folder, entry keys -> realpath -> normcase -> strip os.sep -> add os.sep -> prefix compare -> text. Shadow paths covered by the cases: nil file, malformed file, non-dict entry, drive root, mixed case, sibling. No user-visible interaction.
Section 5 Code quality: a lambda assigned to a name matches operate.py's own style (CFG lambda, line 46); no duplication added; one branch.
Section 6 Tests: diagram of new behaviour to test: Windows worktree under root (unit, in the child), case on either side (unit), root itself (unit), outside and sibling (refused text), drive root, non-dict and malformed (never raises), POSIX sibling with a trailing backslash (refused), POSIX same answers, old-text control (red). The 2am-Friday test is the row; the hostile QA test is the trailing-backslash sibling; no chaos test needed (no I/O beyond one file read). Pyramid: all unit, one row.
Section 7 Performance: the folder's realpath is recomputed per entry (about twice the file-system calls of before); entries number in the tens; negligible, and the one-time resolve is skipped on purpose (bytes).
Section 8 Observability: the refusal names the folder and FOLDER_TRUST; selfcheck reports MISSING folder trust; no new log needed.
Section 9 Deployment: pure script change, no migration, no flag; rollback is a revert; post-merge check is the row and a Windows machine binding a worktree (the owner's verify-by-hand step).
Section 10 Trajectory: reversibility 5/5; debt: the same "/"-joined prefix idiom exists at lanes_cli.py:76, operate.py:328 and pool.py:312 (observed by grep; not shown to fail on Windows and outside issue 5722, so not touched here); a shared path-contains helper is the dream-state path. Ecosystem fit: stdlib only.
Section 11 Design: SKIPPED (no UI scope).

NOT in scope: a shared path helper module; the other "/" prefix sites named in section 10 (filed as issue 5740); a Windows CI runner (a stated limit); UNC paths; making the trust test fail closed (existing behaviour, frozen by the done lines).
What already exists: operate.untrusted, three callers, the new-binds trust and restart sections, size-check.py, the regression table.
Dream state delta: this plan moves one separator-aware check into place and names the remaining sites; the ideal is one tested helper on a Windows runner.

Error and rescue registry (capability rows): untrusted() read of the trust file: OSError rescued to "" (tested by the existing no-file control); malformed JSON ValueError rescued (new case); non-dict entry AttributeError rescued (new case). 0 critical gaps.
Failure modes registry:
| CODEPATH | FAILURE MODE | RESCUED? | TEST? | USER SEES? | LOGGED? |
|---|---|---|---|---|---|
| prefix test | Windows separators | Y (fix) | Y | trusted | n/a |
| prefix test | sibling or outside | Y | Y | REFUSED text | via selfcheck |
| prefix test | trailing backslash name on POSIX | Y (os.sep only) | Y | REFUSED text | via selfcheck |
| trust file | missing or malformed | Y (existing) | Y | nothing refused | no |
0 critical gaps.

Open items from this review, resolved: the other "/"-prefix sites are filed as issue 5740 (out of scope); a Windows runner and the fail-open read are stated limits in the plan (out of scope, reason given); nothing is left for the owner in this plan.
Implementation tasks: T1 (P1) write toy cases and red proof; T2 (P1) edit operate.py and measure; T3 (P1) set USERPROFILE in the trust section; T4 (P2) reads header; T5 (P1) regression row; T6 (P1) run the checks and the lane. Verify each by the commands in step 5.

Completion summary: mode SELECTIVE EXPANSION; sections 1-10 reviewed, section 11 skipped; 5 scope proposals, 3 accepted, 1 deferred, 2 skipped (6 listed); error-rescue 4 rows, 0 gaps; failure modes 4, 0 critical gaps; outside voice Codex completed; Lake Score 3/3; diagrams 2; unresolved decisions 0 (each former open item is fixed or out of scope with a reason); reality rows 7/7, unverified 0.
Approval readiness: PASS (rows D1-D4 approved by autoplan-style auto-decision under the six principles; no user answer was available or needed).

### DX review (hand run of the developer-experience review; unattended, recommended answers taken, nothing approved by a person)

Applicability: product type CLI Tool (the loop's operate, sessions and worker scripts; the surface touched is one trust check and its refusal). Mode chosen: DX TRIAGE (a bug fix; the review's own default for a fix). Per the mode table, TRIAGE traces Install and Hello World only, scores all eight passes for blockers, and skips the outside voice (recorded as skipped, not unavailable).

Developer Persona Card (0A, auto-decided):
```
Who:       an operator or AI worker session on a Windows machine, binding a new goal to a worktree
Context:   first goal on a fresh clone; the repo root is already trusted in ~/.claude.json
Tolerance: none for a refusal that cannot be cleared: two retries, then it hands the question to a human
Expects:   a trusted root trusts every worktree under it, as it does on a Mac
```
Developer Empathy Narrative (0B, from the issue's own evidence, predicted steps marked):
"I cloned the repo on my Windows machine and trusted the root folder when the app asked. I ask the operation session to start my first goal. It makes a worktree under the root and tries to bind me to it. The tool says REFUSED: ask the owner to trust .git/loop/worktrees/<goal> (FOLDER_TRUST). But I did trust the repo. I trust it again; same refusal (predicted, not observed). I open the config to look and the root is there, so I cannot tell what the check wants. Every new goal dies at the bind." Observed: the refusal and its text (issue 5722). Predicted: the retry and the feeling. The cause is invisible to the reader because the text names neither the file nor the entries compared.
Competitive DX benchmark (0C): the clock is "bind a new worktree": persona above, start at a trusted root, stop at a bound session. Today on Windows the stop is never reached (infinite, red flag); on macOS it is immediate [estimated: no timing measured]. No peer comparison is claimed: nothing in this repo's peers (Dev Containers, chezmoi) was timed; the target is parity with macOS. Target chosen (auto): parity, zero extra steps.
Magical Moment (0D): the bind simply works after one trust of the root, on either OS; vehicle: the existing bind command, no new surface (DX TRIAGE: no expansion).
Journey map (0F, TRIAGE: Install and Hello World only):
| STAGE | DEVELOPER DOES | FRICTION | STATUS |
|---|---|---|---|
| 1 Discover | reads the refusal | text names neither file nor entries | out of scope, limit stated (CAP6, below) |
| 2 Install | trusts the repo root in the app | none | ok |
| 3 Hello World | bind a new worktree | refused on Windows (the bug) | fixed by this plan |
| 4-6 Real usage, debug, upgrade | not traced in TRIAGE | n/a | n/a |
First-time developer report (0G, from the issue and source; T+ values are illustrative, not measured): T+0:00 bind says REFUSED naming the worktree. T+0:30 re-trust the root, refusal unchanged. T+2:00 open ~/.claude.json, the root is listed with trust accepted. T+3:00 gives up and asks a human. The fix removes the cause; the confusion in the refusal text remains (below).

Pass 1 Getting started 8/10 after the fix (2/10 before: blocked on Windows). Gap to 10: first run would also say which entry trusted the folder; not in scope.
Pass 2 CLI design 7/10: unchanged; the command, flags and code are not touched.
Pass 3 Error messages 6/10, capped. Error path matrix (agent-ready-v1), surface CLI:
| Path | Class | what | fix | recovery | code | context | trace | redaction | channel | Cap |
|---|---|---|---|---|---|---|---|---|---|---|
| untrusted() refusal (bind, assign) | environment | pass (the folder) | pass (a human must trust it) | pass (ask a human; no side effects) | pass (FOLDER_TRUST) | fail (names neither ~/.claude.json nor the entries it checked) | N/A (expected refusal) | pass | pass (non-zero exit, tested) | CAP6:context |
| selfcheck MISSING folder trust | environment | pass | pass (names the fix) | pass | pass | fail (same) | N/A | pass | pass | CAP6:context |
| trust file unreadable or malformed | unexpected | fail (silent) | fail | fail | fail | fail | fail (absent) | pass | fail (answers "trusted") | CAP6:trace; the silence is pre-existing fail-open |
CAP6:untrusted-refusal:context: today an agent sees `REFUSED: ask the owner to trust <folder> (FOLDER_TRUST).`; the corrected line would add `(checked ~/.claude.json: no trusted entry is a parent of <folder>)`. Not applied: it adds bytes to a script 12 bytes from its cap and the refusal text is frozen by existing tests; out of scope, stated as a limit in the plan, no follow-up item kept. No CAP4 finding: no secret is printed, the exit is non-zero, nothing blocks waiting for a terminal.
Pass 4 Documentation 6/10: no prose describes FOLDER_TRUST; the generated pages need no change.
Pass 5 Upgrade 8/10: nothing breaks; macOS and Linux answers are identical (cases prove it).
Pass 6 Environment 8/10 after (2/10 before on Windows): the toy runs on any host through a Windows path shim; a real Windows runner is out of scope and the simulation is a stated limit.
Pass 7 Community 5/10: not applicable to a one-function fix; no change.
Pass 8 Measurement 5/10: the new regression row is the measurement; no telemetry is added.

NOT in scope (DX): improving the refusal text (CAP6, no bytes and frozen behaviour: a stated limit); a Windows CI runner; telemetry; docs prose for FOLDER_TRUST.
What already exists: the refusal text and code (operate.py:133), the selfcheck line (board_log.py:37), the new-binds trust and restart sections.
TODOs: none kept. The CAP6 context line and the fail-open read are existing behaviour that this goal does not change; both are stated as limits in the plan.

## DX Review Scorecard
```
+====================================================================+
|              DX PLAN REVIEW — SCORECARD                             |
+====================================================================+
| Getting Started      | 8/10   | 2/10   | up                         |
| API/CLI/SDK          | 7/10   | 7/10   | flat                       |
| Error Messages       | 6/10   | 6/10   | flat (CAP6 context)        |
| Documentation        | 6/10   | 6/10   | flat                       |
| Upgrade Path         | 8/10   | 8/10   | flat                       |
| Dev Environment      | 8/10   | 2/10   | up                         |
| Community            | 5/10   | 5/10   | flat                       |
| DX Measurement       | 5/10   | 5/10   | flat                       |
+--------------------------------------------------------------------+
| TTHW                 | parity with macOS (target) | blocked (before)   |
| Competitive Rank     | not benchmarked against peers (no timing)       |
| Magical Moment       | designed via the existing bind command          |
| Product Type         | CLI Tool                                        |
| Mode                 | TRIAGE                                          |
| Overall DX           | 6/10 (was 4/10)                                 |
+====================================================================+
| DX PRINCIPLE COVERAGE                                               |
| Zero Friction      | covered (the fix)                              |
| Learn by Doing     | gap (no example; not in scope)                 |
| Fight Uncertainty  | gap (the refusal's context, CAP6)              |
| Opinionated + Escape Hatches | covered                              |
| Code in Context    | n/a                                            |
| Magical Moments    | covered                                        |
| Agents Are Users   | gap (silent fail-open on an unreadable file)   |
+====================================================================+
```
DX Implementation Checklist: [x] bind works on Windows after one root trust; [x] first run unchanged on macOS; [ ] refusal names the file it read (out of scope, a stated limit, CAP6); [x] every changed error path keeps its exit code and text; [x] cases run on any host.
DX tasks: T1 (P1) cases and fix as planned; no follow-up tasks.
Outside voice (DX): skipped by mode (TRIAGE), not unavailable. Unresolved decisions: none; the two former items are stated limits in the plan.

### Eng review (hand run of the engineering review; target: this plan, user-named)

Scope gate: user-named target, reviewing the plan file for this goal. Probe evidence (a throwaway script outside the repo, no repo file edited): with the module's path functions swapped for Windows ones and a real trust file, the old text refuses a worktree under a trusted Windows root (also with different drive-letter case, and under a drive-root entry) while the candidate text trusts it; an outside folder and a prefix-only sibling are refused by both; on POSIX a sibling named with a trailing backslash is refused by the candidate. operate.py measured 20,455 B before and the candidate edit +13 B.
Step 0 Scope Challenge: 3 files changed (operate.py, the new-binds toy, regression.tsv; the Tests tables regenerate), 0 new classes or services, so the complexity gate does not trip and no scope question is asked. Result: scope accepted as-is (MODE FULL_REVIEW). Search check: no new pattern or component; stdlib only [Layer 1].
REALITY: premise-table pass 7 premises, unverified=0 skills/workflow-monitoring/scripts/operate.py:133 (also dev/toy/test-new-binds.py:91, skills/workflow-regression/scripts/narrow.py:176, dev/toy/test-tree.sh:16, skills/workflow-docs/scripts/docs.py:277)
REALITY: already-done pass git log origin/main since 2026-11-14 on operate.py shows only unrelated commits and none names 5722 or the trust prefix 977f4f067 skills/workflow-monitoring/scripts/operate.py:127
REALITY: surface-check pass docs.py audit and check, dev/package.py, private.py check and size-check.py exist; render.py has only the blocks mode, so the plan uses docs.py audit for the Tests tables skills/workflow-docs/scripts/docs.py:277
REALITY: binding-decisions pass the branch decision search printed nothing; the owner's instruction (keep operate.py within its cap, no growth from review fixes) is kept .loop/goals/pc-path-trust.md:1
REALITY: numbers pass operate.py 20,455 B now and 20,468 B after the candidate edit; the repo's tree check requires under 20,480 [measured: wc -c and a byte count of the edited function, 2026-11-21] dev/toy/test-tree.sh:16
REALITY: deferred-asks pass issue 5722 asks for os.sep, normcase on both sides and a toy with a Windows-style path; all three are in the plan .loop/goals/pc-path-trust.md:11
REALITY: pr-count pass one pull request; no ship-policy file .loop/goals/pc-path-trust.md:1

1. Architecture. [INFORMATIONAL] (confidence: 9/10) skills/workflow-monitoring/scripts/operate.py:127-135 — one function and three callers (worker.py:312, sessions.py:234, board_log.py:35); no new module or boundary, so design-twice is not run (one line, per the skill). Red-flag screen: shallow module no; information leakage no; temporal decomposition no; pass-through no; split ownership no; two ways to do one task no; importable internals no; hand-synced list: the case names appear in the toy and in the row's greps, and a mismatch makes the row fail (derived check), accepted. Data flow, four paths: happy (matching entry, trusted), nil (no trust file, empty answer), empty (no entries, refused), error (malformed file or non-dict entry, empty answer). Distribution: scripts only, no artifact, no CI change. Diagram: sessions/worker/board_log -> operate.untrusted -> at() -> prefix compare -> text (see the CEO section).
   Dispositions: no finding needs a remedy.
2. Code quality. [INFORMATIONAL] (confidence: 8/10) skills/workflow-monitoring/scripts/operate.py:46 — a lambda bound to a name matches the module's own CFG lambda; no duplication added. Shared-code rubric: the other "/"-prefix sites (lanes_cli.py:76, operate.py:328, pool.py:312) have different contracts (relative paths, page names, scope globs) and Windows behaviour is unobserved, so no extraction is proposed. Outside-voice finding (Low, confidence 9/10) dev/toy/test-tree.sh:16 — the repo's tree check needs strictly under 20,480 B; folded into the plan (at most 20,479). Diagram accuracy: the new-binds toy has no diagram; none stale.
   Dispositions: size boundary accepted (plan step edited); extraction rejected.
3. Tests. Coverage diagram (all proposed, existing marked):
```
CODE PATHS                                           USER FLOWS
[+] skills/workflow-monitoring/scripts/operate.py    [+] bind a new worktree on Windows
  ├── at() normalise                                   ├── [GAP] [★★★ planned] under a trusted root, either case
  │   ├── [GAP] windows backslashes, case              ├── [GAP] [★★★ planned] outside folder and prefix-only sibling refused
  │   └── [GAP] drive root, trailing separator         └── [★★ TESTED] posix worktree under a trusted parent (test-new-binds.py:108)
  ├── any(...) match
  │   ├── [★★ TESTED] trusted parent (existing)       [+] selfcheck MISSING folder trust
  │   ├── [★★ TESTED] untrusted refused (existing)      ├── [★★ TESTED] untrusted and trusted parent (existing)
  │   └── [GAP] [★★★ planned] posix backslash sibling
  └── except -> ""
      ├── [★★ TESTED] no file (existing)
      └── [GAP] [★★★ planned] malformed file, non-dict entry
COVERAGE: 4 existing paths tested, 5 gaps each with a planned case | QUALITY: planned cases assert the REFUSED text, so none is a smoke check
```
   Test plan artifact written (outside the repo, in the review state folder). Regression rule: existing POSIX behaviour is at risk by construction-equivalence only, so the existing trust, restart and bind sections stay unedited (except USERPROFILE isolation) and run as the regression proof. Outside-voice findings folded: docs regeneration step (Medium), full eight-column row with a Given/When/Then description (Medium), the header edit does nothing for a Python toy (Low, narrow.py:176; the lane step verifies affected-row selection instead).
   Dispositions: all accepted into the plan; Tests to retire: none.
4. Performance. [INFORMATIONAL] (confidence: 8/10) skills/workflow-monitoring/scripts/operate.py:133 — realpath per entry twice (entry and folder), entries number in the tens, one call per bind: unknown absolute cost, negligible against a process start; no loop on a request path. No issues.

Outside voice (Codex, completed): 4 findings (2 Medium, 2 Low), 4 of 4 folded into the plan; it also confirmed the module-global shim exercises the edited function and that the fix passes its in-memory check. Cross-model: the CEO-phase outside voice found the POSIX trailing-backslash widening; this one found the registration gaps; no overlap, no disagreement.

NOT in scope (eng): a shared path helper; a Windows runner; failing closed on an unreadable trust file; the other "/"-prefix sites.
What already exists: operate.untrusted and its callers, the new-binds toy sections, size-check.py, the Tests tables generator (docs.py audit), the regression table.
Failure modes: prefix test on Windows paths (rescued by the fix, tested); sibling and outside folders (refused, tested); malformed trust file (rescued to empty, new case; silent by design and unchanged, no critical gap because the existing no-file control covers the same answer; a stated limit in the plan); size cap breach (the build re-measures and stops). 0 critical gaps.
Worktree parallelization: sequential implementation, no parallelization opportunity (one script, one toy, one table).
Implementation tasks: T1 (P1, human ~3h / CC ~25min) toy section and cases, then red proof; T2 (P1, ~20min / ~3min) edit operate.py and re-measure; T3 (P1) USERPROFILE in the trust section; T4 (P1) regression row (eight columns) and docs.py audit; T5 (P1) run the checks, then the lane on the committed head. Verify each by the step-5 commands.
Unresolved decisions in this review: 0. The former carried items are resolved: other prefix sites filed as issue 5740; Windows runner and fail-open read are stated limits in the plan.
Completion summary: Step 0 scope accepted as-is; reality rows 7/7, unverified 0; Architecture 0 issues; Code quality 1 informational (size boundary), folded; Test review diagram produced, 5 gaps, all planned; Performance 0 issues; NOT in scope written; What already exists written; TODOS: none proposed (the repo has no TODOS.md; the former carried items are resolved); failure modes 0 critical gaps; outside voice Codex completed; parallelization sequential; Lake Score 4/4.
Approval readiness: PASS (every accepted change traces to the plan's decisions 1-5 and the auto-decisions recorded in the CEO review; no user answer exists or was required in this unattended run).

## REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` (hand run) | Scope & strategy | 1 | CLEAR | 6 proposals, 3 accepted, 1 out of scope, 2 skipped; 0 critical gaps; every open item fixed or out of scope with a reason |
| Outside Review | codex (completed, CEO phase and Eng phase) | Independent 2nd opinion | 2 | completed | CEO phase 2 findings, Eng phase 4 findings; all folded in |
| Eng Review | `/plan-eng-review` (hand run, read from its skill file; the Skill tool answered "Unknown skill: plan-eng-review") | Architecture & tests (required) | 1 | CLEAR | 6 issues, all folded in, 0 critical gaps |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | skipped | no UI scope |
| DX Review | `/plan-devex-review` (hand run, TRIAGE) | Developer experience gaps | 1 | CLEAR with named limits | score: 4/10 -> 6/10, TTHW: blocked on Windows -> parity with macOS; the refusal-text gap is a stated limit, out of scope |

**OUTSIDE COVERAGE:** codex completed for the CEO phase and the Eng phase; the DX phase's outside voice was skipped by mode (TRIAGE), not unavailable; the CEO spec review ran as a native subagent (3 launches, scores 6, 7, 7) and supplies no outside coverage. The red-team gate and an independent plan reviewer ran on the committed plan and are recorded outside this file.
**CROSS-MODEL:** the two completed codex reviews found different issues (the POSIX trailing-backslash widening and the isolation of the existing Windows test; then the docs, row-description, header and size-boundary gaps); no disagreement with the native passes; no overlap to confirm agreement. Model identity per the probe: gpt-6-astra for both.
**VERDICT:** CEO + ENG CLEARED, DX cleared with its named limits (simulated Windows proof, unchanged refusal text, no Windows runner); ready to implement.

NO UNRESOLVED DECISIONS
