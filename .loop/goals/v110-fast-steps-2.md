# Implement DEL-19's one step list, step logging, causes and the per-release summary (v1.1.0 task 5, part 2)

- Slug: v110-fast-steps-2
- Touches: skills/workflow-delivery, skills/workflow-monitoring, skills/workflow-docs, skills/workflow-release, dev/toy, .loop/regression.tsv, docs, .loop/docs.tsv
- ETA: 285 active minutes (estimate 226m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given every DEL-19 (revised) test case on its page, then each runs as a real test linked to its requirement and passes, and each fails on a fixture that breaks only that rule.
2. Given a goal, then it runs DEL-19's one step list (freeze, plan, build, quick checks, tests, merge, after the merge, release), used by every feature, report and the board. Each step logs start, end, minutes, tokens and result; a step that goes wrong logs what happened and why; each cause gets one suggested fix, filed once and grouped with repeats; every release shows a per-step summary, worst first; and the steps page is generated from the code.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, new files stay within MAX_FILES (a new file under skills/ only after the release-gate change allows it), no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

1. In this repository run `python3 skills/workflow-docs/scripts/steps_page.py show v110-fast-steps-2`.
   Expect: eight rows named freeze, plan, build, quick checks, tests, merge, after the merge and release, each with its start, end, minutes, tokens and result.
2. Run `python3 skills/workflow-docs/scripts/steps_page.py file`.
   Expect: one `preview:` line per cause (a `<step>:<CODE>` key with its goals and one fix), or "no step cause is recorded here"; nothing is written to GitHub.
3. Run `python3 skills/workflow-monitoring/scripts/monitor.py report`.
   Expect: the STEP column, the waiting asks and the findings name steps by the list (a goal in review shows `tests`, never `qa` or `ship`).
4. Run `python3 dev/toy/test-steps-safe.py`.
   Expect: it ends with ALL PASS; its cases show a save refusing a held lock (LOCK_TIMEOUT) and an unreadable run record (RECORD_UNREADABLE).
5. Run `python3 skills/workflow-docs/scripts/docs.py check --base origin/main`.
   Expect: `DOCS OK: 17 pages`.
