# blockers-first design

Problem: the check-in's Needs you lists what the owner must do but not what each item holds up, so the owner cannot tell the priority (#4040).

Approaches:
1. Rank in `graph.rank` (pure, testable): follow the goals waiting on each item's goal, say what it holds up with a count and whether it is on the critical path, sort most-blocking first, and have the Stop hook refuse an unranked reply through `checkin.unranked`. Cost: small code in graph.py and checkin.py; reply_hook.py gains only a call (it is at its size cap).
2. Make the operation session add the lines by prompt only. Rejected: the hook is how MON-5 is enforced.

Chosen: 1. The graph shows an `owner item: #N slug needs you` line per repo block. The requirement text goes in DECISIONS.md (MON-19) because the Monitoring page is Reviewed; the row is tied to MON-5 until the owner reviews it.
