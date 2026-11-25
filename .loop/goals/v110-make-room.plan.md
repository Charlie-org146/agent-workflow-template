# Plan: v110-make-room

Source: the goal file's five frozen done lines; owner o954, record o957 (owner o1009). A one-time make room by pure moves: no behaviour change. Facts about main (189d1c831) and file:line references stay in a private build brief, never in this plan.

## URGENT, outside this plan

None.

## Implementation plan

Done lines (frozen): (1) each of the seven split scripts ends with at least 6,000 bytes of room to the 19,000-byte line; (2) every regression row that passes on the merge base passes on the head, no row is added to a known or skip list, and the move check shows every moved line byte-identical but for imports and module prefixes; (3) pods-size and the package rows pass with the new modules listed; (4) no command, flag, setting name or output line of the seven scripts changes; (5) every script stays under 20,480 bytes, no test is loosened, no row turns red, committed text never names the service repo.

Touches (frozen as written): skills/workflow-delivery/scripts, skills/workflow-release/scripts/merge.py, dev/toy, .loop/regression.tsv. The new module beside merge.py (skills/workflow-release/scripts/merge_steps.py) is outside the written touches: the operation widens them first (goal.py touches), or the build stops there and reports.

### Size of this goal (computed by its own rule)
Files: skills/workflow-delivery/scripts/goal.py, skills/workflow-delivery/scripts/goal_steps.py, skills/workflow-delivery/scripts/flow.py, skills/workflow-delivery/scripts/flow_steps.py, skills/workflow-delivery/scripts/lane.py, skills/workflow-delivery/scripts/lane_run.py, skills/workflow-delivery/scripts/fit.py, skills/workflow-delivery/scripts/fit_budget.py, skills/workflow-delivery/scripts/role.py, skills/workflow-delivery/scripts/role_gate.py, skills/workflow-delivery/scripts/routing.py, skills/workflow-delivery/scripts/routing_pick.py, skills/workflow-release/scripts/merge.py, skills/workflow-release/scripts/merge_steps.py, dev/toy/move-check.py, dev/toy/test-make-room.sh, .loop/regression.tsv
Lines: about 1500
Gates: the planning gate, the build gate, the ship gate
Classes: none
Large: 17 files (under the 20-file limit, so one part, no split into A and B), about 1,500 lines moved, three gates. guards.py is left out. Every file is touched by a move or is the move check, its toy or the rows; none is a new behaviour.

### 1. The mechanism (one rule for all seven moves)
- A moved function goes whole, with its decorator lines and its text unchanged, into a new sibling module in the same folder. Names it used from the old script become `g.NAME` (module prefix) where `g` is the old script, imported in the new module as `import <script> as g`. Standard-library imports it needs are repeated at the top of the new module. Nothing else in the body changes.
- The old script gets, at its very end (after its last definition, before its `if __name__` block), one line `from <new_module> import NAME1, NAME2  # noqa: E402,F401`, so every caller (`fit.pr_body`, `role.record`, `goal.cmd_pr`, the toys, the guard code) still finds the same name on the same module. No caller changes.
- A script run as `python3 script.py` is `__main__`; the old script registers itself under its own module name with one line (`sys.modules.setdefault("<script>", sys.modules[__name__])`, as goal.py already does with ME), so `import <script> as g` in the new module returns the running module, not a second copy. goal.py already has it; flow.py, lane.py, fit.py, role.py, routing.py and merge.py each gain that one line.
- Why `g.` and not a parameter: the call signature of each moved function is unchanged, so no call site changes and no output line changes.
- A new module runs alone (the package rule): `python3 new_module.py --help` imports its script and exits 0 with no output.

### 2. The move table (each whole function, its bytes in the base file, from where to which module)
Bytes are the function's source text plus its two blank lines, measured on the merge base.

| script (now) | functions moved (bytes) | to | moved | the script after | room to 19,000 |
|---|---|---|---|---|---|
| goal.py (18,997) | cmd_record 4,092; cmd_pr 3,553; round_stop 627 | goal_steps.py | 8,272 | about 10,850 | about 8,150 |
| flow.py (18,982) | in_session 2,213; start 1,490; runnable 956; unattended 941; step_prompt 762; step_command 496; routine 352 (depth_rule stays: it carries the sizing decorator) | flow_steps.py | 7,210 | about 11,920 | about 7,080 |
| lane.py (18,993) | finalize 4,512; lane_exec 2,710 | lane_run.py | 7,222 | about 11,890 | about 7,110 |
| fit.py (20,443) | cmd_set 2,580; budget_stop 1,241; pr_body 979; regen_warnings 739; pr_text 721; pr_open 624; regen 572; pr_fail 459; off_reply 408; step_line 374; tokens_text 227; off_rows 224; off_line 126 | fit_budget.py | 9,274 | about 11,320 | about 7,680 |
| role.py (20,380) | record 2,286; over_caps 1,661; recorded_gate 1,499; guard 1,285; lane_part 984; markers 918 | role_gate.py | 8,633 | about 11,880 | about 7,120 |
| routing.py (20,469) | cmd_build 3,274; usage 1,457; cmd_finish 1,421; cmd_check 1,237; ask 646 | routing_pick.py | 8,035 | about 12,550 | about 6,450 |
| merge.py (18,990) | advance 3,350; base_moved 1,714; missing_ids 1,200; file_issue 831 | merge_steps.py | 7,095 | about 11,990 | about 7,010 |

