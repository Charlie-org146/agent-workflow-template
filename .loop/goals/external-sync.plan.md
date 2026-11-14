# external-sync: plan

Checked against the code: `counting.sources(root)` maps page to its docs.tsv source; `deployments.read_link(source)` returns
`(text, None)` or `(None, why)` and honours `LOOP_PRD_READER`; `criteria.sections` and `criteria.blocks` parse a PRD's
Requirements; `docs.py` takes verbs through `main()`; `audit.py` has 12 KB of headroom under the 20,480-byte script cap and
`docs.py` about 1 KB; the package is at 98 files, so no new file.

## Build steps
1. `audit.py`: add `sync(root, dry_run, texts)` and its helpers (`requirements(body)`, `mirror_of(path)`): read each external
   source, extract `{id: text}` (strict `- ID: **Unreviewed** text` lines under Requirements, else any line starting with an
   id), compare with `.loop/prd/<Page>.md`, print DRIFT lines, rewrite only an owned file, print `not connected` for an
   unreadable source and `SKIPPED` for a file it does not own. Never calls anything that writes to the source.
2. `docs.py`: add the `sync` verb (`--dry-run`, `--text PAGE=FILE`), a `cmd_sync` that calls `audit.sync`; exit 0 unless
   `--dry-run` finds drift.
3. `dev/toy/test-docs-sync.py`: fixture repo, fake reader script. Rows: DRIFT on a changed requirement and the file
   rewritten to match (sync-drift-rewrites); not connected with no connector, exit 0 (sync-not-connected); a `page` source and
   a hand-written mirror untouched (sync-owns-only); the source file byte-identical after sync (sync-source-readonly). Each row
   seen red with `regression.py red` against a broken copy.
4. Docs: Documentation.md gets DOC-17 (Unreviewed) with its Tests rows; SKILL.md names `sync` in the Command map and the PRD
   source paragraph; references/commands.md gets the verb's syntax; `loop-files.md` names `.loop/prd/`.
5. Render Tests, run `docs.py check`, `dev/package.py`, the headroom toy.

## Tests per done line
DRIFT and rewrite: sync-drift-rewrites. "not connected": sync-not-connected. Repo side only, never the source:
sync-owns-only, sync-source-readonly.

## Could break
`docs.py` over 20,480 bytes (trim helpers into audit.py); the new `.loop/prd/` folder flagged by a hygiene or file-list check;
prd-link-topics' package failure (`tests.py` imports `counting`) is not mine, noted if it blocks.

## Out of scope
Milestones and the README as external sources; Google Docs; writing to Notion; `check` reporting drift.
PENDING: none
