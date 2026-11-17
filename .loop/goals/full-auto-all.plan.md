# full-auto-all: plan

Checked against the code: `auto.why_not`, `auto.decide_all`, `auto.eta_record`, `auto.eta_rows`, `owner_rows` (skills/workflow-monitoring/scripts/auto.py);
`owner_words` (skills/workflow-docs/scripts/deployments.py); the Auto-answered block (checkin.py:167-178); `ETA`/`eta()`/GUARD_FUNCTIONS (rules.py:362-381);
`CONTROLS.update` (controls.py:359); REPORT_ONLY (file.py:44); regression rows mon11-full-auto and auto-owner-words-wait; toy case `case_mon11`
(dev/toy/test-monitoring-prd.sh:165). All exist. Byte room: auto.py 1,187, checkin.py 639, deployments.py 48, rules.py 334, controls.py checked at build.

## Build steps
1. **Red first.** Write `dev/toy/test-full-auto-all.py` (a temp repo, a worker-less run records, no model, no network) and register rows; run each
   against main's code and keep the red output, then `regression.py red`.
2. **auto.py.** Regroup WORDS into classes (destructive, money, security, private, merge) with narrowed token/key/cost/spend; rewrite `why_not`
   (kind destructive/money/security, `waiting.eta`, no recommendation, class hit, risky_paths, always-ask mark; drop the routine-only, owner-words and
   owner-answered rules); `rule_record(root)` (latest owner-words row covering `full-auto-rule`); `decide_all` fails closed with no record, sends
   `<words> (full auto, owner rule oN)`, logs the record; `standing(g, rid, slug)` for `eta_record` (AUTO line for the slug, never `an ETA change`);
   `auto_rows(root)` for the two health rules. Net bytes under +1,187 by trimming the docstring and removed code.
3. **deployments.py.** `owner_words`: a standing record counts for `unreview` for any page and any number of times; never `review`. Trim to stay under 20,480.
4. **checkin.py.** Add `(rule oN)` to each Auto-answered line (the layout line MON-5 describes is unchanged).
5. **Health.** rules.py names `auto-safety` and `auto-record` read `auto.auto_rows`; controls.py gives each a negative control; file.py REPORT_ONLY.
6. **Docs.** MON-11 wording and its How-to line, commands.md (monitoring lines 213 and 679, health rule table), the `full_auto` setting text, then
   `entry.py write` and `docs.py` render from committed data only. Un-review Monitoring and MON-11 with the owner-words record the operation session
   records; leave the token-diet MON-5/GRD-2 lines Unreviewed and untouched.
7. **Tests updated.** `case_mon11` and `test-auto-owner-words.py` follow the new rules; the two MON-11 rows' text follows MON-11.
8. **Verify by hand**, then qa, ship, `goal.py pr`; the PR body shows the token-diet requirement diff (`git diff` of the Monitoring MON-5 and
   Guardrails GRD-2 lines, token-diet's merge against its parent) with "Unreviewed, not stamped".

## Tests per done line
1. `full-auto-all-answers`: routine, owner un-review, owner row cap, owner budget answered AUTO with the o118 record and revert words; security waits.
2. `full-auto-safety-waits` plus `full-auto-safety-control`: one case per class, a destructive/money/security kind, an ETA question and an always-ask
   goal all wait; with the class guard monkeypatched away the same security question is answered (the negative control).
3. `full-auto-record-carried`, `full-auto-standing-reuse` (un-review twice with one record; review refused; an unprompted budget citation refused),
   `health-auto-rules` (both rules with controls).
4. `full-auto-no-new-file` (package file count unchanged, scripts under 20,480 bytes).

## What could break
A loose classifier answers a destructive question: mitigated by classes failing closed, the health rule over auto.log and the control. Existing rows
for MON-11 change on purpose. The size caps: any overrun is trimmed, never raised. An un-review with the standing record while the rule record is
missing is refused.

## Out of scope
MON-5 layout, review stamping, ETA moves, a new setting, a new shipped file, the other token-diet follow-ups.

VERDICT: plan: self-review against the code, design held
PENDING: none for the owner
DEPTH: full
STEP: done
