# external-sync: design

## Problem
A feature's PRD can already live outside the repo (`url:<link>` or `mcp:<server>:<resource>` in `.loop/docs.tsv`, set by
prd-link-topics), but nothing keeps the repo's side of it in step. The repo page holds only the `PRD: <source>` line and the
generated sections, so a requirement added, removed or reworded in Notion changes nothing in the repo until someone notices:
agents then work from stale ids and the Tests table keys on ids that no longer exist.

## Approaches
1. A new `sync.py` script. Cleanest, but the package is at its 98-file cap, so it cannot ship. Rejected.
2. A `sync` verb on `docs.py` whose logic lives in the existing, roomy `audit.py` (8 KB of 20 KB). Cost: `docs.py` grows by a
   few hundred bytes; risk: none beyond keeping `docs.py` under 20,480 bytes. Chosen.

## What it does
`docs.py sync [--dry-run] [--text PAGE=FILE]` visits each feature whose PRD source is `url:` or `mcp:` (pages with source
`page` are the repo's own PRD and are never touched). It reads the PRD through `deployments.read_link` (the same
`LOOP_PRD_READER` connector or fetched URL as `check`; `--text` hands it text a session fetched through its own connector),
extracts the requirement ids and their text, and compares them with the repo's copy, `.loop/prd/<Page>.md`: a file that
opens with `<!-- prd-sync: owned -->` and holds one `- ID: text` line per requirement. A difference prints
`DRIFT <page>: <ID> added|removed|changed ...`. Unless `--dry-run`, it rewrites that file to match and prints `SYNCED <page>`.
Why a sidecar and not a block on the wiki page: a link-form page's head may hold only the title, Milestone and Review lines
and its sections only Runbook, Deployments and Tests (Tests is rewritten by render), so any mirror text there would break the
page contract. "Owns" is concrete: sync writes only a file that opens with its marker, creates it when absent, and prints
`SKIPPED` for a hand-written file at that path.
- Never writes to the external source: the reader is read-only and no write call exists.
- No connector, or any unreadable source: prints `not connected: <page> (<source>): <why>`, changes nothing, exits 0.
- A source with no requirement ids keeps the mirror (`EMPTY`), never wipes it.
- `--dry-run` exits 1 when there is drift, so a check can use it.

## What each done line needs
A toy (`dev/toy/test-docs-sync.py`) with a fixture repo and a fake reader: DRIFT for a changed requirement and the page
rewritten to match; not connected with no connector; a `page` source untouched; no write to the source; seen red first.

## Open questions
PENDING: none. README and milestones as external sources are the same mechanism, left for a later goal.
