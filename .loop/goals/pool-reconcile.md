# Restart-safe item 2 (TD487, TD489): pool.py reconcile matches session-pool.json against the app's real session list, which only the operation session can read, so the operation session writes it to a file the reconcile reads. Ids the app no longer has are dropped from the pool (never deleted from the app), and health gets a ghost-count row. Net-zero files: the code goes in pool.py (18,806 B), no new file, no reformatting

- Slug: pool-reconcile
- Touches: skills/workflow-monitoring, dev/toy
- ETA: 470 active minutes (estimate 373m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a pool with 3 live ids and 5 ghost ids and an app-list file naming only the 3, when pool.py reconcile runs, then the 5 ghosts leave the pool, the 3 stay, and nothing outside the pool file changes, shown by a toy
2. Given ghosts in the pool, then health prints the ghost count as one row, and a toy proves 0 and 5
3. Given this goal's diff, then the package stays at 100 files, pool.py stays under 20,480 bytes, package.py --static, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
