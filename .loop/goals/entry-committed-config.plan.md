# Plan: entry-committed-config

Checked against the code: `config(root)` in `skills/workflow-docs/scripts/entry.py` (line ~56) is the one reader of `.loop/config.json`
for `render`, `write`, `check` and `block`; `merge.py`'s stale check runs `entry.py check`. `subprocess` is already imported.

## Steps
1. `config(root)`: if `git ls-files -v -- .loop/config.json` (cwd=root) starts with `S`, parse `git show HEAD:.loop/config.json`;
   any failure falls back to the working copy. Net-zero bytes in `entry.py` (main is 19,337, over the cap): trim wording elsewhere in the file by the bytes added.
2. New `dev/toy/test-entry-config.sh` (dev/, not shipped): in a temp git repo with committed `min_free_memory_gb` 3.0, set 2.0 in the
   working copy and `git update-index --skip-worktree`; run `entry.py write` then `entry.py check`. Expect 3.0 in START.md, `ENTRY OK`.
   Negative controls: without skip-worktree the 2.0 edit renders (ordinary edits unchanged); a git-less dir reads the file.
3. One `land` regression row `entry-committed-config` for the test, seen failing on main's `entry.py` before the change.
4. Documentation page: one sentence under the entry-point requirement stating the rule, marked Unreviewed with the new wording going to the owner.

## Review changes (red-team pass)
- Mirror `counting.py` `config_of` (lines 258-266), which already does skip-worktree then `HEAD:`; test its flag as `S` or `s` (any flag char in `Ss`).
- Always run git with `cwd=root`; the test calls `entry.py write --repo TREE` from an unrelated cwd.
- Test in a linked worktree (`git worktree add`), where the per-worktree index carries the flag.
- Extra negative controls: skip-worktree set but file absent from HEAD, and invalid JSON from `git show`, both fall back to the working copy.
- "Seen failing": the test takes an `ENTRY` env override so it can run against main's `entry.py` (`git show origin/main:`) first.
- Byte check: assert `entry.py` is no larger than main's size after the change.
- The merge path is `wiki.own_entry` -> `entry.py check --repo TREE`; the test runs `check` the same way.
- Unreviewed marking: the Documentation page's changed requirement text is stamped Unreviewed by the docs tooling, and the PR body asks the owner to review it.

## Done line coverage
1 -> steps 1-2 (3.0 shown, check passes). 2 -> steps 3-4.

## Could break
`git` absent or not a repo: falls back. Bare worktree where `ls-files` prints nothing: falls back. Windows path with CRLF: JSON parse unaffected.

## Out of scope
Other config readers (setup, settings), a shipped new file, any budget or size cap change.

PENDING: none
