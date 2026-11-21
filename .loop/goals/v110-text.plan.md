# Plan: v110-text

Design: the idea step recorded a design in the run record (builder mode, a native second opinion; the design doc stays outside the repo). The plan step ran by hand because /autoplan refused with `init_mismatch` (the owner's words o721 allow a hand plan): /plan-ceo-review (HOLD SCOPE), /plan-devex-review and /plan-eng-review each ran from their own section files, plus a Codex outside voice that was unavailable (no Recommendation line) and a native engineering read. The full review text is kept outside the repo; this file holds the implementation plan and what the review changed.

Timing note: this file was committed after the build commit b23a56e80. The plan was fixed and recorded before the build (run record, plan step, depth full).

## URGENT, outside this plan

None. One tooling defect found while reviewing: `dev/system-design.py` has no `--help` and rewrites its two SVGs when called with it (reported to the operation session).

## Implementation plan

Source: the owner's pinned page frozen-source-v1.1.0-1052 (sha256 cd66455a83be4a0b). Done lines are frozen in `.loop/goals/v110-text.md`.

Build order (the Reviewed marks are the last write, because the mark seals the text and a record can be used once):

1. B1. Extract the three feature units and the brief section from the pinned page with a scratch script kept outside the repo; check the page hash first.
2. B2. `criteria.py revise DEL-19` and `revise DOC-28` with `--owner-record o721 --text-file`; add DEL-23 by hand after DEL-21 with its r1 revision row built by the repo's own functions (`pf.unit`, `pf.enc`, `ms.rput`).
3. B3. Sync the principle-table and by-feature rows on README, Home and Principles, the how-to items and the flow figures (new DEL-23.svg; DEL-19.svg and DOC-28.svg redrawn from the new requirements); run `criteria.py render`, then `dev/system-design.py` and `--check`.
4. B4. Write the brief section into `docs/release-brief-v1.1.0.md`, marked frozen; the service repo's name is written "the service repo".
5. B5. One sentence on the Principles page: principle 1 may hold 8 features until v2.0.0 (o721). It sits in the page head, because the front-page check allows only a sentence, an image and one table line inside a principle's section.
6. B6. Add the one new link origin (`trunkbaseddevelopment.com`) to `scripts/public-origins.json` and to the network list in `listing.json`; nothing else in either file.
7. B7. Checks: `docs.py check`, `criteria.py render --check`, `dev/system-design.py --check`, `dev/package.py --static`, the private-name scan; a script compares the final repo units to the pinned page sentence by sentence (with a control that a changed word fails) and proves every other feature unit is byte-identical to the base.
8. B8. Preflight that record o721 is unused in the review log, then `criteria.py review DEL-19 DEL-23 DOC-28 --user --owner-record o721`; re-run the checks.

## What the review changed in the plan

- Compare the final repo units, not only the extractor output (`revise` strips bullet prefixes and blank lines).
- Marks last and a preflight on o721 (single use per record).
- Regenerate the system-design figures, then check them.
- Redraw the figure bodies, not only their titles; no check validates their content.
- Name which check reads which origin file: the docs check reads `scripts/public-origins.json`, the package check reads `listing.json`.
- The generated "What this is" paragraph changes because it is built from every sub-bullet of DEL-19; accepted as is (operation session, 11:15), with the before and after at the top of the PR notes.
- Done line 4 is read as the Principles page, because DOC-26 holds the limit and is Reviewed and protected by done lines 1 and 2; nothing enforces the cap today, so no check changes.

## NOT in scope

- DOC-26 text or mark; any code in the docs, review or system-design tools; enforcing the cap of 8; the task list, board and checks of DEL-23, DEL-19's format and DOC-28 (T3); the service repo's migration (out of v1.1.0 by o721); the pinned page's explanatory prose and its three questions (not features); new regression rows or tests (done line 5: no row changes result).

## Failure modes

| step | failure | handled | the owner sees |
|---|---|---|---|
| B1 | pinned page changed | hash check stops | message, no write |
| B2 | record missing | the tool refuses with a code and a fix | REFUSED text |
| B4 | the commit hook blocks a name | stop, report the hook's words | hook text |
| B7 | stale generated block | rerun render | STALE line |
| B8 | record already used | preflight stops before the write | refusal |

No critical gaps.

## Decision audit

- D1 line 4 reading: the Principles page (operation session, relayed 11:00).
- D2 "What this is" paragraph: accepted (operation session, 11:15).
- D3 DOC-28's old Problem, Non-goals and metrics rows are replaced by the pinned page's content and stay in its revision rows.
- D4 the service repo's name written "the service repo"; each line is listed in the PR notes.

<!-- autoplan-accepted:eng -->
- Marks last; final-text compare; system-design regenerate then check; origins in both lists; one sentence on the Principles page.
<!-- /autoplan-accepted:eng -->
