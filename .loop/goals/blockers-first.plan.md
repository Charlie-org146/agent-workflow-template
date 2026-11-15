# blockers-first plan

1. `graph.rank` (graph.py): holds-up closure over the waits_on and queue edges, critical path = a live goal is held, sort most first. Confirmed against checkin.render's needs list.
2. `checkin.render`: rank the needs, number them, and add the owner-item lines to Dependencies (the graph is inserted after Needs you is ranked).
3. `checkin.unranked` and its call in `reply_hook.left_out`: the hook refuses an item that does not say what it holds up and an unsorted list.
4. Toy `dev/toy/test-blockers-first.py`, row `blockers-first` seen red; reply-hook toy fixtures say `[blocks nothing]`.
5. DECISIONS.md carries the MON-19 wording and the owner's two sentences; Home mentions the ranking.

Could break: an existing check-in text assertion; only the item text got a suffix. Out of scope: editing the Monitoring page.
