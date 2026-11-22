# Plan: v110-fast-text-2 (DRAFT, not yet gated)

Base (TD1016): planned against the renumber's head bb7a38bc8 (loop/v110-fast-renumber), whose changes are fixed; the build lands on top of it, and main is merged up again after it lands, before the lane.

Source: the owner's final page frozen-source-final-1742 (sha256 c952ee382c4153f8, checked against the HTML). Done lines are frozen in `.loop/goals/v110-fast-text-2.md`. Base: main 65e242e28 (features format from #5793, marks cleared) merged in at 02e6df764.

## What the renumber goal does (v110-fast-renumber, built at bb7a38bc8) and this goal leaves to it

This goal does not touch any of these; it merges after the renumber and builds on it:

- The principles list in `skills/workflow-health/references/commands.md` (3 Fast, 4 Cheap, 5 Small; old 4, 5, 6 become 6, 7, 8) and the headings `## 3. Fast`, `## 4. Cheap`, `## 5. Small`, `## 6.` to `## 8.` on README, Home and the Principles page.
- The figure renames (`principle-03-fast.svg`, `principle-04-cheap.svg`, `principle-05-small.svg`) and the regenerated system-design figures.
- Moving DEL-17's Tokens line, word for word, into DEL-28 under 4 Cheap, under o756, with marks o791 (DEL-17) and o792 (DEL-28); GRD-8 and GRD-15 re-pointed to DEL-28, GRD-7 kept on DEL-17 under o757; GRD-8 and GRD-15 pointers; GRD-20 under 5 Small; OPS-16 under 7 Reproducible.
- The old-number sweep of toys and how-to pages, and the sentence lines (kept as on main, "no principle sentence is changed").

## What this goal does (after the renumber merges and main is merged up again)

1. Principle sentences: write the page's sentences for 3 Fast, 4 Cheap and 5 Small (the page text, lines 84 to 86 of the pinned page) into README, Home and the Principles page, replacing the old combined sentence the renumber kept. Words come from the pinned page only.
2. DEL-17 (revised): `criteria.py revise DEL-17` with the pinned five lines (DEL-17.1 to DEL-17.5; the Tokens part already left for DEL-28); HLT-7's fold is deferred (TD1018, outside the done lines): the PR notes name it as left for v1.2.0.
3. DEL-19 (revised again): `criteria.py revise DEL-19` with the pinned DEL-19.1 to DEL-19.5, including the one list of eight step names; the pages that carry the old step list (README, Home, Principles, Delivery) follow the generated rows.
4. DEL-25, DEL-26 and DEL-27 (new, principle 3 Fast, Delivery): added with the repo's own functions (`pf.unit`, `pf.enc`, `ms.rput`), as DEL-23 was added; each with its flow figure from the repo's route and its how-to item.
5. DEL-22 (TD1019, revises Q1): a new unit with its pinned title "Fast plans" and its pinned text, word for word from the pinned page (lines 108 to 147 of the extracted text, five requirement lines; the default-settings note and the test-lane line are not requirement text unless the page marks them so, checked against the HTML). Added with the repo's own functions (`pf.unit`, `pf.enc`, `ms.rput`) under 3 Fast on Delivery, Milestone v1.2.0, left Unreviewed (no record names DEL-22). No stub.
6. Reviewed marks last: `criteria.py review ... --user --owner-record` with o738 to o742, each record used once (mapping: Open question 2). A refusal stops and goes to operation word for word.
7. Old-number references: re-sweep for `Principle N`, `## N.` and `principle-0N` after the renumber merges; fix any the renumber missed.
8. Regenerate (`criteria.py render`, `dev/system-design.py`, `render.py blocks`), then run: `docs.py check --base origin/main --own`, `criteria.py render --check`, `dev/system-design.py --check`, `dev/package.py --static`, the private-name scan, and the committed read-only compare script (a copy of the `docs/v110-text-check.py` pattern) comparing every new or revised unit (DEL-22 included) to the pinned page sentence by sentence, with a changed word failing it.

