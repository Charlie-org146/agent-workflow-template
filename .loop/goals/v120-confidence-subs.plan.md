# Plan: v120-confidence-subs (second half of #5790; owner o312; TD945)

Depends on v120-confidence-known (pc-w4, branch loop/v120-confidence-subreqs, plan 24c116e9f): same `sections.confidence()`. PLAN now; BUILD only after that change is on main, then rebase and re-measure bytes.

## Idea
A feature's confidence today counts rows keyed to the feature's top ID (`[DEL-3]`). Sub-requirements ("  - ... [DEL-3.n]" bullets under a requirement) are not IDs, so a row cannot name one and one untested sub does not lower anything. Make `DEL-3.n` a real, linkable ID, count its rows, and never show 100% while a declared sub has no passing row, naming it.

## Findings from the code (verified at origin/main 7b3155d90)
- `criteria.ID = ^[A-Z]{2,5}-\d+$` (criteria.py:40) decides whether a regression row's goal or id links to a requirement (`test_rows`, line 131); `linked` keys feed the Tests table and the "rows link to X, which no page has" check (line 278). `seen` is built from `^- ID: **` lines only, so a sub ID is "no page has" today.
- `sections.confidence` matches `\b[A-Z]{2,5}-\d+\b` on the row's bracket text and compares `t[3] in ids` exactly.
- Sub bullets today carry the parent tag (`[DEL-3]`, Delivery.md:24); v120-del3-text writes `[DEL-3.n]`.
- Sizes (LF bytes): sections.py 11,575, render.py 18,737, criteria.py 20,455 (25 bytes under the cap), pageformat.py 18,933, docs.py 18,458, counting.py 18,948, docs.py, pageformat.py. No file may newly cross 19,000 or 20,480 (GRD-20, no trimming); a crossing is a stop and report.

## Meaning
1. Declaration: only in the page's `## Requirements` section, outside code fences, as an indented line (the new `declared(text)` scans the raw lines, tracks fences and stops at the next `## `, because `sections.body` strips indentation and does not skip fences, so it cannot be reused as is)  `^\s+- .*\[([A-Z]{2,5}-\d+)\.(\d+)\]\s*$` whose parent `ID` is a requirement declared on that page. Text under Retired, Non-goals, Success metrics, Revisions, Tests or in a fence is never read (done line 3). A sub whose parent is Retired/moved is not declared.
2. ID grammar widens to `^[A-Z]{2,5}-\d+(\.\d+)?$` in `criteria.ID` and the Tests-page link path (one shared constant, not copies). A row id or goal `DEL-3.2` links; `DEL-3.2` with no declaring page reports "rows link to DEL-3.2, which no page has" exactly as for a top ID.
3. Confidence per feature row (`[DEL-3, DEL-6]`): counted rows are those keyed to the row's IDs and to every declared sub of those IDs (`t[3] in ids ∪ subs`); a row keyed to a sub counts once. Format `NN% (P of T)` unchanged.
4. Cap: if any declared sub of the row's IDs has no PASS row, the shown value is `min(value, 99)`; `round()` would show 100 at 99.5+, so compute as `min(99, round(...))` only when a sub is untested. The same cell names it: `99% (P of T; untested: DEL-3.4, DEL-3.7)`, list cut after 3 with "+N". A sub counts as tested only if a counted row for it has latest state PASS. FAIL, SKIPPED and never-run are untested. With v120-confidence-known on main, KNOWN is not passing for the cap as for the score (stated rule: a FAIL plus KNOWN row without any PASS is untested).
5. UNDATA ordering: no counted rows at all stays UNDATA even when subs are declared (nothing measured); the cap and names apply only once at least one counted row ran. A feature whose subs exist but whose only rows ran green on the parent keeps its parent score capped at 99 and names every untested sub.
6. No declared subs: byte-identical old string (done line 4).
7. Links: README and Home resolve the same Tests anchors for sub IDs, including `blob/main/docs/wiki/*.md` and `(docs/wiki/` forms (the `LINK` regex in sections.py already strips them); one toy asserts both pages render the same cell.

