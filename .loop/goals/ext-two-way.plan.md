# ext-two-way: plan

Design: `.loop/goals/ext-two-way.design.md`, approach 2 (three-way compare, deltas, accept-then-apply).

## Build steps, in order

1. Toy first, red: `dev/toy/test-docs-delta.py` builds a temp git repo with a `.loop/docs.tsv` external source (a file
   `url:`), a fake `gh` on PATH that logs its calls, and a fake `LOOP_PRD_WRITER` that logs its calls; it asserts each
   done line. Replace `dev/toy/test-docs-sync.py` (V1's rewrite-on-drift asserts no longer hold) by folding its
   cases into the new toy; keep its `PASS:` lines that still hold, reworded.
2. `skills/workflow-docs/scripts/audit.py`: replace the V1 `sync` with the three-way compare: `base_of`, `deltas`,
   `post` (gh issue create / comment through `gh api` for the milestone title; the writer for the Notion comment),
   `accept`, `opened` (the ledger, `<git common dir>/loop/deltas.tsv`). Exists today: `audit.sync`, `mirror_of`,
   `requirements`, `req_key`, `SYNC_MARK`. The file is 16.2 KB (LF) with a 20,480 hard cap: V1 sync is shrunk as it is
   replaced; no new file (the package is at its 98-file cap).
3. `skills/workflow-docs/scripts/docs.py`: `sync` gains `--accept PAGE:ID=repo|source` and `--open`; `cmd_sync` passes
   them; one usage line (20,060 bytes now, 20,480 cap).
4. `skills/workflow-health/scripts/health.py` (`docs_rows`): run `docs.py sync --open` and report each `DELTA` line as a
   FAIL row of the Docs rule (19,457 bytes now). `skills/workflow-monitoring/scripts/board.py` (`build`): each open delta
   is a `waiting` entry whose words are `accept PAGE:ID=repo` or `=source` (18,108 bytes now).
5. Redraft `docs/wiki/External-PRDs.md` (Unreviewed): EXT-1..EXT-4, Problem fixed (double space gone, third bullet says the
   agent may now write accepted text), Non-goals and Success metrics updated; `.loop/docs.tsv` paths keep `.loop/prd`.
   Relink the five V1 rows to the new ids; new rows for the new behavior, each seen red with `regression.py red`.
6. Docs the check requires: README How to use External PRDs rows, `skills/workflow-docs/SKILL.md` Command map and
   `references/commands.md` for `sync --accept` and `--open`, `skills/loop-files.md` for `.loop/prd/PAGE.base` and
   `loop/deltas.tsv`, then `criteria.py render` and `entry.py write`.
7. Verify by hand in the goal file; `package.py` size and headroom rows stay green.

## Tests (each seen red before the change)

- Done line 1: toy case "a changed requirement is a DELTA naming page, id, side and both texts; neither side changes".
- Done line 2: toy cases "a delta is posted once as an issue and once as a comment; a second sync posts nothing" and
  "no writer or no gh prints not connected and exits 0".
- Done line 3: toy cases "accept source writes the repo copy only for that id" and "accept repo writes through the
  writer for that id only", each closing the issue.
- Done line 4: toy case "an open ledger row gives a docs FAIL row in health and a waiting item on the board".

## What could break

- Script sizes (audit.py, docs.py, health.py, board.py near their caps): checked by `package.py` and the headroom row.
- V1 behavior changes on purpose (no more rewrite-on-drift): the V1 rows are replaced, not left red.
- A real Notion connector is never used by a toy; the writer contract is a documented command, not code that signs in.
- Reviewed text is untouched: External-PRDs is Unreviewed and no other page changes except generated tables and docs.

## Out of scope

Google Docs, milestones or the README as a source, auto-accepting a side, a writer that signs in by itself.

PENDING: none
