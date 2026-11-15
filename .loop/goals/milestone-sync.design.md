# milestone-sync design

## Problem
ext-two-way (DOC-17, v0.28.63) keeps a PRD in step with an external document through reviewed deltas: `docs.py sync` compares the repo's copy
and the source with what both last agreed on, posts each difference once as a GitHub issue and once as a comment on the external page, and
`--accept PAGE:ID=repo|source` writes the chosen text to the other side. Milestones have the same need (thermis keeps its milestones on an external
Milestones page) but no requirement ids, and the repo's side is GitHub itself, not a file. The owner's rule: opt-in per repo, the template code
generic, only thermis opts in, an inconsistency is reported and never overwritten silently (issue 4186).

## Approaches
1. **Teach audit.sync a second kind of page.** One engine, but audit.py is at its 20,480 byte cap (scripts-a and scripts-b are trimming the docs
   scripts to 19,000) and the engine is a 90 line function written around files on disk; threading a GitHub side through it risks DOC-17's
   proven behaviour.
2. **A new generic module, `milestones.py`, that reuses DOC-17's parts and leaves its engine alone.** A milestone becomes an `id: text` pair
   (id = the milestone's title, text = `state | due YYYY-MM-DD`), so the existing pieces work as they are: `prd.read_link` reads the source,
   `criteria.sha` and `criteria.put` write the agreed copy and baseline, `prd.out` posts through the fakeable `LOOP_GH` and `LOOP_PRD_WRITER`
   hooks, and `counting.ledger` keeps the posted deltas (key `milestones:TITLE`). Cost: one new file and about 90 lines that mirror the delta
   loop. Risk: the two loops drift; mitigated by one toy for each and by reusing the helpers.

## Chosen: 2
- **Opt-in:** `.loop/config.json` key `milestones_source`, `url:<link>` or `mcp:<server>:<resource>` (the PRD source forms). Unset: the command
  prints nothing and exits 0 (a repo with no source "shows nothing"); the template names no Notion page, id or repo, only that repo's own config does.
- **Command:** `docs.py sync` calls `milestones.sync` after the PRD pass when the key is set, with the same `--dry-run`, `--accept` and `--open`;
  the accept target is `milestones:TITLE=repo|source`. So `--open` and the check-in's delta lines already list milestone deltas.
- **Sides:** repo = `gh api repos/{owner}/{repo}/milestones?state=all` (via LOOP_GH in the toy), reduced to `title -> "state | due"`; source = the
  page's lines `- TITLE: state | due`; agreed = `.loop/milestones.md` plus its `.base` (the same sync-owned file shape as `.loop/prd/PAGE.md`).
- **Deltas:** a title on one side only, or a differing `state | due`, is compared with the agreed base exactly as DOC-17 does: the side that changed
  (repo, source or both) is named; `both` with different texts is a conflict, reported and never applied. First run adopts nothing silently:
  with no agreed copy the source's list is the baseline and the repo-only titles are reported as deltas.
- **Accept:** `repo` writes the GitHub text to the page through the writer (`replace`, `remove`); `source` creates, edits or closes the GitHub
  milestone through gh api (`POST`/`PATCH`); neither touches any other title. Never a delete: a milestone missing on one side is closed on the other
  only through an accepted delta.
- **Missing connector:** same rule as DOC-17: `not connected`, nothing changed, exit 0.
- **Size:** the new file stays under 19,000 bytes; the docs scripts it touches (docs.py gets a three line call) must have room after scripts-b.
  The package count (99 now, 98 at most wanted) must allow one more file once scripts-b lands, else the module folds into a smaller docs script.

## What each done line needs
1. `milestones.sync`, the config key, the `docs.py sync` call, `--accept milestones:TITLE=...`, delta ledger entries, issue and writer comment.
2. No key: no output, no gh call, no read. No Notion string in any script or page (a row greps for it).
3. `dev/toy/test-milestone-sync.py` on a fake gh (`LOOP_GH`) and a fake writer and reader, one case each: a change from the repo side, from the source
   side, a conflict (both sides, different), and a repo with no source; each row seen red.

## Open questions
- PENDING: DOC-17 is Reviewed and speaks only of PRDs. Milestone sync needs one sub-bullet (drafted in DECISIONS.md for the owner); the code and
  rows go in first, and the page changes only with the owner's words.
