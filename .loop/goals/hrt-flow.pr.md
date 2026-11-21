# hrt-flow: bring six toys up to current behaviour

Issues: #5652 #5654 #5678 #5667 #5677 #5681. Only the six toys changed; no product script, regression row, known list or setting.
Every toy was run alone, one at a time, outside the sandbox, from a Claude app session (so `CLAUDE_CODE_HOST_SESSION_ID` was set in the
environment, the way the owner's runs were). No product bug was found.

| Toy | Before (exit, FAIL lines) | After (exit, FAIL, wall seconds of the final green run) | What changed |
|---|---|---|---|
| `dev/toy/test-budget.sh` | 1, 3 | 0, 0, 21 s | Hermetic env |
| `dev/toy/test-tokens.sh` | 1, 4 | 0, 0, 10 s | Hermetic env |
| `dev/toy/test-status-graph.sh` | 1, 1 | 0, 0, 10 s | Hermetic env |
| `dev/toy/test-wiki.sh` | 1, 8 | 0, 0, 39 s | Hermetic env |
| `dev/toy/test-milestones.sh` | 1, 1 (2 in the sandbox) | 0, 0, 31 s | Hermetic env; setup-milestone check follows the new opt-in key |
| `dev/toy/test-delivery-prd.sh` | 1, 9 (28 in the sandbox) | 0, 0, 149 s | Hermetic env; owner-record on a budget raise; per-goal touches in the private-name section |

## What drifted

1. All six: `goal.py new` now binds the new goal to the running app session when `CLAUDE_CODE_HOST_SESSION_ID` is set (#4257, `fit.bind_here`),
   so every step then runs "in session" (`flow.py` prints `IN SESSION ...` and waits for a reply) instead of through the toy's headless stand-in
   skill. The toys never cleared that variable, so they were green in a plain shell and red inside a Claude session. Each toy now unsets it next
   to its existing `unset LOOP_SESSION_TOOL ...` line. Nothing is weakened: no assertion changed for this; the toys now test the headless
   path whatever session runs them. `dev/toy/test-new-binds.py` already proves the binding itself.
2. `test-milestones.sh`, first check: setup now writes the opt-in key `milestones_source` (empty, off) into `.loop/config.json`
   (`55e0d2d25`), so "no tracked file contains `milestone`" can no longer hold. The check now strips only the exact empty key
   `"milestones_source": ""` and still requires no other mention in setup's output or any tracked file, and also requires the key to be
   empty. Two negative controls were added: a non-empty `milestones_source` and any other `milestone` text are not hidden by the filter.
3. `test-delivery-prd.sh`, budget: raising a goal's budget with `goal.py set` now needs an owner-words record that covers the goal, used once
   (`ETA_NO_RECORD`, `de7649c3d`). The old check (one `set`, then read `extra.json`) is replaced by: a raise with no record is refused and writes
   nothing (new negative control); the raise on a record that covers the goal writes the 5000 tokens and names the record (the old check plus
   the record); the same record cannot raise it again (new negative control). The worker-refused and no-budget checks are untouched.
4. `test-delivery-prd.sh`, private-name section: goals with overlapping touches now take turns at `goal.py pr`, and a goal refused for a
   private name keeps its place in the queue, so every later `prgoal` sharing `src/api` printed `WAITING pr queue` and never reached the
   scan. Each `prgoal` now touches its own path (`src/<slug>`), so each goal is scanned. All assertions in the section are unchanged
   and also fixed the two later `#38` checks that failed behind the same queue. Observation, not asserted as a bug: a refused goal holds its
   queue place until its heartbeat lapses (1800 s) or it leaves `pr`; that is the queue's documented ticket rule, left as is.

## Why each changed assertion is at least as strict

- Items 1 and 4 change the fixture only; every assertion text is unchanged.
- Item 2 keeps both original conditions (setup output has no `milestone`; no tracked file has it) except the one empty key, and adds the
  empty-value check and two negative controls.
- Item 3 keeps the original outcome check, adds the record check, and adds two refusals.

## Sandbox note

The earlier Codex attempt ran inside a sandbox that refused `ps` (exit 77 from the reap helper), so its numbers differ; the before counts above are
from this run, outside the sandbox, with the session variable set.

## Required checks

`docs.py check`, `criteria.py render --check` and `dev/package.py --static` pass on this commit (see the final report).
