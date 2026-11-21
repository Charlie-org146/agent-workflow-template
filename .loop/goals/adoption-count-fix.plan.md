# Plan: adoption-count-fix

## Implementation plan

Checked against the code: `follows()` (sections.py:99) and `adoption()` (sections.py:121) exist; `adoption()` has one caller, the row loop at sections.py:165, and reads `follows()`. The toy is `dev/toy/test-follows-adoption.py`; the render is `skills/workflow-docs/scripts/criteria.py render`.

The done lines are the three frozen lines in `.loop/goals/adoption-count-fix.md`. The steps below are authoritative; the accepted-obligations block in the review record restates them.

Split rule (one rule, used everywhere below): a bullet is scanned once, splitting at `; ` only outside brackets and parentheses and only when the text since the last split is a complete `source: tag` pair; the tags are `adopted`, `adapted`, `planned` and `own`, lower case, as in `TAGS`. If any resulting part is not a complete tagged pair, the whole bullet stays one source with the tag it would have had on main (main reads a tag only at the very end of the bullet). A line break between bullets is the literal `<br>` the README tables use. A source is one `name: tag` pair; references grouped under one tag (as in DEL-1) are one source, and auditing grouped references is out of scope.

Built and pending, at a glance. Built in dce2f7ea: follows() with the split rule (before the three corrections below), adoption(), the two-source case, the single-source values, four semicolon-in-source negative controls, the unknown-tag control, the generated pages. Pending: the three corrections in step 1, the edge cases, the README check (C1), the hand-written fixture (C5), the re-render after the corrections, the docs re-stamps.

A complete pair, defined once: the part ends with `: ` and one of the four tags as its last characters (text after the tag, such as `adopted (v2)`, means the part is not a pair, exactly as on main), and the separator between sources is `; ` (semicolon and a space). Brackets and parentheses must balance as typed pairs across the whole bullet.

Build steps, in order:

