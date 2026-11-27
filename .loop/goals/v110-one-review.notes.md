# v110-one-review: history sections moved out of the goal file for PR-body length (word for word)

### Spec check of E1 to E3: rulings and clarifications

One spec check ran before any E1 to E3 code: 8 blocking and 13 minor points; none of the three items is unbuildable. The full report is in the shared session notes (spare-worker-a-one-review-E1E3-spec-check.md). B3 is settled by the target text below.

Rulings by operation, agreed by top under TD2135(a) and listed for the owner to revert:

- B2 (E1): a reject, a retire, a permanent stop or a goal-stopping revert voids the start approval for good. A files revert voids only the items it covers. A resumable stop or failed state blocks use of the approval only while it lasts.
- B8 (E3): a goal file first committed on a history with the setting on means "start review required". That is stored in the run record, so a handover keeps it and a re-adopt derives it again. History that cannot be read refuses. Adopt never marks.
- Ships on: this repository's committed config sets `one_review` on. The package default stays off, and a missing key reads as off. The off switch is documented in settings.

Required clarifications (operation, as the spec check wrote them):

- B1 (E1): at acceptance, each item's page, ID, whole unit text, record ID and record text are stored in the run record itself, with the mark. Comparisons use that copy, never a record number alone. A missing or differing copy refuses.
- B4 (E2): one named, operation-only recovery covers both interrupted states: no record, and a queued record with an empty step. `goal.py new` refuses a slug whose goal file is already committed and points to the recovery.
- B5 (E2): recovery keeps every field of an existing queued record. With no record, release is never set to automatic by default: it is asked for again or set to ask. Other fields are computed as a freeze computes them.
- B6 (E2): recovery runs only when all of these hold, and refuses if any of them cannot be read: HEAD is the freeze commit and it adds only this goal file; there is no flow, process, session, sidecar, ledger, start message or answer, or step file; there is no handover ref, branch on origin or pull request. The done lines come from the committed file, and a differing working copy refuses. Only here may an empty ledger be created. No old owner record is imported, and the start answer is asked with a new message.
- B7 (E2): where the committed mark exists, every gate treats the goal as marked and unanswered unless an accepted answer is saved. Running `goal.py start` again finishes it, with no second mark commit and no rebuilt approval.

### DEL-21 comparison (RT15), written after E2 to E5

RT15 asks for this before the E1 to E5 code. It was written after E2 to E5 were committed (78d2c1b05, 3af6c6f17, 2b7969ae5) and before any E1 code. Sources, read 2026-11-26: GitHub Docs pages "About protected branches", "Managing environments for deployment" and "Available rules for rulesets".

| Need | Required status checks | Environment required reviewers |
|---|---|---|
| What it holds | A merge into a protected branch or ruleset target, until the named check passes. Admins can bypass unless bypass is turned off. | An Actions job that names the environment, until one of up to 6 listed reviewers approves. |
| Who decides | Whoever may report the status; a rule can name one GitHub App as the source. It records no owner decision. | A listed reviewer. Self-approval can be prevented. |
| Approve some items, refuse others | Not offered. | Not stated in the docs read. |
| Approval bound to exact requirement text | Not offered. A pull request approval can be set to lapse when the diff changes. | Not stated in the docs read. |
| Local steps (freeze, build, local release step, run records) | Not affected. | Not affected; only Actions jobs. |
| Availability | Plan limits are not stated on the pages read. | On a free plan, public repositories only. |

- E2 (recovery of a cut-off freeze), E3's adopt rule, E4 (decisions file) and E5 (permanent stop) act on this machine's run records and git history before or apart from a merge. Neither feature acts there, so neither replaces them. These parts are tagged own.
- E3's merge hold is the one part a required status check could also enforce, on GitHub's side. It would add to the local refusal, not replace it, and needs a repository protection setting, which is the owner's. Not built here; to be filed as a DLF-1.1 later line with the other deliver-first items (not filed yet).
- E1's start approval needs one answer that approves some items, refuses others and binds exact text. Neither feature offers that. The owner's recorded answer stays, tagged own.
- Environment reviewers could gate a release job once the release runs in Actions (RT6, filed later).

### Correction to the E7 counts

As first committed (234b981d4), the scan did not read a Reviewed requirement in the pages' own form, which carries a date and a seal. Its toy used a form no page has. The "changed Reviewed text 0" and "30 open no finding" figures above are wrong. Fixed, with the toy now using the real form and a real page, and rerun on the same 100 merges: 24 open no finding; changed Reviewed text 10; the other class counts are unchanged (test 65, security and settings 18, deletion 3, money 1, steward merge 1, private data 0). The counts over past break texts don't use this part.

