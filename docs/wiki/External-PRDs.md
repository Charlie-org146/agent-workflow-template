<!-- workflow-docs -->
# External PRDs

Review: **Unreviewed**

## Problem

- My product requirements live in Notion, and the repo's copy of them goes stale without anyone telling me.
- Agents change a requirement in the repo as they build and people change it in Notion, and neither side learns of the other's change until someone happens to notice.
- I never want a tool to overwrite either side on its own: when the two differ I want to be told, decide which text stands, and have the agent write only that text, Notion included.

## Requirements

### Functional

- EXT-1: **Unreviewed** Either side can change a requirement
  - A requirement can be added or changed in the repo's copy, by an agent's goal, or in the external document, by people.
  - A feature's PRD source can be `url:<link>` or `mcp:<server>:<resource>`; `.loop/prd/PAGE.md` is the repo's copy, and the first `docs.py sync` adopts the source into it.
  - Syncing is opt-in per PRD: a PRD lives in the repo by default, and only a page whose PRD source in `.loop/docs.tsv` is a `url:` or `mcp:` source takes part. Every other page is never visited and raises no signal.
- EXT-2: **Unreviewed** A difference is a delta, never a silent overwrite
  - `docs.py sync` compares both sides with what they last agreed on, and each difference is a DELTA naming the page, the id, which side changed (the repo, the source or both) and both texts.
  - Sync never overwrites either side on its own, and `--dry-run` only reports and exits 1.
  - A hand-written file at the repo copy's path is left as it is.
- EXT-3: **Unreviewed** A delta is reviewed, then both sides agree
  - Each delta is posted once as a GitHub issue on the feature's milestone and once as a comment on the Notion page, and stays open until someone accepts one side's text.
  - `docs.py sync --accept PAGE:ID=repo|source` writes only the accepted text to the other side, Notion included, closes the delta and leaves every other requirement as it was.
  - Health and the check-in show each open delta as an inconsistency, only for a page that opted in; a repo or page with no external source never shows one.
- EXT-4: **Unreviewed** No connector never breaks the loop
  - A source, gh or writer that sync cannot reach prints `not connected`, changes nothing and exits 0, and the delta stays open.
  - A source with no requirement ids keeps the repo's copy instead of emptying it.

### Non-functional

None

## Non-goals

- Syncing milestones (the GitHub milestones and a Notion Milestones page) or the README: left for a later goal.
- Choosing which pages opt in: the owner sets a page's PRD source, and nothing here sets one.
- Writing to Notion, or to any source, without an accepted delta: the agent writes only text the owner accepted.
- Google Docs: the same mechanism, added when a repo needs it.

## Success metrics

- A requirement edited in Notion or in the repo shows as a delta on the next sync with neither side touched, and after it is accepted both sides say the same.
- Every open delta shows in health and the check-in until it is accepted.

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [sync-first-adopts](Tests#t-sync-first-adopts) | requirement | EXT-1 | Given an external PRD and no repo copy, when docs.py sync runs, then it adopts the source with a baseline and no delta. | not run |
| [sync-repo-delta](Tests#t-sync-repo-delta) | requirement | EXT-1 | Given a requirement an agent changed in the repo copy, when docs.py sync runs, then it prints a DELTA naming the page, the id, the repo as the side and both texts. | not run |
| [sync-source-delta](Tests#t-sync-source-delta) | requirement | EXT-1 | Given a requirement people changed in the external document, when docs.py sync runs, then it prints a DELTA naming the source as the side and both texts. | not run |
| - | requirement | EXT-1 | no passing test | not enforced |
| [sync-both-sides](Tests#t-sync-both-sides) | requirement | EXT-2 | Given a requirement changed in the repo and in the document, when docs.py sync runs, then its DELTA says both sides changed. | not run |
| [sync-dry-run-drift](Tests#t-sync-dry-run-drift) | requirement | EXT-2 | Given a delta, when docs.py sync --dry-run runs, then it prints the DELTA, exits 1 and posts and writes nothing. | not run |
| [sync-delta-no-overwrite](Tests#t-sync-delta-no-overwrite) | requirement | EXT-2 | Given a delta, when docs.py sync runs, then the repo copy and the external document are both unchanged. | not run |
| [sync-owns-only](Tests#t-sync-owns-only) | requirement | EXT-2 | Given a hand-written file where the repo copy goes, when docs.py sync runs, then it is SKIPPED and left as it was. | not run |
| - | requirement | EXT-2 | no passing test | not enforced |
| [sync-delta-posted](Tests#t-sync-delta-posted) | requirement | EXT-3 | Given a new delta, when docs.py sync runs, then it posts one GitHub issue on the feature's milestone and one comment on the external page. | not run |
| [sync-posts-once](Tests#t-sync-posts-once) | requirement | EXT-3 | Given a delta already posted, when docs.py sync runs again, then it posts nothing more. | not run |
| [sync-accept-source](Tests#t-sync-accept-source) | requirement | EXT-3 | Given a delta, when docs.py sync --accept PAGE:ID=source runs, then the source's text is written to the repo copy for that id only and the issue is closed. | not run |
| [sync-accept-repo](Tests#t-sync-accept-repo) | requirement | EXT-3 | Given a delta, when docs.py sync --accept PAGE:ID=repo runs, then the repo's text is written to the external document through the writer for that id only and the issue is closed. | not run |
| [sync-agree-after-accept](Tests#t-sync-agree-after-accept) | requirement | EXT-3 | Given every delta accepted, when docs.py sync runs, then the sides are in step and no delta is open. | not run |
| [sync-open-lists](Tests#t-sync-open-lists) | requirement | EXT-3 | Given an open delta, when docs.py sync --open runs, then it lists the delta with no call to gh or the connector. | not run |
| [sync-health-delta](Tests#t-sync-health-delta) | requirement | EXT-3 | Given an open delta, when health checks the docs, then it reports a FAIL row of the docs rule for it. | not run |
| [sync-board-delta](Tests#t-sync-board-delta) | requirement | EXT-3 | Given an open delta, when the check-in's board is built, then it lists the delta as waiting on the owner. | not run |
| - | requirement | EXT-3 | no passing test | not enforced |
| [sync-not-connected](Tests#t-sync-not-connected) | requirement | EXT-4 | Given an mcp source and no connector, when docs.py sync runs, then it prints not connected, writes nothing and exits 0. | not run |
| [sync-no-writer-posted](Tests#t-sync-no-writer-posted) | requirement | EXT-4 | Given no writer, when docs.py sync finds a delta, then the issue is posted and the comment says not connected. | not run |
| [sync-accept-no-writer](Tests#t-sync-accept-no-writer) | requirement | EXT-4 | Given no writer, when docs.py sync --accept PAGE:ID=repo runs, then it says not connected, exits 0 and changes nothing. | not run |
| [sync-no-gh](Tests#t-sync-no-gh) | requirement | EXT-4 | Given gh that fails, when docs.py sync finds a delta, then it shows the delta, says not connected and exits 0. | not run |
| - | requirement | EXT-4 | no passing test | not enforced |
