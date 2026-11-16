# milestone-sync plan

Claims checked against the code (by me and by an independent reviewer): `prd.read_link(source)` reads `url:`/`mcp:` sources and honours
$LOOP_PRD_READER; `prd.out` (imported as `post` in audit.py) runs `LOOP_GH` and `LOOP_PRD_WRITER` commands and returns (ok, text);
`criteria.sha`/`criteria.put` write a sync-owned copy and its `.base`; `counting.ledger(root, rows)` keeps `PAGE:ID -> [side, issue, commented, sha8]`
in <git common dir>/loop/deltas.tsv; `docs.py sync` already takes `--dry-run`, `--accept` and `--open`; audit.sync(opened=True) already lists every ledger row.

## Gate before build
Build starts only when scripts-b's release is on origin/main and main is merged in (docs.py 20,414 and audit.py 20,447 bytes have no room, the package is
at 99 files). If the package still has no room for one more file then, milestones.py is folded into an existing docs script instead.

## Build steps (after the gate)
1. `skills/workflow-docs/scripts/milestones.py`: `repo_side(root)` (gh api milestones, paginated, JSON parsed, `title -> "state | due"`, failure = not connected),
   `parse_source(text)` (`- TITLE: state | due`, split on the last `: `, duplicate titles skipped), `read_copy(root)` (sync mark, lines, `.base`),
   `deltas(have, want, agreed)` (side = repo, source or both; absent on the source equals closed on the repo; first run baseline = equal titles only),
   `sync(root, dry, accept, opened)`: no `milestones_source` in .loop/config.json prints nothing and makes no call; `opened` prints nothing; accept splits
   with `rpartition("=")`; accepting `source` creates, edits or closes the GitHub milestone through `gh api` (POST/PATCH); accepting `repo` writes the page through
   the writer; one issue and one writer comment per delta (no `--milestone`); `not connected` and exit 0 when a side cannot be reached.
2. `docs.py`: `sync` calls `milestones.sync` after `audit.sync` (a few lines); the usage text names `milestones:TITLE=repo|source`.
3. `dev/toy/test-milestone-sync.py` on a fake gh, reader and writer (env hooks, throwaway repo): a change from the repo side, a change from the source side, a
   conflict, a repo with no source (no output, the fakes are never called), titles holding `:` and `=`, a first run, a not-connected side.
4. `.loop/regression.tsv` rows (linked to DOC-17, so the Documentation Tests table changes in the same commit and the page is never stale), each seen red with
   `regression.py red`; one row greps the scripts for a page URL or a 32-hex id (none may appear).
5. Command reference: `skills/workflow-docs/SKILL.md` Command map row and `references/commands.md` entry for the milestone form of `docs.py sync`.
6. Size and package: every touched file at or under 19,000 bytes, the package at 98 files or fewer (package gate row), docs check clean.

## DOC-17 wording for the owner (not applied until their words)
Owner sentence: "Un-review the Documentation page and DOC-17 so a sub-bullet for milestone sync can be added to DOC-17 as drafted, then review them again."
Sub-bullet, appended last under DOC-17:
- A repo can keep its GitHub milestones in step with an external Milestones page the same way, opt-in by setting `milestones_source` (a `url:` or `mcp:` source) in `.loop/config.json`: `docs.py sync` compares each milestone by its title, state and due date with what both sides last agreed on, an addition or change on either side is a delta reviewed and accepted with `docs.py sync --accept milestones:TITLE=repo|source`, a milestone that differs on both sides is reported as a conflict and never overwritten, and a repo with no `milestones_source` is never visited and raises no signal.

## What could break
The PRD sync (DOC-17's rows must stay green); `--open` printing a delta twice; a stale `milestones:` ledger row showing for a repo that dropped its source (filtered);
a title with `:`, `=` or `|`; gh returning 30 items by default (per_page=100 and --paginate).

## Out of scope
Deleting a milestone on either side (closing only, through an accepted delta); issues or labels; any Notion page, id or repo name in the template (only the opted-in repo's config).
