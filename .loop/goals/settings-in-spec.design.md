# Design: settings-in-spec

Goal: `.loop/goals/settings-in-spec.md` (3 frozen done lines). Last night the health round, the newsletter and the operation session stopped for the same cause: what a scheduled routine or the operation session needs in order to run unattended lived only in machine-local settings, not in the spec. The owner's words: "I actually want it to be consolidated in the specification instead of like a custom rule or something", and "both like the service settings and also the settings regarding that you end, that the operation session won't just end."

## Problem

A: a routine's Runbook says what it runs, but nothing says what it may run, so each machine grows user-wide rules in `~/.claude/settings.json` and a fresh machine stops at the first prompt. B: the operation session stopped at 02:40 because the desktop app pauses cross-session messages after 20 sends with no owner message, one worker refused an owner-words record, and the scheduled tasks lacked their rules.

## Approaches

1. Everything in config and settings: a `routine_permissions` setting holding JSON, and counters in the check-in code. Cheap, but a JSON blob in `config.json` cannot be checked against the Runbook text, and every repo edit is a settings edit (private-settings churn).
2. A committed declaration file plus one engine per concern (chosen): `.loop/permissions.tsv` (`routine<TAB>allow|deny<TAB>rule<TAB>why`) beside `.loop/routines.tsv`, written by one sibling script into the repo's committed `.claude/settings.json`, and a check that compares the rows with the settings file and with the Runbook's backticked commands and URLs. For B, one small script `unattended.py` keeps three records under `<git common dir>/loop/` (sends, the check-in loop, standing instructions) and the start-up self-check. More files, but each rule is checkable and each repo owns its own list.

## Chosen

Approach 2. The template owns the general rule (AUT-9), the engine and the check; each repo owns its rows (a thermis newsletter row set lands in thermis, from `newsletter-permissions`, in this same format). Files: `skills/workflow-docs/scripts/permissions.py` (`write`, `check`; docs owns the registry and the Runbook parser; `docs.py check` calls `check`, and `/workflow-setup permissions` runs `write`) and `skills/workflow-monitoring/scripts/unattended.py` (`sends`, `loop`, `standing`, `selfcheck`). The package has 4 files of headroom (95 of 99), so these two are the only new files; every other change is a few lines in an existing script, because most scripts sit near the 20 KB cap.

- Rules are Claude Code permission rules (`Bash(python3 skills/workflow-health/scripts/*)`, `Read(~/.workflow-loop/**)`, `WebFetch(domain:api.github.com)`, `Bash(git push:*)` as a deny). A deny always wins over an allow in the check, as it does in Claude Code.
- `write` merges the rows into `.claude/settings.json` (`permissions.allow`, `permissions.deny`), keeps every other key and rule, refuses an unreadable file, and writes nothing private: a row with a user name, an absolute home path or a key-like token is refused.
- `check` reports `UNDECLARED <routine>`, `NOT WRITTEN <routine> <rule>`, `UNCOVERED <routine> <command>` (a program, script or domain the Runbook's Steps or Full run names that no allow row covers) and `CONFLICT <routine> <rule>`; exit 1 on any, `PERMISSIONS OK` otherwise. A repo with no routines passes.
- B counters. Sends: `sessions.py send` and `operate.py send` log each send, the operation session logs its own message-tool sends with `unattended.py sends add TO`, and an owner message resets the count (`sends reset`, called when the operation session records the owner's words or answers a Needs-you question). The check-in prints `Sends: N of 20 since your last message (M left)` and, from 16 on, a Needs-you line asking the owner for any message. Loop: `loop created` records the check-in loop's creation; `loop status` prints the time left of its 7 days and `RECREATE` inside the last 24 hours, which the check-in lists under Needs you for the operation session to act on itself. Standing: `standing add "<text>" --scope merge --goals A,B|all` (operation only) records one instruction in `standing.tsv`; a worker at pr runs `standing check <slug>` and, on `STANDING <id>`, does not wait for a per-merge go. Owner words: no code change is needed (`criteria.py review|unreview --owner-record` already reads the shared file from any worker); a toy proves it under `LOOP_ROLE=worker`, and the requirement states the rule so a worker never refuses a named record.
- `unattended.py selfcheck` lists `MISSING` lines with a fix each: the permission mode (the defaultMode of the project then user settings is `default` or `plan`, which holds cross-session messages for approval), any routine whose `permissions.py check` fails, and the main checkout behind `origin/<base>` (MON-16 asks a free worker to fast-forward it).

## Done lines

1. `permissions.py check` and `write` with toy cases good, undeclared, not written, uncovered, conflict (each a negative control), a refused private row and a kept foreign rule; `.loop/permissions.tsv` for `health-round` and `regression-round` in this repo; `docs.py check` runs it.
2. AUT-9 and MON-18 drafted in DECISIONS.md with one un-review-then-review sentence for the Automation page and one for the Monitoring page; no reviewed text is edited before the owner's words (these are new, Unreviewed requirements; the pages and `criteria_max` change only after the owner's sentences are recorded).
3. `unattended.py` with toy cases for sends (count, warning at 16, reset), loop (time left, RECREATE), standing (add refused in a worker, check), selfcheck (each MISSING line), and the owner-record toy under `LOOP_ROLE=worker`; a regression row for each, seen red first.

## Decisions

- The new Monitoring requirement is MON-18, not MON-16: `machine-status` holds MON-16 and MON-17 and GRD-12 unmerged. Monitoring then holds 18 requirements and `criteria_max` is 17, so the same change raises it to 18 (the precedent in routine-runbooks). Setup has 17 of 17, so nothing is added to Setup: its part (the command that writes the rules) is in AUT-9 and the Setup Command map.
- The drift check is in the docs check, not a health rule, because the registry and the Runbook parser are docs' and HLT-2 lists its groups exactly (a reviewed requirement). A repo can still run it as a repo rule once health-repo-rules is in.
- Sends cannot be read from the app, so the count is the operation session's own log; the warning at 16 leaves 4 sends, and any owner message resets it.

## Open questions

- Which warn threshold the owner wants (16 of 20 proposed).
- Whether the self-check should refuse (exit 1) or only list; proposed: list, exit 1 only when something is MISSING, so a scheduled start can stop on it.
