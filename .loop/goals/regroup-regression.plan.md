# regroup-regression: plan

Claims checked against the repo: `skills/workflow-docs/scripts/milestones.py` holds `revise`, `retire`, `migrate` and `guard`
(criteria.py loads them); `record()` there accepts o155 because it names regroup-regression and the four pages; the pages
Regression, Automation and Documentation carry a Revisions section; `docs/wiki/Documentation.md` already has DOC-20 and DOC-22;
`.loop/regression.tsv` has 4 rows on DOC-7, 43 on DOC-17 and 3 on AUT-8; Release.md has no REL-13 yet.

## Build steps
1. Script outside the repo (scratchpad) reads the four draft tables. For each ID: live and changed -> `criteria.py revise`
   with `--text` (one line; the draft's bold title stays); live and equal -> skipped; absent -> added as an Unreviewed line
   in the right group (Functional or Non-functional by the draft's neighbour) and `criteria.py migrate --page P` gives it r1.
2. Retires: `retire AUT-8 --as moved:DOC-16`, `retire DOC-7 --as merged:DOC-1`, `retire DOC-17 --as moved:INT-3`.
   Order: Integrations page first so INT-3 is live, then DOC-17.
3. New page `docs/wiki/Integrations.md` (Problem, Requirements INT-1..8, Non-goals, Success metrics, Revisions, Tests) and
   `docs/wiki/How-to-use-Integrations.md`, in the repo's page format; a Home row through the render tooling.
4. Re-point `.loop/regression.tsv` rows: DOC-7 -> DOC-1, DOC-17 -> INT-3, AUT-8 -> DOC-16 (goal column only). Update the
   How-to items of the four pages so each functional requirement has an item and no item names an unknown ID.
5. `criteria.py render` re-renders the Tests tables and Tests.md; `docs.py check`, `entry.py check`, `wiki.py prepare`,
   `criteria.py guard 210cc556 regroup-regression` (the base of this branch; against main it also lists prd-revisions' own
   changes, because this branch is stacked on prd-revisions and is mergeable only after it).

## Test per done line
- a: `criteria.py guard 210cc556 regroup-regression` prints GUARD OK; a count script asserts every draft ID is live (or retired with its mover) and
  each revised ID has an r2 row. Before the change the same assertion fails (IDs absent), after it passes.
- b: `docs.py check` DOCS OK with the old IDs resolving as Retired markers; a grep finds no regression row, How-to item or
  issue link on the four pages that names DOC-7, DOC-17 or AUT-8 as live.
- c: render leaves the row count unchanged (net zero); no script changes, so no new check rule, so no new row to prove;
  `wiki.py prepare` clean and `entry.py check` prints ENTRY OK.
- d: `git diff --stat origin/main` lists only the four pages' files, their How-to pages, Home, Tests, the goal files and
  regression.tsv; no script and no added shipped file.

## What could break
- A new page may need a docs.tsv row (outside the declared touches): ask the operation session for `goal.py touches` if so.
- Draft text with a URL, `owner/repo#N` or a machine path trips the stand-alone check: reword to the draft's meaning.
- Each page stays at or under 19 requirements: Regression 16, Automation 9 live, Documentation 19 with DOC-23 left to prd-principles.

## Out of scope
DOC-15, DOC-18, DOC-23, GRD-11, GRD-13, the other eight features, copying cut detail to How-to, REL-13 links (not live), new tests for rules this goal does not add.

## Full-depth review (independent reviewer read the plan and the diff)
- Finding 1 (guard against main refuses DOC-1, DOC-8, DOC-9): those are prd-revisions' own owner-recorded changes, present because this
  branch sits on prd-revisions. Resolved by guarding against the branch base, and by merging after prd-revisions. Operation is told.
- Finding 2 and 3 (stray DOC-17, DOC-7 citations on Home, Documentation non-goals, a How-to example): fixed to INT-3, INT-8, DOC-9.
  One test row's scenario text still names DOC-17; it guards INT-3 and its toy test passes, so it is left as written.
- Finding 4 (done line c, "each new rule has a row seen failing and passing"): this goal adds no check rule and no script, so no
  new row is owed. New requirements (REG-11..16, AUT-10, DOC-21, INT-1,2,4..8) have no row yet, which the draft itself lists as
  "write tests" or "assign when the source is split"; they show not enforced. Zero rows are added net (1278 before and after).
- Checked and fine: all 52 draft IDs present with draft text, 50 rows re-pointed by goal column only, docs check DOCS OK.

VERDICT: independent reviewer: 4 findings, 3 fixed, 1 recorded as an interpretation of done line c
VERDICT: self: plan covers each frozen done line
PENDING: none
DEPTH: full
STEP: done
