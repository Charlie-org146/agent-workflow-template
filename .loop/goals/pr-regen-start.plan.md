# Plan: pr-regen-start

1. fit.py: tool() path helper (used by nag, bind_here, monitor), regen(g, slug).
2. goal.py: call fit.regen after bump_version; trim bytes to stay under main.
3. dev/toy/test-goal.sh: stale START.md before pr (control), pr commits "Regenerate START.md", second pr adds no commit.
Checked by hand in a scratch clone: STALE before, ENTRY OK after, wiki pages committed.
Sizes (LF): goal.py 18,989 (main 18,999), fit.py 19,824 (main 19,827). Net rows 0. Out of scope: merge.py, wiki.py, requirement text.