## Open questions for operation (answers needed before the build)

1. DEL-22 is not in the docs on main (it exists only as `.loop/tasks/v120-del22.md`, release v1.2.0, source frozen-source-v1.2.0-0942). Done line 1 says "DEL-22's title 'Fast plans' as pinned". Which is meant: (a) add DEL-22 with the pinned title and its five lines as a new feature on Delivery; (b) change only a title that already exists elsewhere; (c) leave DEL-22's text to v120-text and write nothing here?
2. Which of o738 to o742 marks which feature (DEL-19, DEL-17, DEL-25, DEL-26, DEL-27, and DEL-22 if (a))? Five records, up to six features.
3. HLT-7's fold: is a Retired pointer line plus its row moving into DEL-17 wanted here (the renumber goal explicitly leaves the fold to this goal)?
4. DEL-19's build is in v1.2.0 (o749) but its text stays here: confirm the revised DEL-19 text goes in exactly as pinned, including the eight step names that no code yet runs.

## Not in scope

Principle numbers and names, DEL-28 and the Tokens move, any code, DEL-19's build, DEL-22's tests, v120 tasks, any regression row change beyond one that a page rename forces.

## Test for each done line

1. `docs.py check` prints DOCS OK; the compare script finds every pinned sentence in the repo and no extra word; marks present for the named features; grep for old principle numbers is empty outside history.
2. Size: `wc -c` on every script under skills/ unchanged (text files only); file count by `dev/package.py --static` unchanged or within MAX_FILES; no regression row edited; no new file under skills/; the committed text never names the service repo (private-name scan).

## Answered (operation, from owner-words)

- Marks: o738 = DEL-19, o739 = DEL-17, o740 = DEL-25, o741 = DEL-26, o742 = DEL-27. No record exists for DEL-22.
- DEL-17 carries o791 after the renumber; revising it to the pinned five lines clears that mark. Re-mark with o739 only on a word-for-word match with the pinned page; if the tool refuses o739, leave DEL-17 Unreviewed and send the refusal word for word.
- Open with top: Q1 (DEL-22), Q3 (HLT-7 fold), Q4 (DEL-19 as pinned).

## Rulings (TD1018)

- Q1: DEL-22 title only, exactly as done line 1; its body comes with its v1.2.0 task.
- Q3: HLT-7 fold deferred; named in the PR notes as left for v1.2.0.
- Q4: DEL-19 exactly as pinned (o738); the PR notes say its eight step names get built in v1.2.0 (o749).
- Every mark only on a word-for-word match and a record the tool accepts; on refusal the feature stays Unreviewed and the refusal goes to operation verbatim.

## Placement question (open)

A title without the feature has no unit to live in. I would carry it as the title of the DEL-22 row in the principle-3 Fast table only if the docs check accepts a row with no unit; I will test that in a scratch clone and report; if it fails, I ask where else before building.

## TD1019

DEL-22 goes in as a full unit, Unreviewed, Milestone v1.2.0, accepted by top under o776 as a plan break (owner-pinned text only, no reviewed text changed, no check weakened). The "Placement question" above is closed: no bare row, no stub. Risk to check in the build: a new Unreviewed unit with a v1.2.0 milestone must pass the docs check and the milestone checks; if either refuses, stop and send the refusal verbatim.

## Gate 1 findings folded in (no ruling needed)

