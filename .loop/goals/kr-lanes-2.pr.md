# kr-lanes-2: known-red rows cleared, and two redesigns found

Per row: cause, fix, proof. Run alone twice, outside any sandbox, with the session's CLAUDE, ANTHROPIC and LOOP variables unset. Six of the eight items are fixed and their known lines removed; two need a redesign and are left red with their known lines in place (see the end).

## guards-resume
- Cause: toy. Commit 9af631e80 made goal reset write an empty report record (`{}`, never null); the g3 section of test-guards.sh still expected `None`.
- Fix: the check expects `{}` (equally strict: one exact value, and test-guards-null-report.sh keeps proving it is never null).
- Proof: `test-guards.sh "" g3` ALL PASS twice; test-guards-null-report.sh ALL PASS; known line removed.

## lane-messages-table
- Cause: product docs. lanes_cli.py prints LANE_MEMORY and fit.py prints LANE_OWED, but the Messages table in skills/loop-files.md had no row for either, so the toy (every printed code has a row) correctly failed.
- Fix: two rows (code, printer, exit, meaning, what to do) written from what the scripts print; the toy is unchanged.
- Proof: `test-lane-messages.sh` ALL PASS twice; known line removed.

## lanes-trace-check
- Cause: toy. lanes_cli.py imports tiers and slots (through lanes), but the check-reads section of test-narrow.sh copied only lanes.py, narrow.py and lanes_cli.py into its fixture repo, so `lanes_cli.py deps` crashed with ModuleNotFoundError and every traced row failed (7 of 7), including the rows meant to pass.
- Fix: the hunk of hrt-monitor's commit e7ec9da66 for dev/toy/test-narrow.sh, applied as it is (it copies tiers.py and slots.py and adds a check that the copied CLI resolves the declared file). The same fix also lands with hidden-red-fixes, so the two branches carry an identical hunk. The expected failures (rows r4 to r7) are still asserted, unchanged.
- Proof: `regression.py run lanes-trace-check` passed twice; test-narrow.sh ALL PASS; known line removed.

