# Plan: merge-from-main-checkout
1. release.py `where(script)`; merge.py calls it after the config is read; wiki.py main calls it for publish.
2. autorelease.py `reopen(state, code)`; merge.py's HEAD_MOVED and BASE_MOVED returns go through it.
3. dev/toy/test-merge-where.py and rows merge-refuses-worktree, merge-refuses-behind, moved-exit-live-at-pr (seen red).
Out of scope: docs.py (read-only), the installed skills' age.
