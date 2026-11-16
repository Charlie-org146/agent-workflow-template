# settings-in-spec plan

Checked against the code: `operate.py cmd_send` (line 207) and `sessions.py cmd_send` (358), `checkin.py` (the Needs you and Coming up sections, main at 268), `docs.py cmd_check` (281), `deployments.owed` (the routines.tsv reader, line 87), `criteria.owner_words` / `deployments.owner_words` (the shared record, read from any worker), setup SKILL.md's Command map, `.loop/config.json` `criteria_max`.

## Build steps
1. `skills/workflow-docs/scripts/permissions.py` (new): `write` merges `.loop/permissions.tsv` rows into `.claude/settings.json`; `check` prints UNDECLARED, NOT WRITTEN, UNCOVERED, CONFLICT or `PERMISSIONS OK`. It reads the routine registry and the Runbook fields the way `deployments.py` does (sibling import, no new parser). `docs.py cmd_check` calls `check` (a few lines; docs.py has 1 KB free).
2. `.loop/permissions.tsv` for `health-round` and `regression-round`, written from their Runbooks' Steps and Never fields; `.claude/settings.json` written by `write`. The setup SKILL.md Command map and the Setup Usage line gain `/workflow-setup permissions`.
3. `skills/workflow-monitoring/scripts/unattended.py` (new): `sends` (add, status, reset), `loop` (created, status), `standing` (add, check) and `selfcheck`. `sessions.py cmd_send` and `operate.py cmd_send` log each send (two lines each; sessions.py has 146 bytes free, so the log call is one line and anything bigger moves into unattended.py). `checkin.py` prints one `Operation:` line under Coming up (sends, loop, standing) and a Needs you line from 16 sends or inside 24 hours of the loop's expiry.
4. Toys under `dev/toy`: `test-permissions.py` (good, undeclared, not written, uncovered, conflict, a private row refused, a foreign rule kept; each case also run against a deliberately broken copy) and `test-unattended.py` (sends count and warning and reset, loop time left and RECREATE, standing add refused in a worker and check, selfcheck's three MISSING lines, and `criteria.py review --owner-record` accepted under `LOOP_ROLE=worker`).
5. Regression rows (each seen red with `regression.py red`), one per done-line case, guarding AUT-9 and MON-18; the Tests tables re-rendered.
6. Pages: AUT-9 and MON-18 and `criteria_max` 18 are applied only after the operation session records the owner's words (the two sentences in DECISIONS.md) and I use `criteria.py unreview ... --owner-record ID`, then add the requirements and `review ... --owner-record ID`. Until then the rows are written with the goal column of the nearest reviewed requirement (AUT-8, MON-11) and re-pointed in the same change when AUT-9 and MON-18 land. Docs: Usage lines on Automation and Monitoring, `wiki.py prepare` for stale pages.
7. Merge `origin/main` before the pr step (machine-status adds MON-16, MON-17, GRD-12; if it merged first my ids stand, if not, no clash).

## Tests for the done lines
1. `test-permissions.py` rows `perms-undeclared`, `perms-not-written`, `perms-uncovered`, `perms-conflict`, `perms-private-refused`, `perms-write-keeps`.
2. `dev/toy/test-docs.sh` (the existing docs toy) asserts AUT-9 and MON-18 exist once applied; the drafted text is in DECISIONS.md before that.
3. `test-unattended.py` rows `sends-count-warn`, `loop-recreate`, `standing-worker-refused`, `selfcheck-missing`, `owner-record-worker`.

## What could break
Script size: `sessions.py` and `docs.py` sit at the 20 KB cap, so each gets one or two lines only; the new scripts stay under 18 KB. File count 95 to 97 of 99. `docs.py check` runs `check` on every repo: a repo with no `permissions.tsv` and no routines must still pass (a routine with no rows is UNDECLARED, but a repo with an empty registry passes). Windows: settings.json written with LF, UTF-8, no BOM; rules use forward slashes. A shipped `.claude/settings.json` is tracked, so a rule must hold no private path or name (the git hooks scan it).

## Out of scope
The newsletter's own rows (thermis, `newsletter-permissions`); making the app's send cap itself configurable; enforcing the permission modes (the self-check only lists); Setup requirements (Setup is full).

PENDING: the owner's words for the Automation and Monitoring un-review (apply step 6)
VERDICT: self: design checked against the code, plan covers all three done lines
DEPTH: full
STEP: done
