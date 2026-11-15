# offline-prd-copy: design

## Problem
A PRD page opted in to an external source (docs.tsv `url:` or `mcp:`, DOC-17) is a link-form page: its ids are read fresh from the
source by `prd.read_link` in the docs check (`deployments.link_page`) and in `render.py`'s tables, so without a reader (CI, a lane, a
machine with no connector) the check says UNREAD and `criteria.contract` suppresses its LINK check; rows, health and the wiki see no
requirements of the page. `docs.py sync` keeps `.loop/prd/PAGE.md`, but that copy is a plain `- ID: text` mirror for diffing, not a PRD.

## Approaches
1. Keep link-form reads, add a cache of the last source read. Cost: small. Risk: a cache that may go stale, reads still fan out, and the
   wiki page still shows no requirements.
2. The copy becomes the PRD (chosen). `.loop/prd/PAGE.md` holds the last agreed version in the repo's own layout (Problem, Requirements,
   Non-goals, Success metrics), written by sync; every reader takes the copy; the wiki page carries a generated block of those four
   sections between `<!-- prd:begin -->` and `<!-- prd:end -->`; sync reads the source only when a reader is set.

## What changes (package stays at 98 files or fewer: 94 now, two new scripts)
- `prdcopy.py` (new): `normalise(text)` brings a source's layout to the repo's (`NL-1 Functional: (Reviewed 2026-11-10) text` becomes
  `- NL-1: **Reviewed 2026-11-10** text`; a `New requirements` heading merges into Requirements, its lines Unreviewed unless marked),
  `read(root, page, source)` (the copy when it exists, else `prd.read_link`), `block(copy)` and `with_block(page_text, copy)`.
- `prdsync.py` (new): `sync` moves out of `audit.py` (which has 100 bytes to spare) and gains: the reader is asked only when one is set
  (no `LOOP_PRD_READER`, no file or http source: `not connected`, nothing changes); adoption writes the full normalised PRD as the copy;
  an id on one side only or changed on one side is a delta accepted with `--accept PAGE:ID=repo|source` (accept=source writes the
  source's block into the copy, accept=repo posts the repo's text to the source as today); an id changed on both sides prints
  `CONFLICT` (a delta naming both texts, posted once, never merged). The Problem, Non-goals and Success metrics are adopted once and
  refreshed only by hand in the copy; a differing source prints a NOTE, never a delta.
- `deployments.link_page`: reads the copy; the four PRD sections are allowed on a link-form page when they are exactly the generated
  block; else SECTIONS as before. With a copy and no reader there is no UNREAD and no LINK failure; with neither, UNREAD says so.
- `render.py`: tables take ids from the copy; the block is refreshed with the tables (`docs.py render`), so the wiki page shows the PRD.
- Pages with no source are untouched (no read, no block, no signal).

## Done lines
1. A page with a source and a copy passes the check, audit, health and the rows with no reader; no LINK or UNREAD.
2. The wiki page shows the four sections as the generated block; `link_page` allows them only as that block.
3. sync: reader only when set; normalises; deltas from either side; CONFLICT; never overwrites.
4. Toys proven red for each; sizes under 19,000; no `~/.workflow-loop` file touched; the DOC-17 text goes to operation first (records o37, o38).

## Open
- The exact layout of the Notion page (operation was asked for a sample); the normaliser also accepts `- ID: text`, `ID: text` and
  `| ID | text |` rows through `entry.REQ`, so an unseen layout falls back to the plain text.
