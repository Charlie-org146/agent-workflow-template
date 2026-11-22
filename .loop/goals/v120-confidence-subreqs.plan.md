# Plan: v120-confidence-subreqs

Review: gstack was absent on this PC, so three read-only subagent reviewers (scope, engineering, regression rows) stood in for the full review; every finding is folded in below. Nothing was set to condensed. The Mac's independent gate follows (gate-5 asked for the reading in step 2, now step 2 and test T1).

Limits: no file newly crosses 19,000 or 20,480 LF bytes (measure LF bytes of every touched file, docs included: `tr -d '\r' < f | wc -c`; the checkout is CRLF so raw `wc -c` overstates). No comment or docstring trimming (GRD-20); if sections.py nears 19,000, move helpers out and stop. render.py (18,737 LF bytes) is untouched.

## Meaning (the reading the Mac gate asked to be proven)
- A sub-requirement is `ID.n` for the feature's own ID (the first ID in the row's bracket). Declared subs are the bullets `^[ \t]*- ID\.(\d+):` (regex built with re.escape) on the feature's page. Absorbed IDs' subs count only through rows. A row keyed to an undeclared `ID.n` still counts toward the feature and is never named untested.
- Exact segments only: row key matches `re.fullmatch(re.escape(id) + r"(\.\d+)?", key)`. DEL-1 never claims DEL-10 or DEL-1.x of another feature; DEL-3.1 never matches DEL-3.10.
- A PASSING `ID.n` row counts as passing. A declared sub with no PASS row is untested and named: no row, SKIPPED or never run, or KNOWN only. A sub whose only row is FAIL is failing, not untested (counted as FAIL, not named).
- Denominator: counted rows (PASS, FAIL, KNOWN; SKIPPED stays out as today), plus 1 per declared sub with no counted row at all. A KNOWN row is already in the denominator, so a KNOWN-only sub is named but never counted twice. So any declared sub without a PASS row keeps the score under 100%.
- Cell text: `NN% (P of T; untested DEL-3.4, DEL-3.5)`. No subs and no KNOWN: the exact old string `NN% (P of T)`; no data: UNDATA as today.

## Build steps
1. sections.py: `subs(page, fid)`, and `confidence(row, tests, runs, subs=())` (new parameter last, default, so test-follows-adoption lines 42-43 run unchanged). `tables(text, tests, runs, keep, pages=None)` (appended after keep; line 47's positional `True` stays keep). `fresh()` reads the page: last path segment of the first `](...)` target (bare `Delivery` or a wiki URL), anchor and `.md` stripped, `folder/<seg>.md` through `read`; a missing page or no link means no subs.
2. Keep path: widen the kept-figure regex at sections.py line 150 to `\d+% \(\d+ of \d+(; untested [^)]*)?\)$|not measured`, so check mode (keep=True, runs={}) never reports the new cell as stale. With runs={} a feature with subs reads "not measured" as today.
3. dev/toy/test-confidence-subreqs.py (`# windows: ok`, `# reads:` header, Value docstring): T1 a passing DEL-3.n row counts as passing and a missing or KNOWN DEL-3.n counts as untested and named; T2 one untested sub never 100% (negative control: with the declaration removed it reaches 100%); T3 KNOWN row not passing (no subs), SKIPPED stays out; T4 FAIL-only sub is `0 of 1`, not named untested; T5 KNOWN-only sub named, counted once; T6 boundaries DEL-1/DEL-10 and DEL-3.1/DEL-3.10, and DEL-31 vs DEL-3; T7 undeclared sub row counts, never named; T8 exact old strings (`67% (2 of 3)`, `33% (1 of 3)`, UNDATA) and the keep-mode round trip of a cell with an untested list; T9 page resolution from a bare name, a wiki URL, a missing page.
4. .loop/regression.tsv, one row per behaviour, each selecting its own PASS line from the toy (`out=$(python3 dev/toy/test-confidence-subreqs.py 2>&1); echo "$out" | grep -qF "PASS: ..."`), goal DEL-21, category criterion: sub rows count (break: match back to equality), KNOWN not passing (break: filter back to PASS/FAIL), untested named and never 100% (break: drop the +1), old strings unchanged (break: change the format string), boundary (break: startswith). Breaks are `python3 -c` one-liners that fail if the file did not change; everything is committed before `regression.py red --break` (it runs on a detached HEAD and rewrites seen_red, a second commit).
5. Docs: only the sentence stating the confidence rule (Principles/Regression pages, README if it states it). Cells are re-rendered with fixed inputs, never live `gh`: tests from regression.tsv, runs from regression-runs.tsv with every id in regression-known.tsv overlaid as KNOWN (as actions.py does), and only cells this change moves are committed. `docs.py check` (keep mode) stays green.
6. Score listing for the PR: a script loading `git show main:.../sections.py` and the worktree copy with those fixed inputs over README.md and Principles.md, printing every cell that differs. Expect: no sub-requirement effect on main (no `ID.n` rows or bullets exist), movement only for features with KNOWN rows (e.g. DOC-25, REG-4, SET-10, CHK-1, OPS-1, DOC-2, HLT-2, DEL-9, DEL-1, AUT-1, SET-1). The PR says the evidence for done line 2 is toy-only until v120-del3-text lands DEL-3.1 to 3.10.

Gates before push: private.py scan, package check, LF byte counts of every touched file, docs check, `regression.py red` for each new row, existing rows (follows-adoption) still green.

## Out of scope
render.py, DEL-3's text and rows (v120-del3-text), known-list edits, the nightly workflow, wiki churn beyond the confidence sentence.

## Decisions for the owner
none. The declaration grammar (`- ID.n:` bullets on the feature's page) is the recommended default; the Mac gate may overrule.
