# Plan: v120-del3-text

Design: `.loop/goals/v120-del3-text.design.md`. Source: `.loop/goals/v120-del3-text.source.md` (verbatim, sha256 bd3be682e232246073a08b71109769b55d1d01f609051674850d40966a087fc4). Checker: `docs/designs/v120-del3-text-check.py` (committed, with a self-test). Text only: no product script, toy or regression row changes.

## Claims checked against the code

- `criteria.py revise|review` are wired in `skills/workflow-docs/scripts/milestones.py` (`revise` line 260, `record` line 225) and the `review` path in `criteria.py`. `revise --text-file` takes line 1 as the title and strips a leading `- ` from every later line before writing it as a `  - ` sub-bullet (milestones.py:288); it writes the revision cell with `pageformat.unit` (whitespace squeezed, lines joined with ` <br> `). `pageformat.py` lines 255-285 hold the format limits (one `  - ` level, at most 20 words in an Unreviewed title, at least one sub-bullet).
- Both commands need an owner record whose names column covers the goal slug and DEL-3 or Delivery (milestones.py:225-231, deployments.py:283-286). The build starts only when operation gives the id of the owner's own typed line (step 0).
- Delivery.md today: DEL-3 at lines 23-29 (r6, Reviewed 2026-11-20), revision table `### DEL-3` at lines 108-117 (r1 to r6), Tests rows for DEL-3 mapped by id.

## Build steps (after the Mac's plan gate, the owner's typed line, and operation's word)

