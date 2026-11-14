<!-- workflow-docs -->
# External PRDs

Review: **Unreviewed**

## Problem

- My  product requirements live in Notion, and the repo's copy of them goes stale without anyone telling me.
- When a requirement changes there, the agents working in the repo keep building from the old wording until someone notices.
- I never want a tool in the loop to write into my own document.

## Requirements

### Functional

- EXT-1: **Unreviewed** The repo's copy of a PRD kept elsewhere follows it
  - A feature's PRD source can be `url:<link>` or `mcp:<server>:<resource>`; `docs.py sync` reads it and compares its requirement ids and text with the repo's copy in `.loop/prd/`.
  - Each requirement added, removed or changed is a DRIFT line naming the page and the id, and the copy is rewritten to match; `--dry-run` only reports and exits 1.
  - A page whose PRD lives in the repo is never visited.
- EXT-2: **Unreviewed** The loop only ever reads my document
  - Sync rewrites only the repo's copy, and only a file it wrote itself; a hand-written file at that path is left as it is.
  - Nothing in sync calls a write on the source, whether it is a link or a connector.
- EXT-3: **Unreviewed** No connector never breaks the loop
  - A source sync cannot read prints `not connected`, changes nothing and exits 0.
  - A source with no requirement ids keeps the repo's copy instead of emptying it.

### Non-functional

None

## Non-goals

- Syncing milestones or the README from an external source: left for a later goal.
- Writing to Notion, or to any source, from the repo.
- Google Docs: the same mechanism, added when a repo needs it.

## Success metrics

- A requirement edited in Notion shows as DRIFT on the next sync and is gone after it, with the Notion page untouched.

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [sync-drift-rewrites](Tests#t-sync-drift-rewrites) | requirement | EXT-1 | Given an external PRD whose requirement changed, when docs.py sync runs, then it prints DRIFT for it and rewrites the repo copy to match. | not run |
| [sync-dry-run-drift](Tests#t-sync-dry-run-drift) | requirement | EXT-1 | Given a source that added, removed and changed requirements, when docs.py sync --dry-run runs, then each is a DRIFT line, nothing is written and it exits 1. | not run |
| - | requirement | EXT-1 | no passing test | not enforced |
| [sync-owns-only](Tests#t-sync-owns-only) | requirement | EXT-2 | Given a hand-written file where the repo copy goes, when docs.py sync runs, then it is SKIPPED and left as it was. | not run |
| [sync-source-readonly](Tests#t-sync-source-readonly) | requirement | EXT-2 | Given an external PRD, when docs.py sync runs, then the source text is unchanged. | not run |
| - | requirement | EXT-2 | no passing test | not enforced |
| [sync-not-connected](Tests#t-sync-not-connected) | requirement | EXT-3 | Given an mcp source and no connector, when docs.py sync runs, then it prints not connected, writes nothing and exits 0. | not run |
| - | requirement | EXT-3 | no passing test | not enforced |
