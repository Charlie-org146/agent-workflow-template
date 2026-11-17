# full-auto-all: design

## Problem
`auto.py pass` answers only a waiting question whose kind is `routine`. A kind `owner` question (un-review, a row cap, a
budget, a pre-flight list) waits under Needs you even with a recommendation, and a question that asks for "owner words"
waits by regex (#4287), and a goal the owner answered once is never auto-answered again. Owner rule o118 says full auto
takes every non-safety recommendation, so tonight's stalls (token-diet at build, three budgets) must not recur. The owner
records that unblock those answers are single use (`criteria.py unreview --owner-record` and `eta_record` refuse a used
record), so the operation session re-records o118's words once per goal (o119, o124, o125).

## Approaches
A. Widen the kind gate only (let `owner` through, keep the risky-word list). Small, but "token" and "cost" in the word list
   still hold every budget question, the owner-words regex still holds every un-review, and the answer a worker then
   needs (an owner record) is still single use: the goal stalls one step later.
B. Classify by safety class, answer everything else, and make the standing rule itself the reusable record (chosen).
   Costs a rewrite of `why_not`, two small reuse rules and two health rules; risk is a classifier that is too loose.
   Mitigated by failing closed: a missing rule record, an unknown class hit or an always-ask mark all wait.

## Chosen design (B)
1. **Standing rule record.** The operation session records the owner's o118 words once per machine with
   `sessions.py owner-words TEXT --ids full-auto-rule` (the existing command; no new setting, no new file). `auto.py`
   finds the latest row covering `full-auto-rule`. With none, every decision waits with "no standing owner rule recorded"
   (fail closed). Each AUTO line in `auto.log` ends `owner rule oN`; the answer sent to the worker reads
   `<words> (full auto, owner rule oN)`, so the worker cites oN.
2. **Who waits (`why_not`).** full_auto off; kind destructive, money or security; the ETA choice (`waiting.eta`: o115
   makes it the owner's); no recommendation among its words; a named safety class in the question or answer
   (destructive, money, security, private data, steward merge: one regex per class, so the reason names the class); a
   `risky_paths` match; an always-ask mark (an owner-words record covering `always-ask:<slug>` or `always-ask:*`).
   Everything else is answered whatever its kind (routine, owner, none given). Removed: the kind-must-be-routine rule,
   the owner-words regex and the owner-answered-before rule. The word list is regrouped by class, with "token", "cost",
   "key" and "spend" narrowed to their secret or money senses so a token budget is not a secret.
3. **Reusable standing record, only in the safe direction.** `criteria.py unreview --user --owner-record oN` accepts a
   standing record for any page and any number of un-reviews (un-reviewing only lowers a lock; the page shows Unreviewed
   until the owner reads and stamps it). `review` never accepts it: stamping stays the owner's. `eta_record` (a budget
   raise, a pre-flight answer) accepts it for the goal when `auto.log` holds an AUTO line for that slug, so a worker cannot
   cite it unprompted. An ETA move never accepts it.
4. **Un-review no longer blocks.** MON-11's wording says so; a goal that changes requirement wording un-reviews with the
   standing record and goes on, the owner reads it later.
5. **Visible and revertible.** The check-in's Auto-answered block adds `(rule oN)` to each line beside the existing revert
   words; the email takes the same lines.
6. **Enforced, not documented.** Two health rules read `auto.log`: `auto-safety` (FAIL: an AUTO line whose question hits a
   safety class) and `auto-record` (FAIL: an AUTO line without a rule record that exists), each with a negative control in
   controls.py. Regression rows: answers (done line 1), safety waits plus a negative control that removes the guard and
   sees a security question answered (done line 2), record carried and reuse rules (done line 3). Rows are seen red
   before the fix.

## What each done line needs
1. `test-full-auto-all.py` builds a temp repo with three waiting questions (routine, owner un-review, owner row cap, owner
   budget, security) and runs `auto.py pass`: the first answers are logged AUTO with the record and revert words, the
   security one stays waiting.
2. Safety class cases (one per class, plus kind and always-ask) wait; guard removed (monkeypatched) answers them.
3. `auto-record` and `auto-safety` rules with controls; `eta_record` and `unreview` reuse rules proved with a worker role.
4. No new file; auto.py, deployments.py, criteria.py, rules.py, controls.py and checkin.py all stay at or under 20,480
   bytes (auto.py has 1,187 bytes of room, so the rewrite removes more than it adds). The PR body carries the token-diet
   MON-5 / Guardrails / Monitoring diff, unstamped.

## Decisions taken by recommendation (o118)
- ETA choices stay the owner's (o115). Recommended; no safety question.
- A standing record is looked up by covered id, not by a hard-coded oN, because owner-words.tsv is per machine.

## Open questions
- PENDING for operation-pc, not the owner: record the o118 words with `--ids full-auto-rule` on each machine, and record the
  words covering Monitoring and MON-11 (and any Guardrails lines this goal edits) so this goal can un-review them before the
  rule it ships exists.