- Module names are the seven the owner approved (goal_steps, flow_steps, lane_run, fit_budget, role_gate, routing_pick, merge_steps).
- Rule 3, a Bytes line per script: goal.py 18,997 now, 8,272 moved, about 10,850 left; flow.py 18,982, 7,210, about 11,920; lane.py 18,993, 7,222, about 11,890; fit.py 20,443, 9,274, about 11,320; role.py 20,380, 8,633, about 11,880; routing.py 20,469, 8,035, about 12,550; merge.py 18,990, 7,095, about 11,990. The after figure adds the re-export line, the registration line and the import line (about 120 to 200 bytes); every script ends with more than 6,000 bytes of room, the smallest about 6,450.
- Each new module is its moved bytes plus about 250 bytes of header and imports: goal_steps about 8,500, flow_steps about 7,500, lane_run about 7,500, fit_budget about 9,500, role_gate about 8,900, routing_pick about 8,300, merge_steps about 7,350. All under 19,000. guards.py (20,390) is not touched and is not in the table; the sizing hooks in guards.py, role.py (bump_version stays in role.py), flow.py (depth_rule keeps its decorator) and board code stay where they are.
- Functions are moved in this order, one script at a time, committed one script per commit: goal, lane, routing, role, fit, flow, merge. After each commit the move check and that script's own toy rows run singly.

### 2a. Moved functions that refuse or allow an action (they move unchanged; the red team must see them)
- role.py to role_gate.py: `guard` refuses a goal step outside a worker (NOT_WORKER); `recorded_gate` refuses rerunning a recorded step and refuses while the step still runs (ALREADY_RECORDED), and `--again` clears the step and every later one; `over_caps` refuses a goal that adds test rows while the repo is over a test cap; `markers` supplies the full-review marker strings that the record check refuses a reply without; `record` and `lane_part` write the lane bookkeeping commit and the lane part of a record (a failure only prints a NOTE).
- merge.py to merge_steps.py: `base_moved` refuses the merge when the base moved in paths the goal's rows reach (BASE_MOVED) or cannot be fetched (BASE_FETCH); `missing_ids` names the requirement ids that hold the merge back; `advance` merges the release pull request once its checks allow, so it allows an action (a merge); `file_issue` files an issue.
- The move check proves each of these is byte-identical to the base after the module prefix is removed, so none changes what it refuses or allows; the toy also runs one refusal of each (a non-worker step, a rerun of a recorded step, a merge on a moved base) on the head and on the base and compares the words.

### 3. The move check (dev/toy/move-check.py, new; one toy script dev/toy/test-make-room.sh runs it)
- Input: a manifest inside the toy listing, per moved function, the old script, the new module and the `g.` names. The base text comes from `git show <merge-base>:<path>`.
- For every moved function it proves: (a) `ast.dump` of the new function, after removing the `g.` prefix from the listed names, equals `ast.dump` of the base function; (b) the source text equals the base text once those `g.` prefixes are removed (so comments, strings and formatting are identical); (c) the function is gone from the old script and present in the new module exactly once; (d) the old script re-exports it by name.
- Whole-file proofs: the set of every string constant in the old script and its new module equals the base script's (no output line, flag, command or setting name changes); `python3 script.py --help` for each of the seven scripts and for every argparse subcommand prints the same text as the base; every name the base script defined at top level is still defined there (by definition or by re-export).
- Negative controls (seen red): change one byte inside a moved body; drop a re-export; rename a moved function; add a string constant: each makes exactly its check fail.
- Size proof: size-check on the seven scripts and the seven modules: each script at most 13,000 bytes, each module under 19,000, every script under 20,480.

### 4. Rows and tests
- Rows linked v110-make-room:1 to :5, one per done line, each added with `regression.py add` and seen red with `regression.py red --break` on a fixture that breaks only that line (line 1: pad one script past 13,000 bytes; line 2: change one moved byte; line 3: remove a module from the package listing; line 4: change one help text; line 5: pad a script past 20,480).
- Single rows from the clean environment after each script's commit: pods-size, package-passes, listing-names-every-command, release-static-rules, and every row whose command reads the moved script (found with regression.py reads). The full affected set runs once in the qa lane. No row goes to a known or skip list.

### 5. Risks
- Import cycles: the new module imports its script and the script imports the module at its end. Mitigation: the registration line, and a toy case that imports each new module first and each script first.
- A caller that reads an attribute off a module while the module is half built. Mitigation: re-exports sit at the very end of each script.
- Scripts run as `__main__` in lanes and by the flow: the toy runs each script by its path with `--help`.
- Windows: `python3 -E -s` lone runs of the new modules.

### NOT in scope
guards.py; any new behaviour, command, flag or setting; renaming a function; trimming a docstring or comment; the sizing, board or monitoring code.

### Verification
move check green and seen red; every row that passed on the merge base passes on the head; size-check; pods-size and the package rows; `docs.py check` clean; the committed text scanned for the service repo name.

## Review record

(filled by the plan review)
