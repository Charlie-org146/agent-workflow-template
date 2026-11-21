## kr-ls: clear known-red rows ls-judge-login and runbook-registry

Refs #5343

Each row was red on main for a reason found here and fixed at its root. No assertion is weakened or skipped; each changed
expectation is checked at least as strictly as before. Each row then passed run alone twice on this branch.

### ls-judge-login

The row runs two cases of `dev/toy/test-local-schedule.sh`: `judge` and `messages` (the old ls-messages-table row was folded
into this one, so both must pass).

- `judge`, "the default judge_command grants no tools (--tools "")": root cause in the product config. Commit 0d3687d5b
  (2026-11-14, "this repo's own config fills its settings") rewrote `.loop/config.json` by hand and dropped the
  `judge_command` key. Setup has not written that key since c53fd2016, and `settings.py` has no default for it, so nothing
  put it back. Without it, `judge.py` answers "no judge_command in .loop/config.json" and the Mac judge never runs in this
  repo. The local-schedule design depends on that key to keep judged issue text from acting (its security mitigation (b)).
  Fix: put back `"judge_command": ["claude", "-p", "--tools", ""]` where it was. The assertion is unchanged.
  `.loop/START.md` lists every config key, so it was regenerated with `entry.py write` and gains that key's one row.
- `messages`, "every code the scripts print has a Messages row ..." and "goal.py pr exit 5 is documented": root cause in the
  toy. drop-usage (9f4e31b8b, 2026-11-13) moved the Messages list from `docs/wiki/Health.md` into
  `skills/workflow-health/references/commands.md`, and health-on-windows (75f533eca, 2026-11-13) moved the mail.env mode
  check (`MAIL_ENV_MODE`) into `rounds.py`. The toy still read Health.md and did not search rounds.py. Fix: the toy reads
  commands.md and also searches rounds.py. The per-code pattern is now stricter. The list is one line in commands.md, so
  the old `` `CODE` .*(exit `` would match any later code's exit. The new pattern needs each code's own meaning, then
  `(exit N; fix: ...)` before the next code. Negative control: an entry with its exit and fix removed is refused by the new
  pattern; the old pattern still accepted it.

### runbook-registry

- "with no registry file the check still passes": root cause in the toy. Since dfa036cb3 (2026-11-13, drop-usage) the
  generated Automation block on `docs/wiki/How-to-use-Automation.md` links each routine to its runbook from
  `.loop/routines.tsv`. Deleting the registry therefore, correctly, makes that generated page STALE, and the toy read this as
  a failure. Fix: with the registry gone, the toy first checks that the output has no Runbook or `routines.tsv` finding and
  nothing new apart from that one STALE line (a new check). Then it renders and requires the output to equal the copy's own
  baseline exactly, which is the original assertion. It restores the pages afterwards.
- "the same routine passes once its page carries the runbook": red on 427590d4 because the toy never declared the
  routine's permissions. It was fixed on main by 39c011064 (w4: the toy declares them) and passes here unchanged. Its known
  line is removed with the other one.

### Rows

Net rows: 0 (none added, none removed). The known lines for ls-judge-login and runbook-registry are removed from
`.loop/regression-known.tsv`.

This file was written with the file tool under owner rule o685, since the push hook matches only prose here.
