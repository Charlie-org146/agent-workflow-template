# ext-two-way: design

## Problem
`docs.py sync` (external-sync, v0.28.53) treats the external document as the only author: it rewrites the repo's copy
to match. The owner wants both sides writable: an agent's goal edits a requirement in the repo copy, people edit it in
Notion, and the two must always say the same. A difference must be reviewed, never silently overwritten, and the
agent may write accepted text into Notion.

## Approaches
1. Two-way auto-merge (last writer wins). Cost: small. Risk: it overwrites a person's or an agent's edit with no
   review; the owner ruled that out. Rejected.
2. Three-way compare with an agreed baseline, a DELTA per difference, review through an issue and a Notion comment,
   and writes only on an explicit accept. Cost: a baseline file per page, a writer hook, a small delta ledger. Risk:
   code size (audit.py has about 4 KB of room under its 20 KB cap, the package is at its 98-file cap) and the writer
   being an agent's connector that a script cannot sign in to. Chosen.

## Chosen
- Baseline: `.loop/prd/<Page>.base` holds `ID<TAB>sha8` of the text both sides last agreed on. The repo copy,
  `.loop/prd/<Page>.md` (marker line, then `- ID: text`), is editable by an agent's goal. First sync with no copy adopts the
  source (no delta). A difference per ID is a DELTA whose side is decided against the baseline: only the repo changed,
  only the source changed, or both (also when there is no baseline).
- `docs.py sync` prints `DELTA PAGE: ID <side> changed (repo: ... | source: ...)` and overwrites neither side.
  `--dry-run` posts and writes nothing and exits 1 with deltas.
- Posting: each new delta is one GitHub issue on the feature's milestone (the page's Milestone line; the title found
  with `gh api`) and one comment on the external page through `$LOOP_PRD_WRITER` (a command run as
  `WRITER SOURCE comment`, the text on stdin, which is how the agent's Notion connector writes). A ledger in the git common
  dir, `loop/deltas.tsv`, remembers what was posted so a repeat posts nothing; a changed delta comments on its issue again;
  a delta that resolved itself is closed. No connector, no gh: `not connected`, exit 0, the delta stays open.
- Accept: `docs.py sync --accept PAGE:ID=repo|source`. `source` writes the source's text into the repo copy; `repo`
  writes the repo's text into the source through `WRITER SOURCE replace ID` (or `remove ID`); either updates the
  baseline for that ID only, closes the issue and drops the ledger row. A missing writer leaves the delta open.
- Signal: `docs.py sync --open` prints the ledger's open deltas, no network. health.py's docs rows run it and report
  each as a FAIL row (the Docs rule); board.py adds each as a waiting-on-you item to the board, which is the check-in.
- External-PRDs is redrafted (Unreviewed): EXT-1 either side can change it, EXT-2 a difference is a delta, EXT-3 a
  delta is reviewed then both sides agree, EXT-4 no connector never breaks the loop (old EXT-3).

## What each done line needs
1. DELTA line with page, ID, side, both texts; neither side overwritten: toy asserts on repo copy and source bytes.
2. Posting once: a fake `gh` on PATH and a fake writer record their calls; a second sync adds none; no writer prints
   `not connected`, exit 0.
3. Accept both ways: the other side changes for that ID only; the issue is closed.
4. Health and board: a fixture repo with an open ledger row gives a FAIL docs row and a waiting item.

## Open questions (recommended answers taken)
- Which label? None: the issue title starts `DELTA PAGE ID` so it is found without a label that might not exist.
- Does `docs.py check` fail on an open delta? No: it would block every merge. Health and the board report it.
