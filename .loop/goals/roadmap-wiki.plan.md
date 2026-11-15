# roadmap-wiki plan

Checked against the code: `skills/workflow-monitoring/scripts/batch.py` has `read_queue`, `fields`, `load(slug)`, `loop_dir`, `root` and a `main`
with `add`, `start` and `status` subparsers (13 KB of room under the 20,480 byte cap); `.loop/docs.tsv` maps a page to paths and a page that holds
`<!-- workflow-docs guide -->` is "mapped and kept fresh, but not a feature page" (pageformat.GUIDE); `docs.py publish` publishes every mapped page
that exists; Tests rows link to a requirement id a page has (DOC-11 Safe publish, DOC-13 Same answer every time, MON-4 where things stand).
The package is at 99 of 99 files, so there is no new script file.

## Build steps
1. `docs/ROADMAP.md`: keep the history sections; replace "## V1" with "## v1.0.0" holding seven `###` group tables (size caps, Windows-safe,
   regression trust, open defects, adoption, Unreviewed requirements (generated, a one-line note), package rules) with rows
   `| #N or `slug` | outcome | blocks | | |` taken from the 2026-11-14 triage, and a `## Rollout` section (the four migrate-* goals, in parallel).
2. `batch.py roadmap [--live] [--out FILE]`: parse the group tables; fetch open issues with `gh issue list --state open --limit 1000 --json
   number,title,milestone` (--live; the toy sets `GH` to a fake gh); drop a `#N` row whose issue is not open; status = "in flight" when a running
   run record's slug is in the row (or `slug` row's record is running), "queued" when queue.md lists it, else "open"; list every open issue on a
   `Backlog: *` milestone under "after v1.0" (grouped by milestone); list "To-do:" issues as off-machine to-dos; list running goals as in flight;
   read Unreviewed requirement lines from `docs/wiki/*.md` (`- ID: **Unreviewed** text`) per page with a one-line summary. Priority is empty.
   Page opens with the guide marker and a generated note. Without --live it prints and writes nothing.
3. `.loop/docs.tsv`: `Roadmap<TAB>docs/ROADMAP.md`; build and commit `docs/wiki/Roadmap.md`; a SKILL.md Command map row and a `roadmap` entry in
   `references/commands.md`.
4. `dev/toy/test-roadmap.py` and `.loop/regression.tsv` rows, each seen red with `regression.py red`.
5. Co-commit page changes (Monitoring and Documentation Tests tables) with the code so no page is stale; run docs check, package gate, toys.

## Tests (one row per done-line claim, seen red first)
- `roadmap-closed-drops` (MON-4): a closed issue's row is not in the page. - `roadmap-status-values` (MON-4): in flight, queued, open.
- `roadmap-backlog-apart` (MON-4): Backlog issues sit under "after v1.0", not in a group. - `roadmap-priority-empty` (MON-4).
- `roadmap-page-fresh` (DOC-13): the committed Roadmap.md equals a fresh offline render of the same inputs (guide marker, mapped in docs.tsv).
- `roadmap-publish-owns` (DOC-11): docs.py publish --dry-run lists Roadmap.

## What could break
batch.py grows past 20,480 bytes (budget: about 4 KB added); the guide page trips a format rule (the toy builds a throwaway repo with one); the
Monitoring or Documentation page goes stale (co-commit); a live gh page differs from the committed one, so the committed page is only ever built
from the toy's fixed inputs by the offline test and rebuilt with --live at ship.

## Out of scope
Setting priorities (the owner's column); closing or moving any issue; a requirement for the roadmap (needs the owner's words); the rollout goals themselves.
