# home-leak plan

1. dev/toy/homeguard.py (snap, diff); reap.sh: LOOP_FLOW and LOOP_HEALTH temp paths, snapshot at start, diff at exit.
2. Mechanical USERPROFILE additions to the toys that set HOME (sh and py).
3. dev/toy/test-home-guard.py with a guard leg (quiet toy passes, a rewriting and an adding toy fail with LEAK) and an isolate leg.
4. Rows home-guard-catches-leak and toys-set-userprofile on DEL-?, each seen red; criteria.py render; docs.py check --own.
5. After the merge close issue 4393 by comment with the proof.

Out of scope: setting HOME for every toy in the harness; Python toys sourcing a shared guard.
Could break: a toy that relied on the real flow or health file (none found); the harness on Linux CI.
