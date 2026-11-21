# Clear known-red rows ls-judge-login and runbook-registry (#5343) (Operation TD596): each row fails on main today for a reason this goal finds and fixes at its root, in the product or in the toy, without weakening any check; each row then passes on this branch run alone twice, and its known line is removed in this goal. Refs the issues the known list names for these rows

- Slug: kr-ls
- Touches: skills, dev/toy, .loop/regression.tsv, .loop/regression-known.tsv, docs/wiki
- ETA: 255 active minutes (estimate 204m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given each of the rows ls-judge-login and runbook-registry (#5343), then it passes on this branch run alone twice outside any sandbox, with its root cause named in the pull request body
2. Given each fix, then no assertion is weakened or skipped, any changed expectation is checked at least as strictly, and the nearest toys for every touched script pass as on main or better
3. Given this goal's diff, then the known lines for ls-judge-login and runbook-registry (#5343) are removed from .loop/regression-known.tsv, only the scripts, toys, rows and pages the fixes need change, the docs check passes and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## PR notes

Refs #5343

Root causes (details in .loop/goals/kr-ls.pr.md):

- ls-judge-login, case `judge`: 0d3687d5b (2026-11-14) rewrote this repo's `.loop/config.json` by hand and dropped
  `judge_command`. Setup has not written it since c53fd2016, so nothing restored it, and the Mac judge here had no command,
  including the tool-less default the design relies on. Fixed by restoring `"judge_command": ["claude", "-p", "--tools", ""]`.
  .loop/START.md was regenerated (`entry.py write`) and gains that key's row.
- ls-judge-login, case `messages` (folded in from ls-messages-table): drop-usage (9f4e31b8b) moved the Messages list from
  docs/wiki/Health.md into skills/workflow-health/references/commands.md, and 75f533eca moved the MAIL_ENV_MODE check into
  rounds.py. The toy still read Health.md and did not search rounds.py. It now reads both, and the per-code pattern is
  stricter: each code needs its own meaning and `(exit N; fix: ...)`.
- runbook-registry, "with no registry file": since dfa036cb3 the generated Automation block links routines to their runbooks
  from `.loop/routines.tsv`, so removing the registry correctly makes How-to-use-Automation STALE. The toy now checks that no
  runbook or registry finding appears and that STALE is the only new line, then renders and requires the exact baseline.
- runbook-registry, "the same routine passes once its page carries the runbook": fixed on main by 39c011064 (the toy declares
  the routine's permissions). It passes unchanged.

Net rows: 0. Both known lines are removed.
