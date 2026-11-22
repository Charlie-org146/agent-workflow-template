# Plan: v120-confidence-subreqs (revised to the KNOWN half only, TD945)

Review: gstack was absent on this PC. Three read-only subagents stood in for the full review (plan head defd09394), then the Mac's gate 1 (record via notify.py plan-record) added B2, B2 and several R/A/C items. TD945 (top) agreed the split: this goal is the KNOWN half only. The sub-requirement half (declaring DEL-3.n, widening criteria.ID and tests.ID, a Requirements-section-only read via sections.body(text, "Requirements"), the indented sub-bullet grammar, the 99% cap, the FAIL+KNOWN naming rule, UNDATA ordering, README/Home link resolution) moves to v120-del3-text, which decides and tests it together against real data. DEL-3's single merge waits for both halves.

NOTE on frozen done lines: lines 1 to 3 mention sub-requirements, which this goal no longer builds. They cannot be met as written; operation-pc decides the re-freeze (a new goal) before any build. Proposed text is in the PC's message to operation-pc.

## Limits
render.py (18,737 LF bytes) is not touched. sections.py is 11,575 LF bytes; the change adds well under 300 bytes. No file newly crosses 19,000 or 20,480 (measure LF bytes of every touched file, docs too). No comment or docstring trimming (GRD-20).

## Meaning
`confidence()` keeps PASS and FAIL and now also keeps KNOWN, counted as not passing: it enters the total, never the passing count. Only the REAL latest state counts: a row that passes, is SKIPPED, or never ran is unchanged (no overlay of regression-known.tsv; a known id that passes stays PASS). Format is unchanged: `NN% (P of T)`, UNDATA with no counted rows. A feature with no KNOWN row returns the exact old string. Row matching stays exact (`t[3] in ids`).

## Build steps
1. sections.py: the filter in `confidence()` becomes `("PASS", "FAIL", "KNOWN")`; nothing else. The kept-figure regex, tables(), fresh() and their signatures are untouched (the cell format does not change, so keep mode is unaffected).
2. dev/toy/test-confidence-known.py (`# windows: ok`, `# reads:` header, Value docstring), cases C1 to C6: C1 a KNOWN row lowers the score and enters the total ("1 of 2" style); C2 a PASS row listed as known stays passing; C3 a never-run row and a SKIPPED row stay out of the total; C4 no KNOWN: exact old strings (`67% (2 of 3)`, `33% (1 of 3)`, UNDATA) byte for byte; C5 all-KNOWN gives `0% (0 of N)`, never UNDATA and never 100%; C6 keep-mode round trip of a cell from a real render. test-follows-adoption stays green unchanged.
3. .loop/regression.tsv: ONE new row (REG-4: one row per script and requirement), id `confidence-known-not-passing`, level land, goal DEL-21, category criterion, command `out=$(python3 dev/toy/test-confidence-known.py 2>&1); echo "$out" | grep -qFx "ALL PASS"` style with no FAIL line, and its Checks text names C1 to C6. Negative control: `regression.py red --break` with a `python3 -c` one-liner that puts the filter back to `("PASS","FAIL")` (and fails if the file did not change); it goes red on C1 and C5. Everything is committed before `red` (it runs on a detached HEAD and rewrites seen_red, a second commit).
4. Docs: only the sentence stating the confidence rule (Principles/Regression, README only if it states it): KNOWN counts as not passing. No re-render; `docs.py check` (keep mode) stays green; committed cells are left to the next live render.
5. Score listing for the PR: a script that loads `git show main:skills/workflow-docs/scripts/sections.py` and the worktree copy and runs both over README.md and docs/wiki/Principles.md with the SAME input, the real latest states from `latest_full` (live gh), or, if gh is down, regression-runs.tsv as it is with no overlay. It prints every cell that differs. Expected: only features whose real latest state has a failing-by-known row move (the Mac's gate expects REG-4 and SET-10). The PR quotes the command and its output and says the cells are not committed.

Gates before push: private.py scan, package check, LF byte counts of every touched file, docs check, `regression.py red` for the one new row, follows-adoption still green.

## Out of scope
The sub-requirement half (above), render.py, DEL-3's text and rows, known-list edits, any live render committed from this branch.

## Decisions for the owner
none beyond operation-pc's re-freeze of done lines 1 to 3.
