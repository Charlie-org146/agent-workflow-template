# Plan: v110-make-room

Source: the goal file's five frozen done lines; owner o954, record o957 (owner o1009). A one-time make room by pure moves: no behaviour change. Facts about main (189d1c831) and file:line references stay in a private build brief, never in this plan.

## URGENT, outside this plan

None.

## Implementation plan

Done lines (frozen): (1) each of the seven split scripts ends with at least 6,000 bytes of room to the 19,000-byte line; (2) every regression row that passes on the merge base passes on the head, no row is added to a known or skip list, and the move check shows every moved line byte-identical but for imports and module prefixes; (3) pods-size and the package rows pass with the new modules listed; (4) no command, flag, setting name or output line of the seven scripts changes; (5) every script stays under 20,480 bytes, no test is loosened, no row turns red, committed text never names the service repo.

Touches (frozen as written): skills/workflow-delivery/scripts, skills/workflow-release/scripts/merge.py, dev/toy, .loop/regression.tsv. The new module beside merge.py (skills/workflow-release/scripts/merge_steps.py) is outside the written touches: the operation widens them first (goal.py touches), or the build stops there and reports.

### Size of this goal (computed by its own rule)
Files: skills/workflow-delivery/scripts/goal.py, skills/workflow-delivery/scripts/goal_steps.py, skills/workflow-delivery/scripts/flow.py, skills/workflow-delivery/scripts/flow_steps.py, skills/workflow-delivery/scripts/lane.py, skills/workflow-delivery/scripts/lane_run.py, skills/workflow-release/scripts/merge.py, skills/workflow-release/scripts/merge_steps.py, dev/toy/move-check.py, dev/toy/move-manifest.json, dev/toy/test-make-room.sh, dev/toy/approved-row-changes.tsv, dev/toy/test-statuses.sh, dev/toy/test-eta-preflight.py, dev/toy/test-hard-eta.py, dev/toy/test-wiki-front.sh, dev/toy/test-portable.sh, dev/toy/test-lane-messages.sh, .loop/regression.tsv
Lines: about 1500
Gates: the planning gate, the build gate, the ship gate
Classes: none
Part B (built after part A, same goal and branch; listed apart so the Files line stays at 19 of the 20 the rule allows): skills/workflow-delivery/scripts/fit.py, skills/workflow-delivery/scripts/fit_budget.py, skills/workflow-delivery/scripts/role.py, skills/workflow-delivery/scripts/role_gate.py, skills/workflow-delivery/scripts/routing.py, skills/workflow-delivery/scripts/routing_pick.py, dev/toy/test-scan-closed.py, plus the shared manifest, move check, approved-row-changes.tsv and .loop/regression.tsv above. All 26 files together are touched by a move, by the move check, or by a repoint of a text-reading toy or row; none carries new behaviour.
Large: part A alone is 19 files and about 1,500 lines with three gates; the whole goal is 26 files. guards.py is left out.

