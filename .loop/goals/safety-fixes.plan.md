# safety-fixes plan

Claims checked against the code: `routing.py` runs the agent with `subprocess.run(..., timeout=)` in `cmd_build` (line
~224) and in `ask` (line ~303); `proctree.kill` (killpg / taskkill /T) is already imported there; `settings.py:77` holds
`("full_auto", REPO, True, ...)`; `auto.py:77` reads `cfg.get("full_auto", True)`; `.loop/config.json:40` holds
`"full_auto": true`; `settings.md`, Home and README print the default from `settings.py`.

## Build steps
1. `routing.py`: add `tree_run(argv, stdin, limit, cwd=None)` (Popen with `start_new_session=True`, `communicate(timeout)`,
   on `TimeoutExpired` `proctree.kill(child.pid)` then drain and re-raise; returns a CompletedProcess). Replace both
   `subprocess.run(..., timeout=)` calls with it. Stay under 19,000 bytes (now 18,826).
2. `settings.py`: `full_auto` default `False`, help text "false (the default) keeps every gate; true lets ..." and the
   same size or smaller (the file is already over 19,000, so it must not grow).
3. `auto.py:77`: a missing key is off (`cfg.get("full_auto") is not True`); fix the docstring's "on by default" and the
   "on by default" in `references/commands.md` (MON-11 prose in Monitoring.md is not touched: it is a requirement line,
   listed in the PR under Needs owner review).
4. Regenerate `references/settings.md` (`settings.py reference`) and the Home and README settings tables
   (`docs.py render`); `.loop/config.json` keeps `full_auto: true`, so Home shows it as overridden.
5. Tests: in `dev/toy/test-agent-routing.py` add one check: a fake agent starts a grandchild and sleeps; `routing.ask`
   with limit 1 returns a failure and both pids are gone (`proctree.probe`). One new row `routing-timeout-tree` runs that
   check. In `dev/toy/test-settings.sh` add one `check` line (full_auto reference default false, this repo commits true);
   fold it into an existing row by extending that row's grep, so no row is added. Run `regression.py red` for the new row
   (the old `subprocess.run` leaves the grandchild).
6. Any toy that asserts full_auto defaulting on (grep) is updated, not given a new row.

## Done-line tests
1. `routing-timeout-tree` (seen red with the old call, green now). 2. the extended settings row. 3. row count +1, byte
check, `git diff --stat` shows no new file.

## Could break
`tree_run` changes output handling: text mode with UTF-8 and `errors=replace` as before; stdin pipe only when the profile
sends the prompt on stdin. Windows: `start_new_session` is ignored there and `proctree.kill` uses taskkill /T, the same as
the flow steps. An older adopted repo with no `full_auto` key now has full auto off (intended).

## Out of scope
Rewording MON-11 or any Reviewed requirement; other repos' configs; the Mac's open goals.

PENDING: MON-11 says "A setting, on by default": owner review of that wording (listed in the PR, not edited)
DEPTH: full