- Compare script (C): extend `docs/v110-text-check.py` (it already takes PINNED_HTML and a PIN) with this goal's IDs and pin; no second script. Add a regression row for it only if one can be added without changing any existing row; otherwise name the gap in the PR notes (B2: it runs by hand against an HTML that never enters the repo).
- Never hand-edit past a tool refusal (B2): every `revise`, `retire`, `review` or add refusal goes to operation word for word and the step stops; the earlier "else page text" fallback for HLT-7 is withdrawn.
- Size: `criteria.py` is 20,455 bytes, 25 under the 20,480 limit. No change to it; a refusal that would need one goes to operation.
- Verify by hand: the goal's section is empty; I will add numbered steps with `Expect:` lines (open the Principles page and see principles 1 to 8 with the pinned 3, 4, 5 sentences; open Delivery and see DEL-17, DEL-19, DEL-22, DEL-25, DEL-26, DEL-27 as pinned) unless operation says the frozen file may not take them.
- DEL-17 pin: before revising, check whether the pinned five lines still hold a Tokens line; the renumber moved Tokens to DEL-28, so DEL-17 and DEL-28 must not duplicate it. If the pin holds Tokens, stop and ask.
- Regression rows: HLT-7 has five rows (docs-check-speed, mon9-board-fast, aut-email-rounds, hlt7-fast-check, aut7-budget-agrees). Retiring HLT-7 is deferred (TD1018), so none moves; if the owner's o752 and a record that passes the tool bring the fold back, the rows' goal column moves in the same change.
- DOC-26 cap: 3 Fast would hold DEL-17, HLT-7, DEL-22, DEL-25, DEL-26, DEL-27 (six or more) while HLT-7 stays. Stop and ask before the build if no ruling allows it.
- Revisions tables: each new unit (DEL-22, DEL-25, DEL-26, DEL-27) needs a Revisions table with an r1 row (pageformat REV-ROW); the "approved" cell uses a record the tool accepts, never invented text.
- Merge order: v110-fast-checks (DEL-25 code) and this goal both touch DEL-25; I check its branch before the lane and report the order.
- o794 means build now in v1.1.0; scope unchanged.
- Line numbers refer to bb7a38bc8 and are re-measured at build start.

## Held for top (owner records)

o738 to o742 carry no slug, so `revise` refuses on them (REV-RECORD); o756 is the only record naming this slug, for a different text. o747 (DEL-22) and o752 (HLT-7 retired, folded into DEL-17) already exist. The build waits for one record whose ids hold the slug and the IDs (operation is asking top).

## TD1022 (withdraws TD1018 Q1, Q3 and TD1019; supersedes earlier DEL-22, HLT-7 and record text above)

1. DEL-22 goes in as reviewed text on the 17:42 pin, under 3 Fast (o747), Milestone v1.2.0 as the pin says. No stub, no title-only.
2. The HLT-7 fold happens in this goal (o752): HLT-7 is retired into DEL-17 with the repo's own `criteria.py retire`, and its five regression rows (docs-check-speed, mon9-board-fast, aut-email-rounds, hlt7-fast-check, aut7-budget-agrees) are re-keyed from goal HLT-7 to DEL-17 in the goal column only; commands and PASS text untouched, nothing loosened. This also brings 3 Fast to DEL-17, DEL-22, DEL-25, DEL-26, DEL-27 (five), inside DOC-26's cap.
3. DEL-17 stays without its Tokens line (o756 and o791 are later than the pin and rule): the five pinned DEL-17 lines are used minus any Tokens text; the compare script states this exception explicitly.
4. No hand fallback. Every tool refusal goes to operation word for word and the step stops.
5. The compare script is `docs/v110-text-check.py`, extended, no new script.
6. Records: one scope record (id to come from operation) names this slug and covers revise (DEL-17, DEL-19), add (DEL-22, DEL-25, DEL-26, DEL-27) and retire (HLT-7 into DEL-17); it is not used for marks. Marks, one ID per record: o738 DEL-19, o739 DEL-17, o740 DEL-25, o741 DEL-26, o742 DEL-27, o747 DEL-22; a refused one ships that feature Unreviewed with exactly the approved words, refusal sent verbatim. The r1 Revisions rows of the new units use the scope record in their "approved" cell.
7. criteria.py has a 25-byte margin: I do not change it; I measure with `wc -c` before and after.
