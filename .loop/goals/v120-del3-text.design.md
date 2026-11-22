# Design: v120-del3-text

Goal (frozen done line): Given docs/wiki/Delivery.md, then DEL-3 carries the reviewed text of DEL-3.1 to DEL-3.10 word for word from the v1.2.0 page, its review mark cites the owner's "DEL-3 reviewed" record, and no other feature's text changes.

## Problem

Delivery.md carries DEL-3 as r6 (six bullets, Reviewed 2026-11-20). The owner's v1.2.0 PRD page (artifact WxS4qhuupMqaSHzWjeGQ4S, version 1795339637-d10d, section "DEL-3 (revised)") replaces it with ten numbered lines, DEL-3.1 to DEL-3.10, each with a Metric and a Test. The owner typed "DEL-3 reviewed" at 01:29:44 PT on 2026-11-22 (PC o311, Mac o780). The page must carry that text and mark, and nothing else may move. Code for DEL-3.1 to DEL-3.10 is the later goals v120-del3-core and v120-del3-rules; this goal changes text only.

## Source

The verbatim extraction relayed by operation-pc (from operation-mac) is committed unchanged as `.loop/goals/v120-del3-text.source.md` (sha256 bd3be682e232246073a08b71109769b55d1d01f609051674850d40966a087fc4, 10 paragraphs, no title line). The Mac's sha256 15b86428... covers the whole section extract (lines 29-99), not this slice, so it is not comparable; the Mac gate checks the slice by diff against the page.

## What the docs tool allows (read from skills/workflow-docs/scripts)

- A Reviewed requirement's text is sealed (`<!-- reviewed HASH -->`); hand-editing it fails `docs.py check` (REV-ROW / seal). The one supported path is `criteria.py revise DEL-3 --owner-record ID --goal v120-del3-text --why ... --text-file F` (adds revision row r7 to the `### DEL-3` table, rewrites the lines, leaves DEL-3 **Unreviewed**), then `criteria.py review DEL-3 --user --owner-record ID` (writes `**Reviewed 2026-11-22**` and the new seal, logged in reviews.tsv).
- `revise` needs an owner record that names the goal slug and DEL-3 (or Delivery) in its names column (milestones.py `record()`); `review` is similar (no --goal flag; it takes --user and --owner-record). The owner's typed "DEL-3 reviewed" (PC o311, Mac o780, 2026-11-22 01:29:44 PT) was typed before this flat layout existed, so the build waits for one line from the owner for DEL-3 in the flat layout, recorded as typed with names covering the goal, DEL-3 and Delivery (`OWNREC` in the plan). Nothing is built or reviewed before it.
- Format limits (pageformat.py): sub-bullets are exactly one level (`  - `); a deeper `    - ` line fails; an Unreviewed requirement title is at most 20 words; each requirement needs at least one sub-bullet; no `/Users/` style paths.

## Approaches

A. Revise through the tool, then review through the tool. Cost: needs the record naming; two commands; exact, logged, keeps the revision table and seal consistent. Risk: the record is missing today.

B. Hand-write the lines, seal and revision row. Cost: low; risk: forges what the tool is meant to write, the seal and revision row would be hand-made, and it would read as editing a Reviewed requirement without the owner's record. Rejected.

Chosen: A.

## Layout decision (words preserved, structure adapted)

The page allows one sub-bullet level and no line breaks inside a sub-bullet, but the source has multi-line items. Layout, with every word of the source kept in order and no word added to or removed from the 10 paragraphs:

- The requirement line stays as the page has it today (title unchanged, "It stops only for decisions that are mine, and asks them clearly"): the owner's extraction gives no new title, and "no other text changes".
- Each DEL-3.n paragraph becomes sub-bullets in order: its first sentence block as one sub-bullet starting `DEL-3.n ...`, then `Metric: ...` and `Test: ...` as their own sub-bullets. Each sub-bullet ends with the tag ` [DEL-3]` like today's bullets. The tag is part of the layout, not of the text: the count check skips lines that name their own requirement (counting.py:154-155), so dropping it later changes which checks run on these lines and needs a new goal.
- DEL-3.1's five list lines are not nested (not allowed): each becomes its own sub-bullet under DEL-3.1, in order, and "The list:" stays at the end of the DEL-3.1 lead sentence. The closing sentence "The list lives in one file..." is its own sub-bullet.

If the owner wants the exact nested form, the docs check has to allow it; that is a product change outside this goal's Touches.

## What each done line needs

1. Word for word: a check that strips the layout (bullets, tags, `Metric:`/`Test:` markers kept as words) and compares to `.loop/goals/v120-del3-text.source.md`. Negative control: change one word and the check fails. The revision row r7 holds the same text.
2. Review mark cites the record: the `### DEL-3` row r7's approved cell cites the owner's typed line (`OWNREC`; o311 on the PC and o780 on the Mac are named in the why cell), and `DEL-3` reads `**Reviewed 2026-11-22**` with a fresh seal; `reviews.tsv` has the entry.
3. No other feature's text changes: diff of docs/wiki against main touches only the DEL-3 block, the `### DEL-3` revision table, the three DEL-3 copies under `docs` (Home.md rows, Principles.md row, built mechanically from the new lines), the page's seal/stamp lines the tool rewrites, and the Tests tables if `criteria.py render` changes them; every other requirement line and seal is identical. README.md's copies (outside the Touches) go with core's PR and are filed as a finding.

## Open questions

1. Open, for the owner: "Mark DEL-3 Reviewed in the flat layout?" Recommended: yes. The flattening keeps every word and loses the nesting; it is the owner's layout call, so it is asked before review, not told afterwards. Operation puts the question.
2. The DEL-3 title is kept as is. Recommended; if the owner wants a title that matches the new text, that is one more line from the owner and a new record.
3. Whether the Delivery.md feature format needs the page's Problem, Non-goals, Success metrics sections to change: not in this goal's done line; left unchanged (the Non-goals of the v1.2.0 page were relayed in prose; they are not in the done line).