## Build steps (after v120-confidence-known is on main)
1. criteria.py: one `ID` regex widened; `seen` gains declared subs via a small `subs(text)` helper placed in sections.py (it already owns `body`). If criteria.py would cross a cap, put the helper in sections.py only and keep criteria.py a one-line change; if still over, stop and report.
2. sections.py: `subs(text)` returns `{ID: [ID.n...]}` from the Requirements section; `confidence()` takes the page's subs (optional param, default none, so old callers behave as before).
3. render.py: pass subs into `tables`/`fresh`; the Tests table lists sub IDs under their parent. Touch the minimum; render.py is 18,737, so at most about 260 bytes of budget before 19,000 (stop and report if the change needs more; no trimming).
4. dev/toy/test-confidence-subs.py (`# windows: ok`, `# reads:` header), cases S1 to S10: S1 a DEL-3.n row links in the docs check and the Tests table; S2 untested sub caps at 99 and is named; S3 sub only under Retired, Non-goals, Success metrics, Revisions or in a fence is not declared, not counted; S4 no subs: old strings byte for byte; S5 rows at 100% with all subs passing shows 100%; S6 round() boundary (199 of 200 style) shows 99 never 100; S7 FAIL+KNOWN without PASS is untested; S8 no counted rows is UNDATA; S9 README and Home resolve the same cell for blob/.md forms; S10 a sub whose parent is not declared on the page is refused (LINK finding). One regression row, id `confidence-subs-counted`, level land, goal DEL-21, runs every case; negative control by `regression.py red --break` reverting the cap line (fails S2 and S6) and a second break for the Requirements-only read (fails S3).
5. Docs: one sentence on the confidence rule (sub rows count, the 99% cap, the naming) where DEL-21 says it; no live re-render committed; `docs.py check` and `entry.py check` pass. README only if it states the rule.
6. PR text lists every feature score the change moves: run old and new `sections` over README and Principles with the same live `latest_full` input (as v120-confidence-known's step 5), print differing cells; expected: none move until a page declares `[ID.n]` subs (v120-del3-text), so the listing says so.

## Gates before push of the build
private.py check and scan, package check, LF byte counts of every touched file, docs check, `regression.py red` for the new row, no existing row changes result, one row (REG-4, row cap 600), TD605 toy ban (no bash toy needing Windows-absent tools; the toy is Python).

## Risks and open points
- Merge order: this goal edits `confidence()` that v120-confidence-known edits; rebase and re-read the function before building.
- Sub IDs in `docs.py` PRD copy paths (`prdcopy.ITEM`, `entry.REQ`) accept `ID` only; a `[DEL-3.n]` bullet inside copied bodies is text, not an item, so they need no change; the toy asserts this.
- `counting.py` ID regex finds `DEL-3` inside `DEL-3.2` (`\b` before the dot); S1 asserts counts do not double count a sub as its parent.
- Real data (Delivery.md) tags subs with the parent today; until v120-del3-text rewrites them no feature moves.

## Out of scope
The KNOWN half, DEL-3's text and rows, known-list edits, any live render committed, trimming or reformatting any file.

## Decisions for the owner
None.

## Review round 1 (three read-only agents: feasibility, correctness, scope), taken
Verdicts: feasibility BLOCKED on bytes, correctness 1 break, scope gaps only.

- BYTES (stop point, decision for operation-pc): criteria.py is 20,455, so only the `ID` widening (about 10 bytes) fits. Declared subs must enter `seen` (criteria.py:233) and the Tests table (render.py:171-178, `criteria.table` 164, stale check 263); neither fits criteria.py or render.py under GRD-20 with no trimming. Proposed route, allowed by GRD-20 (moving code to a sibling): create `skills/workflow-docs/scripts/subreq.py` holding `declared(text)` and the sub-aware table helper, and MOVE one existing self-contained function out of criteria.py into it to make room, with `git diff -w --numstat` equal to `git diff --numstat` and no reformat. Which function moves is chosen at build and sized then. If operation-pc does not approve a move, the build stops at the first crossing and reports; nothing is trimmed.
- Feature-page data: confidence is computed from README, Home and Principles text, but subs live on feature pages. `fresh` and `render.refresh` (render.py:324, docs.py:183) read the feature pages (Requirements sections) once and pass `{ID: [subs]}` into `tables`; `latest_full`'s 80% coverage test keeps using the top IDs only.
- Keep mode: the kept-figure regex (sections.py:150) widens to `\d+% \(\d+ of \d+(; untested: [^)]*)?\)$` so a capped cell round-trips; toy S11 renders a capped cell and keeps it. Without this a keep-mode render would overwrite it with UNDATA.
- Row keys: `confidence` counts `t[3]` only while `test_rows` also links on the row id when the goal is `-`; the plan uses `t[3]` only (as today) and S1 asserts a row keyed by goal DEL-3.n counts and links; a row keyed only by its id links in the docs check but is not counted (stated, as for top IDs today).
- SKIPPED: a sub whose only row is SKIPPED is untested and absent from `P of T` (T counts PASS, FAIL, KNOWN only); S12 covers it.
- Shared ID: widening `criteria.ID` also reaches `criteria.py:159` (a defect row may now guard a sub) and `341/354/355` (`review DEL-3.2` is accepted as an ID) and the REFUSED texts at 359 and 367, which quote the old regex. The plan keeps those messages byte-identical by leaving the quoted text alone and adds S13: the old refusals still print as before; a defect row for a sub is accepted and linked.
- Collisions: `counting.py:35`, `pageformat.IDREF`, `entry.REQ`, `prdcopy.ITEM`, `deployments.py:201` match the parent inside `DEL-3.2`. S1 covers counting's `own` and `other` paths; S14 puts a bullet that begins with `DEL-3.2` through `entry.REQ` and `prdcopy.ITEM` and asserts no new item appears. Any fix is a minimal one-token anchor, sized first.
- Scope: this goal replaces the sibling's "sub half" text (v120-confidence-subreqs done lines 1 to 3); v120-del3-text writes the page text only. Conflicts to expect on rebase: `confidence()` lines 128-131, the regression.tsv tail, the DEL-21 docs sentence. S7 (FAIL+KNOWN) and S12 are gated on the sibling and are written after it lands. The PR's score listing uses the sibling-merged `sections.py` as its baseline so KNOWN movement is not charged here. "No existing row changes result" is checked by `regression.py run` before and after on the rows that touch workflow-docs and diffed. The private-name scan covers the toy, the plan and the row text.
- Row count: .loop/regression.tsv has 698 lines today, above the 600 named in the brief; operation-pc to confirm that the cap applies to rows added per goal (one) and not to the file.
- Rounding: `min(99, round(x))` applies only when a sub is untested; the no-sub path is the unchanged `round`.

## Decisions for operation-pc
1. Approve moving one function out of criteria.py into the new sibling `subreq.py` (GRD-20 allows moves) so the sub support fits; otherwise the build stops at the cap.
2. Confirm the 600-row cap meaning (698 lines today).

## No new file: the helper goes into an existing one (operation-pc, package at 100 of 100)
Replaces the `subreq.py` proposal above; the package file count does not change and this goal needs no grd21-cap-lift-2.
- `declared(text)` (the raw-line Requirements scan) and the sub-aware table helper go into `skills/workflow-docs/scripts/sections.py` (LF 11,575; room of about 7,400 to 19,000; it imports only os and re, so `criteria.py` and `render.py` can import it without a cycle).
- To make room in `criteria.py` (20,455, 25 under 20,480) one self-contained function moves to `sections.py` unchanged and is called through `sections.`: candidates `done_count` (criteria.py:147, 9 lines, uses only os and re, one caller at 134) and `defect_rows` (156, 6 lines). The build moves whichever frees at least the bytes the `seen` and `table` edits need, with `git diff -w --numstat` equal to `git diff --numstat` and no reformat. If the two together do not free enough, the build stops and reports; nothing is trimmed.
- If `render.py` (18,737) needs more than about 260 bytes for the sub-aware Tests rows, `tests_table` itself moves to `sections.py` the same way.
- Row count (TD625): this goal adds one row (`confidence-subs-counted`) and needs a grant or an offsetting removal from top; the build does not start until that is answered.