1. `follows()` applies the split rule above. Built in commit dce2f7ea, with three small corrections still to make (CEO and Eng reviews, each with a counterexample on the branch): (a) a part that starts with `;` or whitespace is not a complete pair, so a doubled `; ;` falls back to one source; (b) in a bullet that splits, a part that still holds a `; ` outside brackets and parentheses is malformed, so the whole bullet falls back (`a: adopted; b: unknown; c: adapted` gave 50 on the branch and 0 on main; one source, 0 after the correction); (c) delimiters must balance as typed pairs across the whole bullet, so a bullet with an unmatched or mismatched bracket falls back (`a: adopted; [b: adapted` gave 50, one source and 0 after the correction). `follows()` has one caller outside the toy, `adoption()` at sections.py:123, so only the Adoption cells can move; render.py imports sections for its tables and does not read the pairs itself. Apart from that this step is verification; the negative controls are run against main's counter (`git show origin/main:skills/workflow-docs/scripts/sections.py` loaded as a module) to see them fail there, and against the branch to see them pass.
2. `adoption()` counts adopted sources over all sources; adapted, planned and own count 0; no sources is not measured; the share is rounded to a whole percent with the same Python `round()` expression main uses (ties go to the even number, unchanged). Docstring wording only: "The share of a row's Follows sources tagged adopted (adapted, planned and own count 0); None with no sources."
3. The toy already holds (built in commit dce2f7ea) the two-source case, the single-source values, four semicolon-inside-source negative controls and the unknown-tag control. Still to build: the edge cases listed under done line 1, and one independent check on this repo's own README (C1, accepted in the CEO review, S, one file already in the diff). The check, as an exact definition: a Follows cell is every table cell of a README row that starts with `- `; for each bullet (the cell split at the literal `<br>`), remove text inside brackets and parentheses by repeatedly deleting innermost pairs with the regular expression `\[[^\[\]]*\]|\([^()]*\)` until nothing changes (its own, not `follows()`'s depth scan; this handles nested brackets and a link target with nested parentheses), then count the matches of `: (?:adopted|adapted|planned|own)(?=; |<br>|$)` (no spaces around the tag, a whole word, lower case, and a `; ` with its space as the separator, like the split rule); a bullet with no match counts as one expected source; the cell's expected count is the sum, and it must equal `len(follows(cell))`. The toy asserts that at least one cell was found, fails with a non-zero exit on any mismatch (so a missed split fails it, and so does a half-tagged bullet such as `a: adopted; b: adapted; c`, which is the deferred C2 finding applied to this README inside the toy only), and carries a negative control: on a synthetic two-source cell a one-line copy of main's one-tag reading fails the same check while the branch's `follows()` passes. A one-off run of this definition on the current README gives 27 cells and 0 mismatches. The toy already runs as the `follows-adoption` row (land) of `.loop/regression.tsv`; that row exists and is unchanged. A hand-written fixture (C5, accepted in the CEO review as a third reference that comes from neither parser): five cells with source counts written by hand in the toy: three shaped like the README's HLT-2, MCH-1 and DEL-1 rows, one with nested brackets and one half-tagged. The check detects a bullet with two or more tagged parts that the counter reads as one (for example `a: adopted; b: adapted; c` and `a: adopted (v2); b: adapted`); a single-token half-tagged bullet such as `a: adopted; b` is not flagged, and C5 is the arbiter for what the correct count is. The toy never touches git history: main's one-token reading is a one-line copy, and the `git show origin/main:...` comparison is a build-time check only. On a mismatch the toy names the cell and the expected and actual counts, and says the check strips brackets by innermost pairs. Home and Principles are rendered from the same Follows cells, and `render --check` proves each page equals a fresh render.
4. `criteria.py render` rewrites the Adoption cells and headlines in README, Home and Principles on the merge of origin/main that is on the branch (48ac06e7d, v1.0.105 line). A later merge of main re-renders and the figures move with it; the figures are produced by the render, never typed.
5. `docs.py check --own` and `criteria.py render --check` pass; stale own pages are re-stamped (stamp lines only).
6. C2 (a docs-check finding for a half-tagged bullet) is not built and TODOS.md is not edited here, because done line 3 limits the diff. It is recorded in this plan (ledger row C2) and in the Follow-ups line of the PR body, which delivery writes from this plan; the follow-up also asks docs check to enforce one `source: tag` pair per line, which would make the heuristic unnecessary.
7. The PR body states that the correction lowers the published Adoption figures and that this is intended (Operation ruled MCH-1's requirement text stays unchanged). Delivery re-derives the base merge and the rendered figures at ship time.

Test for each done line (a negative control is seen failing on main's counter):

- Done line 1: a two-source bullet (adapted; adopted) returns 50 (checked: main returns 100, one source whose text holds the whole bullet); single-source bullets (adopted, adapted, planned, own, and a four-bullet cell) return main's values; a semicolon inside `[A; B](u)`, `[A: adopted; B](u)`, a link target, or a bare `A; B` does not split; an unknown tag does not split. Edge cases with the expected result on the branch: a three-source bullet `a: adopted; b: adapted; c: planned` gives three sources and 33; `a: adopted; b: adapted; c` (last part untagged) stays one untagged source and 0; a trailing `a: adopted;` stays one untagged source; `;` with no following space does not split; an unbalanced bracket does not split; an upper-case `Adopted` is not a tag, so it does not split; a doubled `; ;` falls back to one source (after correction (a)) with the tag main reads at the end of the bullet; `a: adopted; b: unknown; c: adapted` and an unknown or upper-case tag in the middle fall back to one source and 0 (after correction (b)); `a: adopted; [b: adapted` and a mismatched `[a)` fall back to one source and 0 (after correction (c)); `a: adopted (v2); b: adapted` stays one source and 0 because the first tag does not end its part; `a: adopted; b` stays one untagged source and 0; the nested-bracket source `[outer [inner] label: adopted; tail](u): adapted` is one source tagged adapted (hand-counted, 0). For these fallback cases main gives the same result as the branch.
- Done line 2: after render, only the HLT-2 and MCH-1 cells and the two headlines that average them change (informational, not acceptance numbers: HLT-2 cell 33 to 25 percent, MCH-1 cell 25 to 20 percent, headline of principle 2 (Sensed: enforced, verified and honest, which holds HLT-2) 43 to 42 (a headline is the rounded average of the rounded row shares, as `tables()` computes it) and headline of principle 5 (Reproducible, portable and adoptable, which holds MCH-1) 45 to 44; these figures are checked at the merge of origin/main on the branch only, and the durable check is that `render --check` passes and only these two rows and their two headlines differ from main); `render --check` prints TABLES OK and `docs.py check` passes.
- Done line 3: `git diff origin/main...HEAD --stat` lists only `skills/workflow-docs/scripts/sections.py` (12,196 bytes, under 19,000), `README.md`, `docs/wiki/Home.md`, `docs/wiki/Principles.md`, `dev/toy/test-follows-adoption.py`, `.loop/goals/adoption-count-fix.*`, the goal's own `.loop/kept/` and `.loop/lane-results/` records, and stamp-line-only changes in `docs/wiki/*.md`; no requirement text, tag or Follows line differs; the private-names scan is clean.

What could break:

- A Follows line whose source text holds `; ` followed by something shaped like `x: adopted` inside prose, which would split wrongly. The bracket and parenthesis depth rule and the all-parts-must-be-tagged rule make it fall back to one source.
- A page re-render reordering unrelated cells. Checked by diffing the render: only the two rows and their headlines move.
- sections.py growing past the size cap. It is 12,196 bytes.

Out of scope: any requirement text, tag or Follows line; MCH-1 is not raised from the 20 percent the corrected counter gives it (Operation's ruling: no change to its requirement text); the Adoption definition itself; other generated pages.

PENDING: none for the owner.


<!-- autoplan-accepted:ceo -->
- follows() applies the split rule stated in the plan: split at `; ` only outside brackets and parentheses and only after a complete `source: tag` pair (tags adopted, adapted, planned, own, lower case); if any part is not a complete tagged pair the whole bullet stays one source. Verified by the two-source toy case returning 50, the edge cases listed under done line 1, and negative controls for a semicolon inside a link, a source name, a link target and an unknown tag.
- adoption() counts adopted sources over all sources; adapted, planned and own count 0; no sources is not measured. Single-source cells keep main's values (toy).
- criteria.py render rewrites only Adoption cells and headlines in README, Home and Principles; after the merge only HLT-2 and MCH-1 cells and their two headlines change; `render --check` prints TABLES OK and `docs.py check` passes.
- The toy compares, for every Follows cell of this repo's README, the count of `: <tag>` tokens (the same four tags, text inside brackets and parentheses removed first) ending at `;`, a line break or the end of the cell with `len(follows(cell))`, counted outside follows() as defined in step 3 (an untagged bullet counts as one source, a half-tagged bullet fails it), a mismatch failing the toy, with at least one cell required (C1).
- follows() also treats a part that starts with `;` or whitespace as not a complete pair (a doubled `; ;` falls back to one source); a source is one `name: tag` pair; the toy carries a hand-written fixture of three README-shaped cells with hand-counted source counts (C5).
- Diff limits: sections.py under 19,000 bytes, no requirement text, tag or Follows line changes, private scan clean, only the listed files change.
<!-- /autoplan-accepted:ceo -->

<!-- autoplan-accepted:eng -->
- follows() keeps the split rule and adds three corrections: (a) a part that starts with `;` or whitespace is not a complete pair; (b) in a bullet that splits, a part that still holds a `; ` outside brackets and parentheses makes the whole bullet fall back to one source with the tag main reads at the end; (c) brackets and parentheses must balance as typed pairs across the whole bullet, else the bullet falls back. A complete pair ends with `: ` and one of the four lower-case tags as its last characters; the separator is `; `. Verified by one toy case for each correction, seen failing on main's counter.
- The toy gains the edge cases listed under done line 1 (three sources, untagged last part, trailing `;`, no space, unbalanced bracket, upper-case tag, doubled `; ;`, unknown tag in the middle, `a: adopted; [b: adapted`, mismatched `[a)`, `a: adopted (v2); b: adapted`, nested brackets) with the stated expected results; single-source values and the four existing semicolon controls stay.
- The README check (C1) strips bracket and parenthesis pairs repeatedly from the inside out, counts `: <tag>` followed by `; `, `<br>` or the end, counts an untagged bullet as one source, requires at least one cell, exits non-zero naming the cell on a mismatch, and has a negative control; the hand-written fixture (C5) has five cells with hand counts; the toy never touches git history.
- follows() has one non-toy caller (adoption(), sections.py:123), so only Adoption cells move; a headline is the rounded average of the rounded row shares; sections.py stays under 19,000 bytes and the diff stays inside the listed files.
<!-- /autoplan-accepted:eng -->
## Review record

### CEO review (autoplan, SELECTIVE EXPANSION)

Mode: SELECTIVE EXPANSION (autoplan override). Rationale: a counter fix with a fixed done-line set; the mode lets the review offer in-blast-radius additions one by one while the three frozen done lines stay as written. Approved decisions at the handoff: none.

Decision ledger

| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| D-A, sections.py | Approach: fix the counter, not the README (design doc, approach B; done line 1) | one tag per bullet | per-source tag (built, dce2f7ea) | approved | the goal's frozen done lines; auto-decision P5 (explicit, one script) |
| C1, toy | Independent oracle on the real README (done line 1, reg guard) | none | count `: <tag>` tokens ending at `;`, a break or the cell end and compare with `len(follows(cell))` | approved | auto-decision P2 (in blast radius, one file already in the diff, S) |
| C5, toy | A third reference for source counts, from neither parser (native CEO voice, finding 3) | none | hand-written fixture of three README-shaped cells | approved | auto-decision P2 (one file already in the diff, S) |
| C6, sections.py | Corrections (b) and (c): a part holding a depth-0 `; ` or unbalanced delimiters makes the bullet fall back (Codex eng findings 1 and 2) | none | two small checks in follows() | approved | auto-decision P1 (in blast radius, one file, the stated fallback guarantee needs them) |
| C2, docs check | A half-tagged two-source bullet (`A: adapted; B`) falls back to one source silently | silent | a docs-check finding naming the bullet | deferred | auto-decision P3: touches pageformat.py, outside the done-line-3 file list; NOT in scope, pending write only |
| C3, README | Split two-source bullets into one source per bullet (design approach A) | rejected in design | change Follows lines | declined | the goal forbids Follows-line changes; P3 |
| C4, front pages | Show a per-source count next to each Adoption cell | none | new column text | declined | changes generated page format; outside the goal; P3 |

Premise table (receipts from this worktree at origin/main 48ac06e7d plus the branch)

| premise | claim | receipt | verdict |
|---|---|---|---|
| P1 | follows() read one tag per bullet before the fix | skills/workflow-docs/scripts/sections.py:99 (main version) | verified |
| P2 | adoption() has one caller, the row loop | sections.py:165 (`scores.append(adoption(c[2]))`); grep of skills finds no other call | verified |
| P3 | HLT-2 goes 33 to 25 percent and MCH-1 25 to 20 percent after the merge of main | git diff origin/main...HEAD -- README.md (headlines 43 to 42 and 45 to 44) | verified |
| P4 | README text is right and unchanged | the same diff changes only Adoption cells and headlines | verified |
| P5 | render --check passes on the branch | `criteria.py render --check` prints TABLES OK | verified |
| P6 | sections.py is far under the 19,000-byte cap | wc -c: 12,196 | verified |
| P7 | Nothing on main already fixes it | git log origin/main --since=2026-11-20 -- sections.py is empty | verified |

REALITY: premise-table pass seven premises, unverified=0 skills/workflow-docs/scripts/sections.py:99
REALITY: already-done pass no commit on origin/main touches sections.py since the ask 48ac06e7d
REALITY: surface-check pass only criteria.py render, render --check and docs.py check are named and exist skills/workflow-docs/scripts/criteria.py:1
REALITY: binding-decisions pass no branch decisions recorded for this goal .loop/goals/adoption-count-fix.md:1
REALITY: numbers pass 12,196 bytes [measured: skills/workflow-docs/scripts/sections.py:1], HLT-2 33 to 25 [measured: README.md:47], MCH-1 25 to 20 [measured: README.md:93]
REALITY: deferred-asks pass no linked issue; Operation TD531 and TD569 ask only for the counter fix .loop/goals/adoption-count-fix.md:1
REALITY: pr-count pass one PR for the goal; no ship policy file .loop/goals/adoption-count-fix.md:1

0A Premise challenge: the real problem is a wrong share on three front-page rows because the counter reads the wrong thing; the plan fixes the counter directly, not a proxy. Doing nothing leaves HLT-2, REG-4 and MCH-1 overstated and teaches owners to split bullets by hand to please the counter.
0B Existing code leverage: the fix reuses `TAGS`, `TAG`, `bullets()` and the existing toy; nothing is rebuilt. `bullets()` already splits at `;` for the old format (sections.py:90), and follows() now splits on the same boundary with a stricter rule.
0C Dream state

```
CURRENT STATE                    THIS PLAN                      12-MONTH IDEAL
counter reads one tag   --->     counter reads each source  ---> Adoption computed from the source list
per bullet; two-source           with its own tag; a toy        once, with a docs-check finding for any
bullets overstate                and an independent README      bullet the counter cannot read
                                 check keep it honest
```

Scope proposals (SELECTIVE EXPANSION): 6 proposed, 3 accepted (C1, C5, C6), 1 deferred (C2: NOT in scope, TODOS.md write pending, kept out of this diff because done line 3 lists the files that may change), 2 declined (C3, C4).

<!-- autoplan-baseline-edits:ceo {"sourceSha256":"14620ced7195513fd199f69df66185949be275f196107531f8c31ee919ce7b83","replacements":[{"oldText":"Checked against the code: `follows()` (sections.py:99) and `adoption()` (sections.py:121) exist; `adoption()` has one caller, the row loop at sections.py:165, and reads `follows()`. The toy is `dev/toy/test-follows-adoption.py`; the render is `skills/workflow-docs/scripts/criteria.py render`.\n","newText":"Checked against the code: `follows()` (sections.py:99) and `adoption()` (sections.py:121) exist; `adoption()` has one caller, the row loop at sections.py:165, and reads `follows()`. The toy is `dev/toy/test-follows-adoption.py`; the render is `skills/workflow-docs/scripts/criteria.py render`.\n\nThe done lines are the three frozen lines in `.loop/goals/adoption-count-fix.md`. The steps below are authoritative; the accepted-obligations block in the review record restates them.\n\nSplit rule (one rule, used everywhere below): a bullet is scanned once, splitting at `; ` only outside brackets and parentheses and only when the text since the last split is a complete `source: tag` pair; the tags are `adopted`, `adapted`, `planned` and `own`, lower case, as in `TAGS`. If any resulting part is not a complete tagged pair, the whole bullet stays one source with the tag it would have had on main (main reads a tag only at the very end of the bullet). A line break between bullets is the literal `<br>` the README tables use. A source is one `name: tag` pair; references grouped under one tag (as in DEL-1) are one source, and auditing grouped references is out of scope.\n"},{"oldText":"1. `follows()` splits a bullet at `; ` only outside brackets and parentheses, and only when the text before the split is itself a complete `source: tag` pair with a known tag; a bullet that does not split completely stays one source. Already built in commit dce2f7ea; build confirms it, it does not rewrite it.\n2. `adoption()` counts adopted sources over all sources; adapted, planned and own count 0; no sources is not measured. Docstring wording only.\n3. The toy gains the cases below, plus one independent check on this repo's own README: in every Follows cell, the number of `: <tag>` tokens that end at `;`, a line break or the end of the cell equals `len(follows(cell))` (counted outside the counter, so a missed split fails it). Accepted in the CEO review as C1 (S, one file already in the diff).\n4. `criteria.py render` rewrites the Adoption cells and headlines in README, Home and Principles after main is merged.\n5. `docs.py check --own` and `criteria.py render --check` pass; stale own pages are re-stamped.","newText":"1. `follows()` applies the split rule above. Built in commit dce2f7ea, with one small correction still to make (CEO review): a part that starts with `;` or whitespace is not a complete pair, so a doubled `; ;` falls back to one source like the other fallbacks. Apart from that this step is verification; the negative controls are run against main's counter (`git show origin/main:skills/workflow-docs/scripts/sections.py` loaded as a module) to see them fail there, and against the branch to see them pass.\n2. `adoption()` counts adopted sources over all sources; adapted, planned and own count 0; no sources is not measured; the share is rounded to a whole percent with the same Python `round()` expression main uses (ties go to the even number, unchanged). Docstring wording only: \"The share of a row's Follows sources tagged adopted (adapted, planned and own count 0); None with no sources.\"\n3. The toy already holds (built in commit dce2f7ea) the two-source case, the single-source values, four semicolon-inside-source negative controls and the unknown-tag control. Still to build: the edge cases listed under done line 1, and one independent check on this repo's own README (C1, accepted in the CEO review, S, one file already in the diff). The check, as an exact definition: a Follows cell is every table cell of a README row that starts with `- `; for each bullet (the cell split at the literal `<br>`), remove text inside brackets and parentheses with the regular expression `\\[[^\\]]*\\]|\\([^)]*\\)` (its own, not `follows()`'s depth scan), then count the matches of `: (?:adopted|adapted|planned|own)(?=; |<br>|$)` (no spaces around the tag, a whole word, lower case, and a `; ` with its space as the separator, like the split rule); a bullet with no match counts as one expected source; the cell's expected count is the sum, and it must equal `len(follows(cell))`. The toy asserts that at least one cell was found, fails with a non-zero exit on any mismatch (so a missed split fails it, and so does a half-tagged bullet such as `a: adopted; b: adapted; c`, which is the deferred C2 finding applied to this README inside the toy only), and carries a negative control: on a synthetic two-source cell a one-line copy of main's one-tag reading fails the same check while the branch's `follows()` passes. A one-off run of this definition on the current README gives 27 cells and 0 mismatches. The toy already runs as the `follows-adoption` row (land) of `.loop/regression.tsv`; that row exists and is unchanged. A hand-written fixture (C5, accepted in the CEO review as a third reference that comes from neither parser): three cells shaped like the README's HLT-2, MCH-1 and DEL-1 rows, with source counts written by hand in the toy. Home and Principles are rendered from the same Follows cells, and `render --check` proves each page equals a fresh render.\n4. `criteria.py render` rewrites the Adoption cells and headlines in README, Home and Principles on the merge of origin/main that is on the branch (48ac06e7d, v1.0.105 line). A later merge of main re-renders and the figures move with it; the figures are produced by the render, never typed.\n5. `docs.py check --own` and `criteria.py render --check` pass; stale own pages are re-stamped (stamp lines only).\n6. C2 (a docs-check finding for a half-tagged bullet) is not built and TODOS.md is not edited here, because done line 3 limits the diff. It is recorded in this plan (ledger row C2) and in the Follow-ups line of the PR body, which delivery writes from this plan; the follow-up also asks docs check to enforce one `source: tag` pair per line, which would make the heuristic unnecessary.\n7. The PR body states that the correction lowers the published Adoption figures and that this is intended (Operation ruled MCH-1's requirement text stays unchanged). Delivery re-derives the base merge and the rendered figures at ship time."},{"oldText":"Test for each done line (a negative control is seen failing before the change, on main's counter):","newText":"Test for each done line (a negative control is seen failing on main's counter):"},{"oldText":"- Done line 1: a two-source bullet (adapted; adopted) returns 50 (checked: main returns 100, one source whose text holds the whole bullet); single-source bullets (adopted, adapted, planned, own, and a four-bullet cell) return main's values; a semicolon inside `[A; B](u)`, `[A: adopted; B](u)`, a link target, or a bare `A; B` does not split; an unknown tag does not split.\n- Done line 2: after render, only the HLT-2 and MCH-1 cells and the two headlines that average them change (33 to 25 percent, 25 to 20 percent); `render --check` prints TABLES OK and `docs.py check` passes.\n- Done line 3: `git diff origin/main...HEAD --stat` lists only sections.py (12,196 bytes, under 19,000), the three front pages, the toy, this goal's records and wiki re-stamps; no requirement text, tag or Follows line differs; the private-names scan is clean.","newText":"- Done line 1: a two-source bullet (adapted; adopted) returns 50 (checked: main returns 100, one source whose text holds the whole bullet); single-source bullets (adopted, adapted, planned, own, and a four-bullet cell) return main's values; a semicolon inside `[A; B](u)`, `[A: adopted; B](u)`, a link target, or a bare `A; B` does not split; an unknown tag does not split. Edge cases with the expected result on the branch: a three-source bullet `a: adopted; b: adapted; c: planned` gives three sources and 33; `a: adopted; b: adapted; c` (last part untagged) stays one untagged source and 0; a trailing `a: adopted;` stays one untagged source; `;` with no following space does not split; an unbalanced bracket does not split; an upper-case `Adopted` is not a tag, so it does not split; a doubled `; ;` falls back to one source (after the correction in step 1) with the tag main reads at the end of the bullet. For the six fallback cases (untagged last part, trailing `;`, no space, unbalanced bracket, upper-case tag, doubled `; ;`) main gives the same result as the branch.\n- Done line 2: after render, only the HLT-2 and MCH-1 cells and the two headlines that average them change (informational, not acceptance numbers: HLT-2 cell 33 to 25 percent, MCH-1 cell 25 to 20 percent, headline of principle 2 (Sensed: enforced, verified and honest, which holds HLT-2) 43 to 42 and headline of principle 5 (Reproducible, portable and adoptable, which holds MCH-1) 45 to 44; these figures are checked at the merge of origin/main on the branch only, and the durable check is that `render --check` passes and only these two rows and their two headlines differ from main); `render --check` prints TABLES OK and `docs.py check` passes.\n- Done line 3: `git diff origin/main...HEAD --stat` lists only `skills/workflow-docs/scripts/sections.py` (12,196 bytes, under 19,000), `README.md`, `docs/wiki/Home.md`, `docs/wiki/Principles.md`, `dev/toy/test-follows-adoption.py`, `.loop/goals/adoption-count-fix.*`, the goal's own `.loop/kept/` and `.loop/lane-results/` records, and stamp-line-only changes in `docs/wiki/*.md`; no requirement text, tag or Follows line differs; the private-names scan is clean."},{"oldText":"Out of scope: any requirement text, tag or Follows line; MCH-1 stays at 20 percent (Operation's ruling); the Adoption definition itself; other generated pages.","newText":"Out of scope: any requirement text, tag or Follows line; MCH-1 is not raised from the 20 percent the corrected counter gives it (Operation's ruling: no change to its requirement text); the Adoption definition itself; other generated pages."}]} -->

<!-- autoplan-baseline-edits:eng {"sourceSha256":"8f3c82d04f9e9eb3553c456259498442db0f548a522ebb144f69d86c26af5629","replacements":[{"oldText":"Split rule (one rule, used everywhere below): a bullet is scanned once, splitting at `; ` only outside brackets and parentheses and only when the text since the last split is a complete `source: tag` pair; the tags are `adopted`, `adapted`, `planned` and `own`, lower case, as in `TAGS`. If any resulting part is not a complete tagged pair, the whole bullet stays one source with the tag it would have had on main (main reads a tag only at the very end of the bullet). A line break between bullets is the literal `<br>` the README tables use. A source is one `name: tag` pair; references grouped under one tag (as in DEL-1) are one source, and auditing grouped references is out of scope.\n","newText":"Split rule (one rule, used everywhere below): a bullet is scanned once, splitting at `; ` only outside brackets and parentheses and only when the text since the last split is a complete `source: tag` pair; the tags are `adopted`, `adapted`, `planned` and `own`, lower case, as in `TAGS`. If any resulting part is not a complete tagged pair, the whole bullet stays one source with the tag it would have had on main (main reads a tag only at the very end of the bullet). A line break between bullets is the literal `<br>` the README tables use. A source is one `name: tag` pair; references grouped under one tag (as in DEL-1) are one source, and auditing grouped references is out of scope.\n\nBuilt and pending, at a glance. Built in dce2f7ea: follows() with the split rule (before the three corrections below), adoption(), the two-source case, the single-source values, four semicolon-in-source negative controls, the unknown-tag control, the generated pages. Pending: the three corrections in step 1, the edge cases, the README check (C1), the hand-written fixture (C5), the re-render after the corrections, the docs re-stamps.\n\nA complete pair, defined once: the part ends with `: ` and one of the four tags as its last characters (text after the tag, such as `adopted (v2)`, means the part is not a pair, exactly as on main), and the separator between sources is `; ` (semicolon and a space). Brackets and parentheses must balance as typed pairs across the whole bullet.\n"},{"oldText":"1. `follows()` applies the split rule above. Built in commit dce2f7ea, with one small correction still to make (CEO review): a part that starts with `;` or whitespace is not a complete pair, so a doubled `; ;` falls back to one source like the other fallbacks. Apart from that this step is verification; the negative controls are run against main's counter (`git show origin/main:skills/workflow-docs/scripts/sections.py` loaded as a module) to see them fail there, and against the branch to see them pass.","newText":"1. `follows()` applies the split rule above. Built in commit dce2f7ea, with three small corrections still to make (CEO and Eng reviews, each with a counterexample on the branch): (a) a part that starts with `;` or whitespace is not a complete pair, so a doubled `; ;` falls back to one source; (b) in a bullet that splits, a part that still holds a `; ` outside brackets and parentheses is malformed, so the whole bullet falls back (`a: adopted; b: unknown; c: adapted` gave 50 on the branch and 0 on main; one source, 0 after the correction); (c) delimiters must balance as typed pairs across the whole bullet, so a bullet with an unmatched or mismatched bracket falls back (`a: adopted; [b: adapted` gave 50, one source and 0 after the correction). `follows()` has one caller outside the toy, `adoption()` at sections.py:123, so only the Adoption cells can move; render.py imports sections for its tables and does not read the pairs itself. Apart from that this step is verification; the negative controls are run against main's counter (`git show origin/main:skills/workflow-docs/scripts/sections.py` loaded as a module) to see them fail there, and against the branch to see them pass."},{"oldText":"3. The toy already holds (built in commit dce2f7ea) the two-source case, the single-source values, four semicolon-inside-source negative controls and the unknown-tag control. Still to build: the edge cases listed under done line 1, and one independent check on this repo's own README (C1, accepted in the CEO review, S, one file already in the diff). The check, as an exact definition: a Follows cell is every table cell of a README row that starts with `- `; for each bullet (the cell split at the literal `<br>`), remove text inside brackets and parentheses with the regular expression `\\[[^\\]]*\\]|\\([^)]*\\)` (its own, not `follows()`'s depth scan), then count the matches of `: (?:adopted|adapted|planned|own)(?=; |<br>|$)` (no spaces around the tag, a whole word, lower case, and a `; ` with its space as the separator, like the split rule); a bullet with no match counts as one expected source; the cell's expected count is the sum, and it must equal `len(follows(cell))`. The toy asserts that at least one cell was found, fails with a non-zero exit on any mismatch (so a missed split fails it, and so does a half-tagged bullet such as `a: adopted; b: adapted; c`, which is the deferred C2 finding applied to this README inside the toy only), and carries a negative control: on a synthetic two-source cell a one-line copy of main's one-tag reading fails the same check while the branch's `follows()` passes. A one-off run of this definition on the current README gives 27 cells and 0 mismatches. The toy already runs as the `follows-adoption` row (land) of `.loop/regression.tsv`; that row exists and is unchanged. A hand-written fixture (C5, accepted in the CEO review as a third reference that comes from neither parser): three cells shaped like the README's HLT-2, MCH-1 and DEL-1 rows, with source counts written by hand in the toy. Home and Principles are rendered from the same Follows cells, and `render --check` proves each page equals a fresh render.","newText":"3. The toy already holds (built in commit dce2f7ea) the two-source case, the single-source values, four semicolon-inside-source negative controls and the unknown-tag control. Still to build: the edge cases listed under done line 1, and one independent check on this repo's own README (C1, accepted in the CEO review, S, one file already in the diff). The check, as an exact definition: a Follows cell is every table cell of a README row that starts with `- `; for each bullet (the cell split at the literal `<br>`), remove text inside brackets and parentheses by repeatedly deleting innermost pairs with the regular expression `\\[[^\\[\\]]*\\]|\\([^()]*\\)` until nothing changes (its own, not `follows()`'s depth scan; this handles nested brackets and a link target with nested parentheses), then count the matches of `: (?:adopted|adapted|planned|own)(?=; |<br>|$)` (no spaces around the tag, a whole word, lower case, and a `; ` with its space as the separator, like the split rule); a bullet with no match counts as one expected source; the cell's expected count is the sum, and it must equal `len(follows(cell))`. The toy asserts that at least one cell was found, fails with a non-zero exit on any mismatch (so a missed split fails it, and so does a half-tagged bullet such as `a: adopted; b: adapted; c`, which is the deferred C2 finding applied to this README inside the toy only), and carries a negative control: on a synthetic two-source cell a one-line copy of main's one-tag reading fails the same check while the branch's `follows()` passes. A one-off run of this definition on the current README gives 27 cells and 0 mismatches. The toy already runs as the `follows-adoption` row (land) of `.loop/regression.tsv`; that row exists and is unchanged. A hand-written fixture (C5, accepted in the CEO review as a third reference that comes from neither parser): five cells with source counts written by hand in the toy: three shaped like the README's HLT-2, MCH-1 and DEL-1 rows, one with nested brackets and one half-tagged. The check detects a bullet with two or more tagged parts that the counter reads as one (for example `a: adopted; b: adapted; c` and `a: adopted (v2); b: adapted`); a single-token half-tagged bullet such as `a: adopted; b` is not flagged, and C5 is the arbiter for what the correct count is. The toy never touches git history: main's one-token reading is a one-line copy, and the `git show origin/main:...` comparison is a build-time check only. On a mismatch the toy names the cell and the expected and actual counts, and says the check strips brackets by innermost pairs. Home and Principles are rendered from the same Follows cells, and `render --check` proves each page equals a fresh render."},{"oldText":"- Done line 1: a two-source bullet (adapted; adopted) returns 50 (checked: main returns 100, one source whose text holds the whole bullet); single-source bullets (adopted, adapted, planned, own, and a four-bullet cell) return main's values; a semicolon inside `[A; B](u)`, `[A: adopted; B](u)`, a link target, or a bare `A; B` does not split; an unknown tag does not split. Edge cases with the expected result on the branch: a three-source bullet `a: adopted; b: adapted; c: planned` gives three sources and 33; `a: adopted; b: adapted; c` (last part untagged) stays one untagged source and 0; a trailing `a: adopted;` stays one untagged source; `;` with no following space does not split; an unbalanced bracket does not split; an upper-case `Adopted` is not a tag, so it does not split; a doubled `; ;` falls back to one source (after the correction in step 1) with the tag main reads at the end of the bullet. For the six fallback cases (untagged last part, trailing `;`, no space, unbalanced bracket, upper-case tag, doubled `; ;`) main gives the same result as the branch.\n- Done line 2: after render, only the HLT-2 and MCH-1 cells and the two headlines that average them change (informational, not acceptance numbers: HLT-2 cell 33 to 25 percent, MCH-1 cell 25 to 20 percent, headline of principle 2 (Sensed: enforced, verified and honest, which holds HLT-2) 43 to 42 and headline of principle 5 (Reproducible, portable and adoptable, which holds MCH-1) 45 to 44; these figures are checked at the merge of origin/main on the branch only, and the durable check is that `render --check` passes and only these two rows and their two headlines differ from main); `render --check` prints TABLES OK and `docs.py check` passes.","newText":"- Done line 1: a two-source bullet (adapted; adopted) returns 50 (checked: main returns 100, one source whose text holds the whole bullet); single-source bullets (adopted, adapted, planned, own, and a four-bullet cell) return main's values; a semicolon inside `[A; B](u)`, `[A: adopted; B](u)`, a link target, or a bare `A; B` does not split; an unknown tag does not split. Edge cases with the expected result on the branch: a three-source bullet `a: adopted; b: adapted; c: planned` gives three sources and 33; `a: adopted; b: adapted; c` (last part untagged) stays one untagged source and 0; a trailing `a: adopted;` stays one untagged source; `;` with no following space does not split; an unbalanced bracket does not split; an upper-case `Adopted` is not a tag, so it does not split; a doubled `; ;` falls back to one source (after correction (a)) with the tag main reads at the end of the bullet; `a: adopted; b: unknown; c: adapted` and an unknown or upper-case tag in the middle fall back to one source and 0 (after correction (b)); `a: adopted; [b: adapted` and a mismatched `[a)` fall back to one source and 0 (after correction (c)); `a: adopted (v2); b: adapted` stays one source and 0 because the first tag does not end its part; `a: adopted; b` stays one untagged source and 0; the nested-bracket source `[outer [inner] label: adopted; tail](u): adapted` is one source tagged adapted (hand-counted, 0). For these fallback cases main gives the same result as the branch.\n- Done line 2: after render, only the HLT-2 and MCH-1 cells and the two headlines that average them change (informational, not acceptance numbers: HLT-2 cell 33 to 25 percent, MCH-1 cell 25 to 20 percent, headline of principle 2 (Sensed: enforced, verified and honest, which holds HLT-2) 43 to 42 (a headline is the rounded average of the rounded row shares, as `tables()` computes it) and headline of principle 5 (Reproducible, portable and adoptable, which holds MCH-1) 45 to 44; these figures are checked at the merge of origin/main on the branch only, and the durable check is that `render --check` passes and only these two rows and their two headlines differ from main); `render --check` prints TABLES OK and `docs.py check` passes."}]} -->

<!-- autoplan-accepted:ceo -->
- follows() applies the split rule stated in the plan: split at `; ` only outside brackets and parentheses and only after a complete `source: tag` pair (tags adopted, adapted, planned, own, lower case); if any part is not a complete tagged pair the whole bullet stays one source. Verified by the two-source toy case returning 50, the edge cases listed under done line 1, and negative controls for a semicolon inside a link, a source name, a link target and an unknown tag.
- adoption() counts adopted sources over all sources; adapted, planned and own count 0; no sources is not measured. Single-source cells keep main's values (toy).
- criteria.py render rewrites only Adoption cells and headlines in README, Home and Principles; after the merge only HLT-2 and MCH-1 cells and their two headlines change; `render --check` prints TABLES OK and `docs.py check` passes.
- The toy compares, for every Follows cell of this repo's README, the count of `: <tag>` tokens (the same four tags, text inside brackets and parentheses removed first) ending at `;`, a line break or the end of the cell with `len(follows(cell))`, counted outside follows() as defined in step 3 (an untagged bullet counts as one source, a half-tagged bullet fails it), a mismatch failing the toy, with at least one cell required (C1).
- follows() also treats a part that starts with `;` or whitespace as not a complete pair (a doubled `; ;` falls back to one source); a source is one `name: tag` pair; the toy carries a hand-written fixture of three README-shaped cells with hand-counted source counts (C5).
- Diff limits: sections.py under 19,000 bytes, no requirement text, tag or Follows line changes, private scan clean, only the listed files change.
<!-- /autoplan-accepted:ceo -->

0H document approval (auto-decided, recommended option A): the working plan and the CEO scope summary are approved as documents. Spec review ran three times (6/10, 7/10, 7/10, the cap); issues verified: 9 of 9 against the plan text (applied edits, not a reviewer verdict); spec not re-verified by a reviewer after the last fixes. Unresolved amendments: none.

Effort estimate (human team vs. agent)
- Hour 1 (foundations): the implementer needs the split rule and the exact oracle definition; both are in the plan. Effort: S / S.
- Hour 2-3 (core logic): follows() and adoption() are built (commit dce2f7ea); the only ambiguity left is the doubled `; ;` case, documented with its expected result. Effort: S / S.
- Hour 4-5 (integration): the toy additions (edge cases, oracle, negative control) and the re-render. A merge of main moves the rendered figures; they are produced by the render, never typed. Effort: M / S.
- Hour 6+ (polish and tests): re-stamp stale own pages (stamp lines only), private scan, size check. Effort: S / S.

Decision Audit Trail

<!-- AUTONOMOUS DECISION LOG -->
## Decision Audit Trail

| # | Phase | Decision | Classification | Principle | Rationale | Rejected |
|---|-------|----------|----------------|-----------|-----------|----------|
| 1 | CEO | Mode SELECTIVE EXPANSION | Mechanical | autoplan override | fixed by the pipeline | other modes |
| 2 | CEO | Accept C1 (independent README oracle in the toy) | Mechanical | P2 | in blast radius, one file already in the diff, catches a missed split on real data | none |
| 3 | CEO | Defer C2 (docs-check finding for a half-tagged bullet) | Taste | P3 | outside the done-line-3 file list; better as its own goal | add now (3 files) |
| 4 | CEO | Decline C3 (split README bullets) | Mechanical | P4, goal | the goal forbids Follows changes; counter fix is the cause | split bullets |
| 5 | CEO | Decline C4 (per-source column) | Mechanical | P3 | generated page format change outside the goal | add column |
| 6 | CEO | Spec review 1: state one split rule, tags, oracle bracket handling, edge cases, per-cell figures, file list, C2 record in the PR body | Mechanical | P1, P5 | each fix removes an ambiguity without changing a done line | leave implicit |
| 7 | CEO | Spec review 2: line break named, rounding unchanged, oracle failure and runner row, doubled semicolon documented, headline-to-row map, figures pinned to one merge | Mechanical | P1, P5 | wording and evidence only; no done line changes | leave implicit |
| 8 | CEO | Spec review 3 (cap reached, no fourth review): exact oracle definition incl. untagged bullet, non-empty guard, oracle negative control, built/to-build marked, C2 record, regression row unchanged, figures informational; issues verified 9 of 9 against the plan text; spec not re-verified by a reviewer | Mechanical | P1, P5 | the oracle would have disagreed with follows() on untagged or no-space bullets | leave it |
| 9 | CEO | Native voice: fix doubled `; ;` (a part starting with `;` or whitespace is not a complete pair) | Mechanical | P1 | the two-source answer for `; ;` was an accident of the regex; one source matches main and the other fallbacks | keep two sources |
| 10 | CEO | Native voice: accept C5, a hand-written fixture of three README-shaped cells | Mechanical | P2 | gives a reference independent of both parsers; one file already in the diff | none |
| 11 | CEO | Both voices: C2 durable record stays in the plan and the PR body Follow-ups; no TODOS row or issue is created here | Taste | P3 | a TODOS row needs done line 3 changed (a new goal); an issue is an outward action the plan step does not take; Operation can file either from the Follow-ups line | add the TODOS row now |
| 12 | CEO | Codex finding 1: define a source as one `name: tag` pair; grouped references count once; no audit of grouped references | Taste | P3 | the done lines define the fix as per-source tags; DEL-1's grouped references are README content, which the goal forbids changing | count each reference |
| 13 | CEO | Codex finding 2 (the Adoption metric rewards citations): not in scope | Taste | P3 | the definition is frozen by Operation's ruling; a metric review is its own goal | change the metric |
| 14 | CEO | Native voice 5 and 6: PR body says the figures drop on purpose; delivery re-derives merge and figures at ship time | Mechanical | P1 | removes the risk that the drop reads as a regression and that pinned SHAs go stale | leave implicit |
| 15 | Eng | Codex eng 1 and 2: corrections (b) and (c) in follows() so the whole-bullet fallback holds for an embedded unknown tag and unbalanced delimiters | Mechanical | P1, P5 | both reproduce on the branch (50 against main's 0); the plan's own fallback guarantee needs them | leave the permissive matcher |
| 16 | Eng | Codex eng 3: oracle strips innermost pairs repeatedly; states what it detects; C5 gains nested and half-tagged hand-counted cells | Mechanical | P1 | the non-nesting strip falsely failed valid nested text | keep the one-pass regex |
| 17 | Eng | Native eng 1: define a complete pair (tag last, `; ` separator); add `a: adopted (v2); b: adapted` | Mechanical | P5 | removes the unspecified boundary between the two counters | leave implicit |
| 18 | Eng | Native eng 2 and 7: callers listed (one non-toy caller; render.py imports sections only); headline is the rounded average of rounded rows | Mechanical | P1 | answers the unchecked-callers risk with evidence | skip the grep |
| 19 | Eng | Native eng 3, 4, 5, 6: C5 arbiter stated; toy never touches git history; failure message names cell and counts; C2 follow-up stays in the PR body (an issue is an outward action not taken here) | Taste | P3 | low severity; durable C2 record already a taste decision (row 11) | create an issue now |
| 20 | Eng | TODOS.md: not written, although the eng phase would auto-write deferred scope | Taste | P3 | done line 3 limits the diff to listed files; TODOS.md is not listed | write the row |

### CEO dual voices (native CEO subagent: approve with 2 high, 4 medium; Codex plan-review model: FINDINGS P1, 2 high, 1 medium)

```
CEO DUAL VOICES - CONSENSUS TABLE:
  Dimension                             Claude                       Codex                          Consensus
  1. Premises valid?                    yes; "untagged = 0" assumed  source never defined (DEL-1)   DISAGREE -> taste, row 12 (define a source)
  2. Right problem to solve?            yes, right size              metric may reward citations    DISAGREE -> taste, row 13 (not in scope)
  3. Scope calibration correct?         right; C2 too thin a record  validation deferred too long   CONFIRMED: narrow scope; C2 record flagged by both, row 11
  4. Alternatives sufficiently explored? format change had no cost analysis  grouped counting not weighed  CONFIRMED gap: follow-up asks docs check for one source per line
  5. Competitive/market risks covered?  none (internal tooling)      none                           CONFIRMED: N/A
  6. 6-month trajectory sound?          silent 0 on half-tagged      unsupported score published    CONFIRMED: C2 follow-up, row 11
```

Cross-model tension: the two voices agree on the thin C2 record and on the unsupported-score risk. They differ on the metric itself (Codex questions the incentive; Claude accepts the frozen definition). Both are taste decisions in the audit trail and need no owner decision, because the done lines and Operation's ruling fix the definition.

Outside voice coverage: Claude native CEO subagent completed; Codex (gpt-6-astra, role plan-review) completed, OUTSIDE_STATUS completed.

### CEO review sections (SELECTIVE EXPANSION)

Current scope: mode SELECTIVE EXPANSION; accepted C1 and C5 (toy additions) and the correction of the doubled `; ;` case; deferred C2 (PR body Follow-ups); declined C3 and C4; Codex findings 1 to 3 and native findings 1 to 6 dispositioned in rows 9 to 14.

Section 1, Architecture: one script (sections.py: follows() then adoption(), one caller in tables()), one toy, three generated pages. No new component, coupling or state. Data flow: README Follows cell -> follows() -> (source, tag) pairs -> adoption() -> share -> tables() cell and headline -> render.

```
README Follows cell --> follows() --split rule--> [(source, tag)...] --> adoption() --> tables(): row cell + headline
        |                    |  nil/empty: [] -> None ("not measured")                 |
        |                    |  malformed bullet: one source, main's tag                v
        +-- toy oracle (own regex, outside follows()) must agree          criteria.py render -> README, Home, Principles
```

Single points of failure: the split rule as a heuristic over prose (finding 2, accepted as a heuristic for this PR; the follow-up asks docs check to enforce one pair per line). Rollback: revert the PR; the pages regenerate. Value test: the toy oracle and fixture are consumed by the regression row follows-adoption (land), and they retire when docs check enforces one pair per line.

Section 2, Error and rescue map: follows() raises nothing; malformed input degrades to one source (rescued, tested). adoption() with no sources returns None, rendered "not measured". A mixed-tag bullet with an unknown tag (`A: unknown; B: adopted`) reads as one source at 100 (same as main; Codex finding 3) and is recorded under C2.

Section 3, Security: no input from outside the repo; a README is read, never executed; regexes are linear (no nested quantifiers). No issues found.

Section 4, Data flow and edge cases: nil (empty cell), empty (no bullets), wrong type (bullet without a tag), unbalanced brackets, no space after `;`, upper-case tag, trailing `;`, doubled `; ;`: each has a stated expected result in the plan.

Section 5, Code quality: about 20 lines, one loop, bracket depth counter; the doubled-semicolon correction adds one lookahead to the pair regex; no method branches more than 5 times beyond the existing loop. No issues found beyond finding 4.

Section 6, Tests: new behaviors are covered by the toy (two-source case, single-source values, six fallback cases, four negative controls), the README oracle with a non-empty guard and a negative control, and the hand-written fixture. Test pyramid: unit only, which is right for a pure function. Flakiness: none (no time, network or ordering).

Section 7, Performance: the README is under 30 KB and the regexes are linear. No issues found.

Section 8, Observability: the failure surfaces are the toy (non-zero exit), `render --check` and `docs.py check`, all loud. Gap: a half-tagged bullet is silent in production docs checks (C2).

Section 9, Deployment: generated pages and one script; ships with the PR; rollback is a revert plus a re-render. No migration.

Section 10, Long-term trajectory: reversibility 5/5. Debt: the heuristic parser (C2 follow-up removes it). The 1-year question: a new engineer finds the split rule stated once in the docstring and the plan. Retrospective on cherry-picks: C1 and C5 were right; C2 is the one the voices wanted more durable.

Section 11, Design and UX: SKIPPED (no UI scope).

NOT in scope
- Deferred: C2 (a docs-check finding for a half-tagged or unknown-tag bullet, and enforcing one source per line); recorded in this plan and the PR body Follow-ups line.
- Rejected: C3 (splitting README bullets: Follows lines may not change), C4 (per-source count column), counting each grouped reference separately (README content), changing the Adoption metric (Operation's ruling).

What already exists
- `TAGS`, `TAG`, `bullets()` and the existing toy in sections.py and dev/toy/test-follows-adoption.py are reused; `criteria.py render` and `render --check` already regenerate and verify the pages; the regression row follows-adoption (land) already runs the toy.

Dream state delta: after this plan the counter reads each source correctly and a toy keeps it honest; the 12-month ideal (one `source: tag` pair per line enforced by docs check) is one follow-up away.

Error and Rescue Registry (capability rows)

| Capability | What can go wrong | Rescued? | Action | User sees |
|---|---|---|---|---|
| follows() | bullet is not a clean list of tagged pairs | yes | one source, main's tag | a lower or untagged share (silent; C2) |
| follows() | unknown tag in a two-source bullet | yes, as main | one source tagged by the last tag | an overstated share (silent; C2, Codex 3) |
| adoption() | no sources | yes | None | "not measured" |
| render | page differs from a fresh render | n/a | `render --check` fails | TABLES not OK |
| toy oracle | counter and oracle disagree | n/a | toy exits non-zero | a red row |

Failure Modes Registry

```
CODEPATH            | FAILURE MODE                   | RESCUED? | TEST? | USER SEES?        | LOGGED?
--------------------|--------------------------------|----------|-------|-------------------|--------
follows()           | half-tagged bullet             | Y        | Y     | silent (WARNING)  | toy edge case
follows()           | unknown tag beside a tagged one| Y        | Y     | silent (WARNING)  | toy negative control
follows()           | semicolon inside link or name  | Y        | Y     | correct count     | toy
adoption()          | no sources                     | Y        | Y     | "not measured"    | toy
oracle              | README edited later            | n/a      | Y     | toy fails (loud)  | regression row
render              | unrelated cells reordered      | n/a      | Y     | render --check    | docs check
```

No row has RESCUED=N and TEST=N and a silent result, so there are 0 CRITICAL GAPS; two silent WARNING rows are the C2 deferral.

Diagrams produced: system data flow (above); error flow (registry); deployment and rollback below. A state machine does not apply (no stateful object).

```
DEPLOY:  merge PR -> pages already re-rendered in the PR -> release step re-renders from merged tree
ROLLBACK: revert PR -> criteria.py render -> render --check prints TABLES OK
```

Stale diagram audit: no ASCII diagram exists in the files this plan touches (sections.py, the toy); none found stale.

REALITY: premise-table pass seven premises, unverified=0 skills/workflow-docs/scripts/sections.py:99
REALITY: already-done pass no commit on origin/main touches sections.py since the ask 48ac06e7d
REALITY: surface-check pass only criteria.py render, render --check and docs.py check are named and exist skills/workflow-docs/scripts/criteria.py:1
REALITY: binding-decisions pass no branch decisions recorded for this goal .loop/goals/adoption-count-fix.md:1
REALITY: numbers pass 12,196 bytes [measured: skills/workflow-docs/scripts/sections.py:1], HLT-2 33 to 25 [measured: README.md:47], MCH-1 25 to 20 [measured: README.md:93]
REALITY: deferred-asks pass no linked issue; Operation TD531 and TD569 ask only for the counter fix .loop/goals/adoption-count-fix.md:1
REALITY: pr-count pass one PR for the goal; no ship policy file .loop/goals/adoption-count-fix.md:1

Completion Summary

```
+====================================================================+
|            MEGA PLAN REVIEW - COMPLETION SUMMARY                   |
+====================================================================+
| Mode selected        | SELECTIVE EXPANSION                         |
| System Audit         | one script, one toy, three generated pages  |
| Step 0               | SELECTIVE EXPANSION; C1, C5 accepted        |
| Section 1  (Arch)    | 1 issue found (heuristic parser)            |
| Section 2  (Errors)  | 5 error paths mapped, 0 GAPS, 2 WARNINGS    |
| Section 3  (Security)| 0 issues found, 0 High severity             |
| Section 4  (Data/UX) | 8 edge cases mapped, 0 unhandled            |
| Section 5  (Quality) | 1 issue found (doubled semicolon, fixed)    |
| Section 6  (Tests)   | Diagram produced, 0 gaps                    |
| Section 7  (Perf)    | 0 issues found                              |
| Section 8  (Observ)  | 1 gap found (silent half-tagged, C2)        |
| Section 9  (Deploy)  | 0 risks flagged                             |
| Section 10 (Future)  | Reversibility: 5/5, debt items: 1           |
| Section 11 (Design)  | SKIPPED (no UI scope)                       |
+--------------------------------------------------------------------+
| NOT in scope         | written (5 items)                           |
| What already exists  | written                                     |
| Dream state delta    | written                                     |
| Error/rescue registry| 5 rows, 0 CRITICAL GAPS                     |
| Failure modes        | 6 total, 0 CRITICAL GAPS                    |
| TODOS.md updates     | 0 items written (C2 recorded in the PR body)|
| Scope proposals      | 5 proposed, 2 accepted (EXP + SEL)          |
| CEO plan             | written                                     |
| Outside voice        | codex completed; native CEO subagent completed |
| Lake Score           | N/A (no scored coverage choices asked)      |
| Diagrams produced    | 3 (data flow, error flow, deploy/rollback)  |
| Stale diagrams found | 0                                           |
| Unresolved decisions | 0                                           |
| Reality rows         | 7/7 rows (PLAN_REALITY), 0 unverified       |
+====================================================================+
```

### Design review and DX review

Phase 2 (Design Review): skipped, no UI scope detected (scope check: uiRequired false; matches were the words "row" and "list", with no rendered file or visual noun). This is a skip, not a completed review.
Phase 2.5 (DX Review): skipped, no developer-facing scope detected (dxRequired false; developer-tool and agent-primary flags not set). This is a skip, not a completed review.

### Eng review (autoplan)

Eng dual voices: native eng subagent completed (2 medium, 5 low, 1 note); Codex plan-review model completed (3 medium, VERDICT FINDINGS, P2).

```
ENG DUAL VOICES - CONSENSUS TABLE:
  Dimension                           Claude                         Codex                          Consensus
  1. Architecture sound?              yes, small, one owner of state  yes; permissive pair matcher  CONFIRMED sound; matcher tightened by corrections (a) to (c)
  2. Test coverage sufficient?        oracle not independent          oracle misses nested text      CONFIRMED gap: C5 arbiter, nested fixture, innermost stripping
  3. Perf risks + budget/bench named? none; regexes bounded           none                           CONFIRMED: N/A, README under 30 KB, one scan per bullet
  4. Security threats covered?        no new surface                  no new surface                 CONFIRMED: none
  5. Error paths handled?             silent doubled-space fallback   embedded unknown tag, brackets CONFIRMED: corrections (b), (c); silent fallback is C2
  6. Deployment risk manageable?      yes                             yes                            CONFIRMED: revert plus re-render
```

CODEX SAYS (eng, architecture challenge): three Medium findings, all reproduced read-only. 1. `a: adopted; b: unknown; c: adapted` returns 50 on the branch against main's 0 because the permissive pair matcher accepts `b: unknown; c` as a source name. 2. `a: adopted; [b: adapted` returns 50: delimiter balance is not checked across the whole bullet and `[a)` balances the shared depth counter. 3. The oracle's one-pass regex rejects valid nested text and does not flag `a: adopted; b`; C5's three fixtures do not cover it. VERDICT: FINDINGS.

CLAUDE SUBAGENT (eng, independent review): 1 (medium) the boundary of a complete pair is not defined (`a: adopted (v2); b: adapted`); 2 (medium) other callers of follows() were not listed; 3 to 7 (low) the oracle's partial independence, bracket-regex brittleness on nested URLs, the silent doubled-space fallback, toy hermeticity and stale figures.

Step 0 Scope Challenge (read the code): scope accepted as-is. Counts: 2 hand-edited files (sections.py, one toy) plus generated pages and records, 0 new classes or services, so the complexity gate (8 files or 2 classes) is not reached and no selector question is asked. What already solves each sub-problem: TAGS, TAG and bullets() in sections.py; criteria.py render and render --check; the follows-adoption row. Search check: no new architectural pattern, infrastructure or concurrency approach, so no research was needed [Layer 1: reuse the existing regex and loop]. TODOS cross-reference: TODOS.md was not changed (done line 3); deferred scope sits in the plan's NOT in scope.

REALITY: premise-table pass nine premises, unverified=0 skills/workflow-docs/scripts/sections.py:123
REALITY: already-done pass no commit on origin/main touches sections.py since the ask 48ac06e7d
REALITY: surface-check pass criteria.py render, render --check and docs.py check exist and ran skills/workflow-docs/scripts/criteria.py:1
REALITY: binding-decisions pass no branch decisions recorded for this goal .loop/goals/adoption-count-fix.md:1
REALITY: numbers pass 12,196 bytes [measured: skills/workflow-docs/scripts/sections.py:1], 27 README cells with 0 mismatches [measured: README.md:47]
REALITY: deferred-asks pass no linked issue; Operation TD531 and TD569 ask only for the counter fix .loop/goals/adoption-count-fix.md:1
REALITY: pr-count pass one PR for the goal; no ship policy file .loop/goals/adoption-count-fix.md:1

Section 1, Architecture. Dependency graph (nothing new; two shapes compared because no new module or boundary is introduced, so design-twice does not apply):

```
dev/toy/test-follows-adoption.py --imports--> skills/workflow-docs/scripts/sections.py
sections.tables() --calls--> adoption() --calls--> follows()      (only caller of follows(): sections.py:123)
skills/workflow-docs/scripts/render.py --imports--> sections      (tables(), no direct follows())
criteria.py render --writes--> README.md, docs/wiki/Home.md, docs/wiki/Principles.md
```

[INFORMATIONAL] (confidence: 9/10) sections.py:102 `pair = re.compile(r"(.+): (%s)$" % TAGS)` - the permissive source group lets an embedded malformed pair pass as a source name; corrections (b) and (c) close it. No coupling, scaling or security concern. Distribution: no new artifact. Dispositions: accepted (C6, audit row 15).

Section 2, Code quality: follows() stays one function with a bracket depth scan; correction (c) replaces the shared counter by a typed stack; no duplication with `bullets()` beyond the same `; ` boundary, which was already shared; accepted. Diagram accuracy: no ASCII diagram in the touched files. [INFORMATIONAL] (confidence: 8/10) sections.py:106-117 depth counter does not distinguish `[` from `(`. Dispositions: accepted (row 15).

Section 3, Test review. Framework detected: python toys under dev/toy run by the regression table (row follows-adoption, land); CLAUDE.md has no Testing section.

```
CODE PATHS                                              USER FLOWS
[+] skills/workflow-docs/scripts/sections.py            [+] owner reads the front-page Adoption cell
  |-- follows()                                           |-- [TESTED ***] two-source bullet = 50
  |   |-- split at depth-0 "; " after a pair              |-- [TESTED ***] single-source values = main
  |   |   [GAP -> add] three-source bullet                 |-- [GAP -> add] hand-counted fixtures (C5)
  |   |-- fallback: untagged / trailing ; / no space      [+] docs check and render --check
  |   |   [GAP -> add] each fallback case                   |-- [TESTED **] render --check on the branch
  |   |-- corrections (a) leading ; (b) depth-0 ; in part  [+] README grows a new Follows bullet
  |   |   (c) typed delimiter balance                       |-- [GAP -> add] README oracle with negative control
  |   |   [GAP -> add] one case each, seen failing on main
  |   `-- semicolon inside link / name / target: [TESTED ***] four controls
  `-- adoption(): [TESTED **] share and None; [GAP -> add] rounding ties unchanged (state only)

COVERAGE: 6/12 paths tested (50%) | Code paths: 3/7 | User flows: 3/5
QUALITY: *** 4, ** 2 | GAPS: 6 (0 E2E, 0 eval), all with Value cards in the test plan
```

Section 4, Performance: README under 30 KB, one scan per bullet, innermost-pair stripping is bounded by bracket depth; no per-request path, memory or cache concern. The independent check loops over 27 cells. No issues found.

NOT in scope: C2 and the one-pair-per-line docs-check rule (follow-up in the PR body); C3, C4; auditing grouped references; the Adoption metric; the Follows format; TODOS.md edits (done line 3).

What already exists: `TAGS`, `bullets()`, the existing toy cases, `criteria.py render` and `render --check`, the regression row follows-adoption.

Failure modes

```
CODEPATH           | FAILURE MODE                         | RESCUED? | TEST?        | USER SEES?       | LOGGED?
-------------------|--------------------------------------|----------|--------------|------------------|--------
follows()          | embedded unknown tag (b)             | Y (after fix) | Y (add) | correct fallback | toy
follows()          | unbalanced or mismatched delimiter(c)| Y (after fix) | Y (add) | correct fallback | toy
follows()          | doubled "; ;" (a)                    | Y (after fix) | Y (add) | correct fallback | toy
follows()          | half-tagged bullet                   | Y        | Y (oracle, 2+ tokens) | silent (WARNING; C2) | toy
oracle             | nested text read as extra token      | Y (innermost strip) | Y (C5) | toy stays green | toy
render             | unrelated cells reordered            | n/a      | Y            | render --check   | docs check
```

0 critical gaps (no row has no test, no handling and a silent result).

Worktree parallelization strategy: sequential implementation, no parallelization opportunity (one script, one toy, then a render that depends on both).

Diagrams: dependency graph (above), coverage diagram (above), data flow and deploy/rollback (CEO section).

<!-- autoplan-accepted:eng -->
- follows() keeps the split rule and adds three corrections: (a) a part that starts with `;` or whitespace is not a complete pair; (b) in a bullet that splits, a part that still holds a `; ` outside brackets and parentheses makes the whole bullet fall back to one source with the tag main reads at the end; (c) brackets and parentheses must balance as typed pairs across the whole bullet, else the bullet falls back. A complete pair ends with `: ` and one of the four lower-case tags as its last characters; the separator is `; `. Verified by one toy case for each correction, seen failing on main's counter.
- The toy gains the edge cases listed under done line 1 (three sources, untagged last part, trailing `;`, no space, unbalanced bracket, upper-case tag, doubled `; ;`, unknown tag in the middle, `a: adopted; [b: adapted`, mismatched `[a)`, `a: adopted (v2); b: adapted`, nested brackets) with the stated expected results; single-source values and the four existing semicolon controls stay.
- The README check (C1) strips bracket and parenthesis pairs repeatedly from the inside out, counts `: <tag>` followed by `; `, `<br>` or the end, counts an untagged bullet as one source, requires at least one cell, exits non-zero naming the cell on a mismatch, and has a negative control; the hand-written fixture (C5) has five cells with hand counts; the toy never touches git history.
- follows() has one non-toy caller (adoption(), sections.py:123), so only Adoption cells move; a headline is the rounded average of the rounded row shares; sections.py stays under 19,000 bytes and the diff stays inside the listed files.
<!-- /autoplan-accepted:eng -->

Eng Completion Summary

```
- Step 0: Scope Challenge - scope accepted as-is
- Reality rows: 7/7 applicable rows emitted (PLAN_REALITY), 0 unverified premises
- Architecture Review: 1 issue found
- Code Quality Review: 1 issue found
- Test Review: diagram produced, 6 gaps identified
- Performance Review: 0 issues found
- NOT in scope: written
- What already exists: written
- TODOS.md updates: 0 items proposed (not written: done line 3)
- Failure modes: 0 critical gaps flagged
- Unresolved decisions: 0 in this review
- Outside voice: codex completed (gpt-6-astra); native eng subagent completed
- Parallelization: 1 lane, 0 parallel / 1 sequential
- Lake Score: N/A (no scored coverage choices asked)
```

Implementation Tasks

- [ ] **T1 (P1, human: ~1h / CC: ~10min)** - sections.py - correct follows(): (a) leading `;` or whitespace, (b) depth-0 `; ` inside a part, (c) typed delimiter balance
  - Surfaced by: Section 1 and Codex eng findings 1 and 2 (sections.py:102, :106-117)
  - Files: skills/workflow-docs/scripts/sections.py
  - Verify: `python3 dev/toy/test-follows-adoption.py` prints ALL PASS; each new case fails on main's counter
- [ ] **T2 (P1, human: ~2h / CC: ~15min)** - dev/toy/test-follows-adoption.py - add the edge cases, the README check with its negative control and the five-cell hand-counted fixture
  - Surfaced by: Section 3 test gaps; native eng 1, 3, 6; Codex eng 3
  - Files: dev/toy/test-follows-adoption.py
  - Verify: the toy prints ALL PASS and the README check reports 27 cells, 0 mismatches
- [ ] **T3 (P2, human: ~30min / CC: ~5min)** - README.md, docs/wiki/Home.md, docs/wiki/Principles.md - re-render and re-stamp
  - Surfaced by: done line 2; native eng 7
  - Files: README.md, docs/wiki/Home.md, docs/wiki/Principles.md, stamp lines in docs/wiki/*.md
  - Verify: `criteria.py render --check` prints TABLES OK; `docs.py check --own` passes; only HLT-2 and MCH-1 differ from main

### Build notes

- Correction (b) was narrowed while building. As worded in the plan ("a part that still holds a `; ` outside brackets is malformed") it broke the kept control `A; B` and split one real README bullet wrongly (`[Temporal durable execution](...): adapted; macOS launchd; Claude Code cloud sessions: adopted` must stay two sources; MCH-1 25 to 20 depends on it). The README check (C1) caught it. Built rule: a `; ` outside brackets marks the bullet malformed only when the text before it ends in `: <word>` (a `name: word` with a wrong tag), as in `a: adopted; b: unknown; c: adapted`. Counterexamples on dce2f7ea before the corrections: `a: adopted; b: unknown; c: adapted` gave 50 and `a: adopted; [b: adapted` gave 50; both give one source and 0 now, the same as main.
- Corrections (a) and (c) are built as planned. sections.py is 12,676 bytes. The toy prints ALL PASS: 13 edge cases, the README check (27 cells, 0 mismatches) with two negative controls, and five hand-counted cells.