### 1. The mechanism (one rule for all seven moves)
- A moved function goes whole, with its decorator lines and its text unchanged, into a new sibling module in the same folder. The names it used from the old script become `_s.NAME` (the module prefix). The alias is `_s`, never `g`: fit.py's `cmd_set`, `regen`, `pr_open`, `pr_text`, `regen_warnings` and `pr_fail`, and goal.py's `round_stop`, already take a parameter named `g` (the goal module), so a `g` alias would shadow it and a `g.view` or `g.tool` would raise.
- The new module imports its script at the BOTTOM of the module: `import <script> as _s  # noqa: E402`, after every def. The function bodies read `_s.NAME` only when called, so the import order never matters at call time, and importing a new module first (`import goal_steps`) works: the script's `from <new_module> import ...` at its end finds the module already complete.
- The old script re-exports the moved names with one line at its very end, after its last definition and before its `if __name__` block: `from <new_module> import NAME1, NAME2  # noqa: E402,F401`. Every caller (`fit.pr_body`, `role.record`, `goal.cmd_pr`, the toys, the guard code) still finds the same name on the same module, so no caller changes.
- Registration: a script run as `python3 script.py` is `__main__`, so it registers itself under its module name with `sys.modules.setdefault("<script>", sys.modules[__name__])` (goal.py already does, as ME). The line goes BEFORE the first import in that script that can import it back (found by the build with a grep of the script's imports; role.py: above its `from lane import` line), not at the end. flow.py, lane.py, fit.py, role.py, routing.py and merge.py each gain that one line.
- Names a moved function uses that are moved with it into the same module are plain names (siblings, no prefix); names that stay in the old script get `_s.`; standard-library modules it needs are imported at the top of the new module; builtins are ignored.
- A new module runs alone (the package rule): `python3 new_module.py --help` imports its script (which imports the module back) and exits 0 with no output.
- The header of every new module is exactly: a one-line docstring saying what the module holds, its standard-library imports, the DEL-10 guard line (only when the module mentions `subprocess`: it is the same `os.environ.update(GIT_TERMINAL_PROMPT=...)` line the existing scripts carry, because the package rule test-rows.sh DEL-10 requires it in every script that starts a process), then the moved functions in table order, then the `_s` import. The docstring, the guard line, the registration line, the `_s` import and the re-export line are the ONLY lines in the whole goal that are not a byte-identical move (the "header exemption"); the move check allows exactly those and nothing else.
- Docstrings (owner-approved wording intent): fit_budget "the budget commands and the pull request text"; routing_pick "the routing run commands"; goal_steps "the record and pr commands"; flow_steps "the step runner and the prompt builders"; lane_run "the lane finish and exec"; role_gate "the role guard, the recorded-step gate, the cap and lane parts"; merge_steps "the merge steps: base check, release advance, issue filing".

### 2. The move table (each whole function, its bytes in the base file, from where to which module)
Bytes are the function's source text plus its two blank lines, measured on the merge base (every figure re-measured by the round 1 review and exact).

| script (now) | functions moved (bytes) | to | moved | the script after (at most) | room to 19,000 (at least) |
|---|---|---|---|---|---|
| goal.py (18,997) | cmd_record 4,092; cmd_pr 3,553; round_stop 627 | goal_steps.py | 8,272 | 10,975 | 8,025 |
| flow.py (18,982) | in_session 2,213; start 1,490; runnable 956; unattended 941; step_prompt 762; step_command 496; routine 352 (depth_rule stays: it carries the sizing decorator) | flow_steps.py | 7,210 | 12,022 | 6,978 |
| lane.py (18,993) | finalize 4,512; lane_exec 2,710 | lane_run.py | 7,222 | 12,021 | 6,979 |
| fit.py (20,443) | cmd_set 2,580; budget_stop 1,241; pr_body 979; regen_warnings 739; pr_text 721; pr_open 624; regen 572; pr_fail 459; off_reply 408; step_line 374; tokens_text 227; off_rows 224; off_line 126 | fit_budget.py | 9,274 | 11,419 | 7,581 |
| role.py (20,380) | record 2,286; over_caps 1,661; recorded_gate 1,499; guard 1,285; lane_part 984; markers 918 | role_gate.py | 8,633 | 11,997 | 7,003 |
| routing.py (20,469) | cmd_build 3,274; usage 1,457; cmd_finish 1,421; cmd_check 1,237; ask 646 | routing_pick.py | 8,035 | 12,684 | 6,316 |
| merge.py (18,990) | advance 3,350; base_moved 1,714; missing_ids 1,200; file_issue 831 | merge_steps.py | 7,095 | 12,145 | 6,855 |

- Rule 3, a Bytes line per script: goal.py 18,997 now, 8,272 moved, at most 10,975 left; flow.py 18,982, 7,210, at most 12,022; lane.py 18,993, 7,222, at most 12,021; fit.py 20,443, 9,274, at most 11,419; role.py 20,380, 8,633, at most 11,997; routing.py 20,469, 8,035, at most 12,684; merge.py 18,990, 7,095, at most 12,145. The "after" figure is the base size minus the moved bytes plus at most 250 bytes of added lines (the re-export, the registration line and the import line); every script keeps more than 6,000 bytes of room, the smallest 6,316.
- Each new module is its moved bytes plus at most 450 bytes of header (docstring, imports, the guard line where needed, the `_s` import): goal_steps about 8,700, flow_steps about 7,700, lane_run about 7,700, fit_budget about 9,700, role_gate about 9,100, routing_pick about 8,500, merge_steps about 7,550. All under 19,000. guards.py (20,390) is not touched; the sizing hooks in guards.py, role.py (bump_version stays in role.py), flow.py (depth_rule keeps its decorator) and board code stay where they are.
- The refuse/allow functions in role.py and merge.py (section 2a) move byte for byte; any change beyond an import line stops the goal and goes to the operation.
- Next candidates, not in this goal: guards.py (20,390, deliberately left out, the heavily edited guard), lanekit.py (20,410), private.py (20,360), and in monitoring auto.py (20,377), layers.py (20,439), board_log.py (20,466), operate.py (20,466), board_status.py (20,477).
- Order and land-first: part A goal, lane, merge, flow; then part B routing, role, fit; one script per commit. Build starts with `git merge origin/main`, and the build goes straight through to the pr so the seven scripts have no unmerged concurrent edit (they had 233 commits since 11-10). Before the build the operation asks other goals to leave these seven scripts alone until this goal merges. A modify/delete conflict at any merge of main (a main edit to a moved function) stops the goal and goes to the operation: nothing is resolved by guess.

### 2a. Moved functions that refuse or allow an action (they move unchanged; the red team must see them)
- role.py to role_gate.py: `guard` refuses a goal step outside a worker (NOT_WORKER); `recorded_gate` refuses rerunning a recorded step and refuses while the step still runs (ALREADY_RECORDED), and `--again` clears the step and every later one; `over_caps` refuses a goal that adds test rows while the repo is over a test cap; `markers` supplies the full-review marker strings that the record check refuses a reply without; `record` and `lane_part` write the lane bookkeeping commit and the lane part of a record (a failure only prints a NOTE).
- merge.py to merge_steps.py: `base_moved` refuses the merge when the base moved in paths the goal's rows reach (BASE_MOVED) or cannot be fetched (BASE_FETCH); `missing_ids` names the requirement ids that hold the merge back; `advance` merges the release pull request once its checks allow, so it allows an action (a merge); `file_issue` files an issue.
- The move check proves each of these is byte-identical to the base after the module prefix is removed, so none changes what it refuses or allows; the toy also runs one refusal of each (a non-worker step, a rerun of a recorded step, a merge on a moved base) on the head and on the base and compares the words.

### 3. The move check (dev/toy/move-check.py, new; dev/toy/test-make-room.sh runs it)
- The manifest (dev/toy/move-manifest.json, committed) is DERIVED, never typed: `move-check.py --derive` reads each moved function's free names with ast, marks every name defined at top level in the old script and not moved with it as `_s.NAME`, treats names moved to the same module as siblings, and writes the manifest; the check recomputes it and fails if the committed manifest differs. The base text comes from `git show 189d1c831:<path>` (a pinned sha, see rows below).
- For every moved function it proves: (a) `ast.dump` of the new function, after removing the `_s.` prefix from the manifest's names, equals `ast.dump` of the base function; (b) the source text equals the base text once those prefixes are removed; (c) the function is gone from the old script and present in the new module exactly once; (d) the old script re-exports it by name.
- Header exemption proof: parsing each new module, removing the docstring, the imports, the guard line (exact text), the `_s` import and the moved functions leaves nothing; parsing each old script, removing the moved functions and the five header lines (registration, re-export, imports) leaves the base script's remaining text byte-identical.
- Whole-file proofs: the set of string constants of the old script plus its new module, minus the header exemption (docstring, the two registration strings, the guard line's constants), equals the base script's set (no output line, flag, command or setting name changes); `python3 script.py --help` for each of the seven scripts and every argparse subcommand prints the same text as on the base; every name the base script defined at top level is still defined there (by definition or by re-export).
- Negative controls (seen red): change one byte inside a moved body; drop a re-export; rename a moved function; add a string constant; add a non-header line to a new module; use `g.` for a name: each makes exactly its own check fail.
- Size proof: size-check on the seven scripts and the seven modules: each script at most 13,000 bytes, each module under 19,000, every script under 20,480.

### 4. The text inventory (what reads a moved script's TEXT) and the repoints
Move 0 of the build, before any move: `move-check.py --inventory` lists every toy and every row command that names a moved function or reads the text of one of the seven scripts (grep, split, open, count); the table below is what the reviews found, the build completes it from that listing before it moves a line.
| reader | what it reads | repoint (an assert is never weakened) |
|---|---|---|
| row pr-body-by-file (.loop/regression.tsv) | "--body-file" in fit.py (now in pr_open) | the same grep over fit.py and fit_budget.py |
| dev/toy/test-statuses.sh:89 | the `return 5 * (state["statuses"]...` text in goal.py | read goal_steps.py (cmd_pr) |
| dev/toy/test-statuses.sh:122, :125, :126 | autorelease.release_statuses call, "--admin"/"--auto" absence, "--merge" appearing twice in merge.py | the same asserts over merge.py plus merge_steps.py (count summed over both) |
| dev/toy/test-eta-preflight.py:210, dev/toy/test-hard-eta.py:169 | `queue("preflight", ME, state)` in goal.py | the text with the module prefix, `_s.queue("preflight", _s.ME, state)`, over goal_steps.py |
| row/toy on routing.py cmd_finish and the private.py scan gate (dev/toy/test-scan-closed.py:118) | the gate in cmd_finish | read routing_pick.py |
| dev/toy/test-wiki-front.sh:261 | split("def cmd_pr") in goal.py | goal_steps.py |
| dev/toy/test-portable.sh:58, dev/toy/test-lane-messages.sh:15 | killpg absence in flow.py and lane.py; merge.py named explicitly | the same asserts over the added module files (a negative grep now also covers the new files) |
- EACH repointed toy or row gets its OWN line in dev/toy/approved-row-changes.tsv (one id per line, never a group), naming the old text and the new place, with its assert unchanged: the record column `o957 (owner o1009)` and the words "moved by the make-room goal: reads <old text> in <old file>, now in <new file>; assert unchanged". The cutgate rule (TD1103) allows only those ids to differ from main, and the operation checks that file at merge (TD1229). A repoint that would weaken an assert stops the goal and goes to the operation.

### 5. Rows and tests
- Rows linked v110-make-room:1 to :5, one per done line, each added with `regression.py add` and seen red with `regression.py red --break` on a fixture that breaks only that line. Rows 1 and 2 are pinned so they stay true after the merge and never block later work: row 1 (room) reads the seven scripts at the head sha of the commit that completes the last move (written into the row by a docs-only commit after the move) and compares sizes there; row 2 (byte-identical) runs the move check with `--base 189d1c831` (a fixed commit that stays in main's history) against that same pinned head sha, never against the moving merge base. Row 3 runs pods-size and the package rows; row 4 compares the `--help` surface and string constants to 189d1c831; row 5 is the size-check plus the leak scan.
- What "listed" means for done line 3: the package walks every file under skills/, so the new modules are in the package by existing; there is no separate list to edit. "Listed" is proved by the package rule passing with the modules present: each runs alone with `--help`, carries the DEL-10 line if it mentions subprocess, is under 19,000 bytes, and the package file count stays at or under the cap.
- Single rows from the clean environment after each script's commit: pods-size, package-passes, listing-names-every-command, release-static-rules, and every row the inventory names. The full affected set runs once in the qa lane. No row goes to a known or skip list.

### 6. Risks
- Import cycles and import order: handled by the `_s` import at the bottom of each new module, the re-export at the end of each script and the registration line placed before any import-back; a toy case imports each new module first and each script first, and runs each script by its path with `--help`.
- A caller that reads an attribute off a module while the module is half built: re-exports sit at the very end of each script.
- Scripts run as `__main__` in lanes and by the flow: the toy runs each script by its path.
- Windows: `python3 -E -s` lone runs of the new modules.
- Text-reading toys and rows: the inventory above and move 0.

### NOT in scope
guards.py; any new behaviour, command, flag or setting; renaming a function; trimming a docstring or comment; the sizing, board or monitoring code.

### Verification
move check green and seen red; every row that passed on the merge base passes on the head; size-check; pods-size and the package rows; `docs.py check` clean; the committed text scanned for the service repo name.

## Review record

(filled by the plan review)
