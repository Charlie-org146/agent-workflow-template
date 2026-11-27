# Test levels G3 (LVL-1.2; owner o980, o985; split TD1749): L2 full runs every row and a skipped row is red

- Slug: v110-lvl-l2
- Touches: skills/workflow-regression, .github/workflows, dev/toy, .loop/regression.tsv, skills/loop-files.md, .loop/regression-relevel.tsv, docs/wiki/Tests.md, docs/wiki/How-to-use-Guardrails.md, docs/wiki/Regression.md, skills/workflow-regression/scripts/actions_write.py
- ETA: 385 active minutes (estimate 306m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a row that no change has reached for 30 days, when L2 runs, then the row runs and its result is recorded.
2. Given a shard that runs out of job time with rows left, when L2 ends, then the run is red and one issue names each skipped row.
3. Given a row that fails at L2, when the run ends, then one issue is open for it, the main-red goal names it, and main has no revert commit.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. Run `gh workflow run regression.yml -f target=L2`. Expect: the summary's first line reads `L2 GREEN`, `L2 RED` or `L2 INCOMPLETE` with counts, then the covered lines and, on main, an `L2_VERDICT` line.
2. Run `gh workflow run regression.yml -f target=L3`. Expect: the summary's first line is `REFUSED (BAD_TARGET)` naming L2 among the targets, and the run is red.
3. If any row was skipped without exemption or left unfinished, open the issue `Regression: L2 skipped rows`. Expect: every skipped or unfinished row with its cause and a fix line.
4. List open issues labelled `l2-red`, then open the issue `Regression: L2 failing rows` (or the open `main-red` issue). Expect: one `L2 red: #n` line for each, and no revert commit on main.
5. Search the generated `.github/workflows/regression.yml` for `git revert`. Expect: no match.

## Notes

Departures from the plan (the reviewed text), each with its reason:

1. The summary step calls l2.py directly (check, issues and summary); tests.py does not load it. The plan's item 19 had tests.py load l2.py by path on the L2 path. Same outputs, tests.py untouched.
2. The verdict is computed over the set of expected row ids, not per shard split (item 9). The rebuilt set is the same land and nightly rows the shards split among them; a row with no result line is unfinished either way.
3. The published artifact `l2-verdict` holds one line, `L2_VERDICT <sha> red|incomplete|green`, written by l2.py's summary command on main only; no row id, output or free text.
4. Check 12 (a silent failing row's second run with no job time left) is covered by the code (`l2_again`) but has no check of its own yet.
5. The step checks for the summary job were written after its code; each fails on the runner commit a104cb061 (12 FAIL there), and all pass here.

## PR notes

- docs/wiki/Regression.md is a widening beyond the plan's Files line (TD2215): three Usage bullets (schedule, steps, full run) now describe L2 and the concurrency rule. No Reviewed requirement text is touched.
- Departures 1 and 2 above are changes to the reviewed plan; the verdict and its outputs are unchanged.
- test-body-file.sh (1 failure) and test-regression.sh (7 failures) fail the same way on main without this change; they have open issues. test-automation-email.sh's "codes documented" also fails without this change.
- The workflow changes (target default L2, concurrency off main only, the copied code block, the summary job, the verdict artifact) have owner approval: o1032. permissions, triggers and secrets are unchanged.
- dev/toy/test-ci-target.sh: two assertions are changed to match, not weakened: the target-input check now expects the nightly target expression, and the bad-target checks expect the same full line with L2 added to the listed targets.
- Check 12 (the second run of a silent failing row with no job time left) was not seen red on its own assertion: on the commit before l2.py it stops with ModuleNotFoundError, which is the missing code and not the check's assertion. It is not claimed as red first.
- No leak-reader pair ran for this goal (o1040); the stored form `leak-readers full 2` does not mean one ran.
- The tool only accepts the stored form 'full' for full-test-run; it does NOT mean a full test run happened (19 of 709 rows ran locally in qa, 17 passed and 2 known on main's list, plus the rows run alone before it); GitHub's full regression run on the PR head is the full-run proof.
- G3's three CI reds (no-done-line-refused, home-guard-catches-leak, toys-set-userprofile) first ran on GitHub: the 15-minute lane budget left them unrun locally (the same gap as #5940; deliver-first v110-one-review-break-7).
- Three guard toys (test-rows.sh DEL-2 and DEL-4-verify, test-docs-link.sh) failed only in a by-hand harness whose mktemp HOME had no git identity; the rows that run them (no-done-line-refused, home-guard-catches-leak) passed through the tool.
- codex-key-commands fails on main in a clean environment (#5895, the Codex fix goal's own issue; GitHub skips it, codex is not installed there); it is not this goal's.
