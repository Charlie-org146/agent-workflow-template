# Plan: audit-pr-head

1. dev/toy/test-audit-pr-head.py (fix, stale) and dev/toy/test-new-binds.py (in, out), seen red first (done).
2. wiki.py `pending` audits the head's tree in a temporary worktree (+358 bytes, 19,024).
3. fit.py `bind_here`, called by goal.py new after FROZEN; trimmed goal.py comments and a fit.py note to stay under the cap (fit 20,461, goal 20,428).
4. Three defect rows (4208 x2, 4257), Tests tables re-rendered.

What could break: a leftover worktree (removed in a finally); bind refused outside the goal worktree (it prints the refusal; the goal stays frozen). Out of scope: reviewed wording, other callers of docs audit.
PENDING: none

## Full-depth plan review (claims checked against the code)

- `wiki.pending(top, cfg, fix=False, head="HEAD")` exists in wiki.py and is the only caller path merge.py uses (merge.py passes `head="origin/<branch>"`); `prepare --commit` calls it with `head="HEAD"` and keeps auditing the checkout, unchanged.
- `release.docs_trouble(top, base, whole=True)` runs `docs.py audit --base "" --dry-run` with `cwd=top`: docs.py takes its tree from the cwd's git top level, so pointing cwd at a detached worktree of the PR head audits the head's pages with main's checker. Verified by the toy: the same repo, checkout on main, gives pass for a head that fixes B and a refusal for a head that stales A.
- `audit.own_split(..., head="HEAD")` in the worktree compares the head with origin/<base>; a head already merged into the base returns every STALE unchanged (main's own run), so a re-run after the merge keeps its old meaning.
- Cleanup: `git worktree remove --force` in a `finally`; if `worktree add` fails, the audit falls back to the checkout (the old behaviour), never a pass by default.
- Risk, a stale local ref when the fetch fails: same as before the change (the fetch was already there).
- #4257: `fit.bind_here` runs `sessions.py bind SLUG self` only when CLAUDE_CODE_HOST_SESSION_ID is set and sessions.py is installed beside delivery; a refusal (session busy, folder outside the worktree) is printed and the goal stays frozen, which is today's state, so it can't make anything worse.
- Sizes checked on the staged blobs: wiki.py 19,024 (+358), fit.py 20,461 (+371), goal.py 20,428 (-40).