## st-union-contexts (three parts of test-statuses.sh, each failing for its own reason)
- union: toy. tests.py classify() (#3840/#4537) posts a status only for a required check some workflow job provides, and says `BLOCKS: <check> cannot be run here` for one with no job. The fixture's classic protection requires lane-c but its workflow had no lane-c job. Fix: the fixture workflow gets a lane-c job (regression-only), so lane-c is postable as the check expects; the never-post-a-bound-check assertions are unchanged.
- postfails: toy. The check grepped goal.py for the old statement `state["statuses"] = "ok" if private.pr_result`; goal.py now writes it as `state.update(..., statuses="ok" if private.pr_result(...))`. Same behaviour, so the check greps the new text (the exit-5 line is unchanged).
- release: toy. merge.py imports autorelease as ar, so the check greps `ar.release_statuses(top, cfg, state` instead of `autorelease.release_statuses(top, cfg, state`.
- Proof: `regression.py run st-union-contexts` passed twice, and test-statuses.sh (all parts) ALL PASS twice; known line removed.

## lanes-headers (valid # reads: headers half) and repo-narrow-178
- Cause: toy headers and one toy regex. `lanes_cli.py check` reported 25 header problems in 19 files (7 headers placed after code, so ignored; 8 toys reading all of skills/ without declaring it; 5 reading a whole skill folder without declaring it; 2 declaring skills/ with nothing reading it whole; 2 with no header; one row naming the nonexistent dev/toy/test-x.sh as a script). Separately, repo-narrow-178's own check grepped the closure for `^\.git`, which also matches `.github/workflows/`, a path tests.py now reads, so a full clone was judged to depend on git's store.
- Fix: moved or declared each header as the check's own fix line says (no check changed), the row names an existing helper as $0, and the regex is now `^\.git(/|$)`, tested against `.github/workflows/` (accepted) and `.git/objects` and `.git` (refused).
- Proof: lanes_cli.py check exits 0; tree-once shows the valid-header PASS line and the .git/ line.

## toy-no-leftovers
- Cause: toy hygiene. The test's static check (every dev/toy/test-*.sh sources reap.sh on the line after `here=` and sets no trap) found 13 findings in 9 toys: test-adoption-golden, test-automation-budgets, test-docs-sections, test-lanes-abs-path, test-owed and test-package-win lacked the source line; test-machine sourced it two lines late; test-entry-config, test-package-win and test-migration-v1 set their own EXIT/TERM traps. The land-set part passed.
- Fix: each toy sources reap.sh right after `here=` (the rule the check asserts), and the toys that had their own cleanup or trap now register it with toy_on_exit; test-migration-v1.sh now takes `here` as the repo root like the others and keeps its temp copy under dev/toy. No assertion changed. Not every toy registers a cleanup: test-lanes-abs-path.sh still leaves the folder its `mktemp -d` makes (it removes that folder and recreates it, and never removes it at the end). That is how it is on main too, a pre-existing leftover this goal does not change, because the check asserts only the source line and the traps.
- Proof: test-no-leftovers.sh ALL PASS (263 s) and `regression.py run toy-no-leftovers` passed; the nine toys still give the results they gave before (test-docs-sections and test-entry-config fail the same way on main for unrelated reasons: a DOC-25 case and a BSD sed call in the toy); known line removed. Memory was 54-61 percent free for the heavy runs.

## lanes-trace (NOT fixed here; #5693)
- Finding: `dev/toy/check-reads.sh` runs every land row's command serially under a Python audit hook. The newest full-suite times in the common git dir's suite-times.tsv are about 17,900 s of row time, so the trace cannot finish inside the row's 900 s limit however it is run. Measured: after 10 minutes it had traced 4 of about 625 distinct commands; I stopped it and checked that nothing was left running.
- Needs: shard the trace (per-shard rows or parallel workers) so each shard fits the limit; that is the sharded trace of #5693.

## rerun-fraction check behind lanes-headers (NOT fixed here; #5694)
The check ("a one-file change reruns fewer than half the land rows") fails because a `batch.py` change reruns 632 of 644 land rows (half is 322). The valid-header half of lanes-headers is fixed (see repo-narrow-178 above); this half is not. Measured on a scratch clone, not committed:
- 100 rows are ALWAYS (they run tools on the repo's own files); 532 more reach batch.py through their closure.
- Finding 1, a product bug: `narrow.py` `header()` reads `# reads:` headers only from .sh and extension-less files, so the headers of the 156 Python toys that declare them are ignored and 271 rows fall back to the wide mapping. Honouring `dev/toy/*.py` is a one-line change, and `lanes_cli.py check` then reports 13 header problems in those toys to fix (8 LANES-DECL-FOLDER-UNBACKED and 5 LANES-DECL-MISSING). Alone it moves 632 to 628. It is not shipped here: it would narrow 271 rows to headers the trace has not proven, so a row could under-run and a stale result could pass the merge gate. It must land with the sharded trace.
- Finding 2, the mesh: nearly every skill script reaches batch.py through cross-skill by-path loads and subprocess runs, so cutting one edge only moves the shortest path to the next. Shortest-path edge counts over the narrow rows after finding 1: guards.py to sessions.py 456 rows; render.py to settings.py 442; board_lines.py to fit.py 431; worker.py to merge.py 391; review.py to health.py 273; lean.py to setup.py 232; setup.py to unattended.py 228; deployments.py to auto.py 207; workflows.py to private.py 207; agents.py to workflows.py 207; fit.py to entry.py 206; milestone.py to board_status.py 201; tests.py to deployments.py 176. Before finding 1 the leading edges were watch.py to guards.py (209), tests.py to deployments.py (193), render.py to tests.py (174), fit.py to wiki.py (171), role.py to lanes_cli.py (165), deployments.py to auto.py (160), lanes_cli.py to private.py (158), private.py to milestone.py (138), board_page.py to goal.py (136), merge.py to machines.py (124), proctree.py to govern_hook.py (124 and 85 for the regression copy).
- Marking those loads `# lanes: no read` would narrow the rows only if the lazy loads are not read by those rows, and many of these files sit within about 100 bytes of the 19,000-byte cap (proctree.py is 18,995). An annotation on the proctree.py load alone changed nothing (632 stayed 632). The proof is the sharded trace.

## Not fixed here: lanes-trace (#5693) and the rerun fraction (#5694)
Neither is fixed in this pull request. The owner ruled (owner record o684) to redesign both before v2.0, each in its own goal: lanes-trace-shard (the sharded trace, #5693) and rerun-fraction (the rerun fraction, #5694). Their known lines stay exactly as on main: the known line for lanes-trace, and the one for lanes-headers (it names package-cap-3).

## Not touched
- The rerun-fraction check stays red (#5694).
- test-tree.sh still reports three repo-health traceability lines (#88, #5635, #5638: closed with no defect test). They belong to other goals.
- `.loop/regression-runs.tsv` is left as committed; the runs of these rows were not recorded.
