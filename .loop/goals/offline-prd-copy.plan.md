# offline-prd-copy: plan

Checked against the code: `deployments.link_page` (reads `prd.read_link`), `render.render` (ids via `prd.read_link`), `criteria.contract`
(link branch, LINK check suppressed when `unread`), `audit.sync` (moves to `prdsync.py`), `render.mirror_of`, `criteria.put`,
`entry.requirements`/`REQ`, `counting.sources`/`ledger`, `docs.py cmd_sync`. All exist as the design says; the scripts sit at 17,966 to
18,921 LF bytes, so new code goes in two new files and call sites change by a few bytes.

## Build steps
1. `prdcopy.py`: normalise, parse, block, with_block, read.
2. `prdsync.py`: sync moved from `audit.py` with the new behaviour; `audit.py` imports it.
3. `deployments.link_page` and `render.render` read the copy; the block is allowed and refreshed.
4. The DOC-17 sub-bullets (after operation's word) with `criteria.py unreview/review Documentation --user --owner-record o37/o38`; Documentation page and its Tests table.
5. Toys and rows, each seen red.

## Tests (one per done line)
- `prd-copy-no-reader` (opted-in page, copy, no reader: check and tables pass, no LINK or UNREAD).
- `prd-copy-block` (the page shows the four sections as the block; a hand-edited block is STALE).
- `sync-delta-source-add`, `sync-delta-repo-add`, `sync-conflict` (both changed), `sync-normalises`, `sync-no-reader` (reader unset: not connected).
- `prd-copy-no-source-unchanged` (a page with no source: no block, no read).

## What could break
- Existing link-form pages with no copy keep today's read (UNREAD without a reader). Existing v1 copies (plain lines) parse through `entry.requirements`.
- Every script stays under 19,000 LF bytes; the package goes from 94 to 96 files.

## Out of scope
The two-way write to Notion itself (the writer is the owner's, `LOOP_PRD_WRITER`), thermis opt-in (pool-09 after the merge), the other reviewed text.

VERDICT: self-check: the design meets the frozen done lines
DEPTH: full
