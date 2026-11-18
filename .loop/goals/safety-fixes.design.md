# safety-fixes design

## Problem
`routing.py` runs a routed agent with `subprocess.run(timeout=)` (the build, and `ask` for the plan cross-check). On a
timeout that kills only the direct child, so the agent's own children keep running, against the rule that a step stopped
for a timeout loses its whole process tree. Separately `settings.py` defaults `full_auto` to true, so a repo adopted from
the template starts with the operation session answering decisions, against the README promise that an adopted repo
keeps every gate until its owner turns one off (o146, template o39).

## Approaches
1. Fix 1: one helper in `routing.py`, `tree_run`, starts the agent with `Popen(start_new_session=True)` and, on a
   timeout, calls `proctree.kill` (killpg on POSIX, taskkill /T on Windows) before it re-raises; build and `ask` both use
   it, so the file shrinks a little (it has 174 bytes of room under 19,000). Alternative: add the helper to
   `proctree.py`; rejected, it is one identical copy in three skills and none has room.
2. Fix 2: change the default to false in `settings.py` and its help text, regenerate the settings reference and the
   Home/README settings tables (`docs.py render`), keep `full_auto: true` in this repo's config. Also `auto.py` reads a
   missing key as on (`cfg.get("full_auto", True)`): change it to off, otherwise an older adopted repo with no key stays
   on. Alternative: leave auto.py; rejected, the default would still be on in practice.

## Chosen
Both approach 1s above. Tests: one new row `routing-timeout-tree` (net +1) whose check lives in the existing
`test-agent-routing.py` (no new file): a fake agent starts a grandchild and sleeps, `routing.ask` times it out at 1 s, and
both pids are gone (`proctree.probe`). The `full_auto` default is folded into the existing settings row by a new `check`
line in `test-settings.sh` (no new row): the reference shows `false`, this repo commits `true`.

## Done lines
1. The new toy check, red before (the old `subprocess.run` leaves the grandchild), green after.
2. The settings toy line, plus the regenerated reference and tables.
3. Row count +1, scripts under 19,000 bytes where they are now, no new file. MON-11 says "on by default": not reworded, listed
   in the PR under Needs owner review.

## Open questions
None. MON-11's wording is the owner's to review.