0. **Wait for the owner's line.** No `revise` and no `review` until operation records, as the owner typed it, one line for DEL-3 in the flat layout (the question put to the owner: "Mark DEL-3 Reviewed in the flat layout?"), with names covering `v120-del3-text`, DEL-3 and Delivery, and tells this worker its id (`OWNREC` below). This worker never makes or edits an owner record.
1. Body: `python3 docs/designs/v120-del3-text-check.py --body > <scratch file outside the repo>`. Line 1 is the page's unchanged title; each later line is a source line (DEL-3.1's five list lines lose their `- `), tagged ` [DEL-3]`. The tag is part of the layout like every other line on the page; the count check skips lines naming their own requirement (counting.py:154-155), so the tag is kept and not dropped later without a new goal.
1b. Dry run in a clone that shares nothing with the real repo: `git clone --no-local <repo> <scratch>`, never a copy of the worktree. Run steps 2 and 3 there with a scratch owner record naming the goal, DEL-3 and Delivery, then `docs.py check --own` and the checker. The real `owner-words.tsv` and `reviews.tsv` are checksummed before and after and must be unchanged. Any layout refusal is fixed by layout only. The source has no `|`, no `<` and no non-ASCII, so `enc` and `unit` keep it byte for byte (the checker asserts it).
2. `LOOP_ROLE=worker python3 skills/workflow-docs/scripts/criteria.py revise DEL-3 --owner-record OWNREC --goal v120-del3-text --why "v1.2.0 revised DEL-3: DEL-3.1 to DEL-3.10, word for word from the owner's v1.2.0 PRD page (artifact version 1795339637-d10d)" --text-file <scratch>`. It adds r7 and leaves DEL-3 Unreviewed.
3. `criteria.py review DEL-3 --user --owner-record OWNREC` (review has no --goal flag; the slug comes from the branch name). The r7 approved cell then cites OWNREC with the owner's words; the why cell names the owner's earlier lines o311 (PC) and o780 (Mac), 2026-11-22 01:29:44 PT, which were typed before this layout existed.
4. Copies, then render-last (TD885), all in one commit with the checker run after:
   - Hand-update the DEL-3 copies under `docs` mechanically from the new sub-bullets, adding no word: `docs/wiki/Home.md` Requirements-by-feature row (line 129: title, then each line tagged and joined with `<br>`, the format of the other rows), the DEL-3 Summary cell on `docs/wiki/Home.md` (line 107) and `docs/wiki/Principles.md` (line 97) (the lines joined with spaces, untagged, the way the other principles' Summary cells are built). README.md (lines 110 and 132) is outside this goal's Touches and goes with core's PR.
   - Then one `criteria.py render` commit, `audit.py restamp-own` for any stale page, `wiki.py prepare` (commits nothing), `docs.py check --own` clean, `git status` empty. If the docs check refuses the Home and README copies disagreeing, stop and tell operation-pc (README.md would have to join the Touches); never hand-edit around it.
5. Lane later, when operation-pc says: merge main up, render-last, 0 behind, one lane (TD915) with the session env cleared.

## Tests per done line (no new regression row)

The goal's Touches are `docs/wiki/Delivery.md` and `docs`; a regression row needs `.loop/regression.tsv` and a toy under `dev/toy`, which are outside them. The three checks are run by hand on the committed head, by this worker and again by the Mac, and again by operation on core's PR head (core's plan carries those merge-time checks). The lane runs the existing docs-check rows on the head.

1. **Word for word.** `python3 docs/designs/v120-del3-text-check.py` (committed; exits 0 and prints `WORD FOR WORD OK`). It pins the source's sha256, expects the source's non-blank lines in order (DEL-3.1's five `- ` lines without the `- `), reads Delivery.md's DEL-3 sub-bullets with only the leading `  - ` and trailing ` [DEL-3]` removed, requires them equal line for line, and requires the first row of the `### DEL-3` table to equal `pageformat.unit(title, tagged lines)` (the same function that wrote it, so the whitespace and ` <br> ` joining are the tool's own). `--selftest` shows it failing on one word changed, one line dropped, one line added and a differing revision row, and passing on a faithful page. Seen failing now on main's r6 text. The anchor to the owner's page is the Mac gate's diff against the artifact, which stays a gate.
2. **Review mark.** `docs.py check --own` has no DEL-3 finding; the DEL-3 line reads `**Reviewed 2026-11-22**` with a seal; the `### DEL-3` table's first row is r7 and cites OWNREC with the owner's own typed words, its why cell naming o311 and o780; `reviews.tsv` has the review entry. Seen failing before: main's DEL-3 reads Reviewed 2026-11-20 with six r1-r6 rows.
3. **No other feature's text changes.** `git diff origin/main -- docs README.md` shows hunks only in the DEL-3 requirement block, the `### DEL-3` revision table, the three DEL-3 copies of step 4, Delivery.md's stamp lines and render-owned Tests tables; `criteria.py guard` prints `GUARD OK`; the seal of every other requirement line is byte-identical to main's.

## Verify by hand (for the goal's own section, if operation allows it to be filled)

1. Run `python3 docs/designs/v120-del3-text-check.py`. Expect: `WORD FOR WORD OK: 36 lines, the revision row equals them`.
2. Run `python3 docs/designs/v120-del3-text-check.py --selftest`. Expect: `SELFTEST OK`.
3. Open docs/wiki/Delivery.md at DEL-3. Expect: Reviewed 2026-11-22, ten DEL-3.n blocks, each with its Metric and Test lines.
4. Run `docs.py check --own`. Expect: no DEL-3 finding.

## What could break

- The owner's line is missing or does not cover the goal, DEL-3 and Delivery: the build does not start; nothing is hand-edited around it.
- The page format refuses the layout: fix by layout only, never by changing words; if the source cannot fit without changing words, stop and tell operation-pc.
- A render or restamp rewriting other pages: only stamp lines, Tests tables and DEL-3's own copies may change; any other ID's text is reverted.
- The about 8 Tests rows mapped to DEL-3 keep their ids; their descriptions say the old DEL-3 and are not changed here (a later goal).

## Out of scope

Any product script, toy or regression row; the requirement title; other features' text; README.md rows; the page's Problem, Non-goals and Success metrics sections; DEL-3.1 to DEL-3.10 behaviour (v120-del3-core and v120-del3-rules); the confidence figure and the merge order, which belong to v120-del3-core's plan (this goal has no pull request of its own and merges inside core's).

## Findings to file (through operation, not goal.py finding)

1. README.md:110 and :132 keep DEL-3's r6 text after this goal (outside the Touches); core updates them. Backlog: Delivery.
2. The Tests rows mapped to DEL-3 describe r6 behaviour; their descriptions need rewording to the new DEL-3.n. Backlog: Delivery.

## PENDING

- Owner: one typed line for DEL-3 in the flat layout (operation puts the question). The flattening keeps every word and loses the nesting: DEL-3.1's five list items and every Metric and Test line sit at the same level as the DEL-3.n lead lines.
- Not pending: a regression row for the three done lines (outside the Touches; hand checks plus the committed checker and the existing docs-check rows).

## Budget and ETA

- ETA 190 active minutes (frozen at goal start): MISSED. Cause: the goal's merge waits behind the two confidence goals and the v1.2.0 cut, and the plan has been through 13 gates. Operation records the missed ETA in its ledger.
- From now on each gate adds one line to Review with its number and the time spent, so the budget per step is visible.

## Review

Gates 1 to 12 (Mac, independent): word for word PASS each time (1213 words each side). Their findings were folded in, and the confidence and merge-order material they led to moved to v120-del3-core's plan. Gate 13's reply is held locally by operation's instruction (TD944); this revision follows top's TD1021. Not yet gated: this head.
