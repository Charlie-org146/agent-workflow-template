# One review at the start: a goal asks the owner once, and no later step waits on the owner (owner o1037, o1038)

- Slug: v110-one-review
- Touches: skills/workflow-delivery, skills/workflow-monitoring, dev/toy, .loop/regression.tsv, docs/wiki/Delivery.md, docs/wiki/Deliver-first.md, docs/wiki/How-to-use-Deliver-first.md, docs/wiki/Operation.md, docs/wiki/How-to-use-Operation.md, docs/wiki/Tests.md, skills/loop-files.md, listing.json, docs/wiki/Home.md, skills/workflow-release, .loop/config.json, .loop/START.md, skills/workflow-setup/scripts/settings.py, docs/wiki/How-to-use-Delivery.md, skills/workflow-docs/scripts/deployments.py, skills/workflow-docs/scripts/milestones.py, skills/workflow-docs/scripts/criteria.py, README.md, docs/wiki/Principles.md
- ETA: 870 active minutes (estimate 694m plus a 25% margin)

## Words used

The replacement for DLF-1.3, approved with the done lines (o1038):

> DLF-1.3 **One review, at the start.** A goal waits for me once: at its start, where I approve its done lines and the safety items it is known to touch (deleting what can't be restored, money, security and sandbox settings, private data, steward merges, a change to what a feature promises, a test loosened or deleted). After that nothing waits for me. A safety item found later takes the safe option without asking: it is fixed in the build, or that part is dropped and filed as a DLF-1.1 line; nothing is waived or loosened that the start review didn't approve. The leak read before any push and the PR's reached-test run before a merge stay as automatic checks, not waits for me. Every decision made in my place is listed in the next check-in with a one-line revert.

The DEL-3 line on the Delivery page is aligned in this goal's build to this wording (operation's decision under o1037 and o1038, listed for the owner to revert):

> My decisions are made once, at a goal's start; later ones are made on the recommendation, with the safe option for safety, and listed for me to revert (DLF-1.3).

The metric becomes "minutes a goal waits for me after its start review, target 0", and the Operation page's owner-question lines change the same way.

## Done lines

Frozen. A wrong done line needs a new goal.

1. A goal asks the owner once, at its start: its done lines and its known safety items together, in one message.
2. After that start review, no step waits on the owner: readings, red-team findings and plan questions are decided by the operation on its recommendation.
3. A safety finding found later takes the safe option without asking: fixed in the build, or that part dropped and filed as a later item; a check is never waived or loosened.
4. Every such decision appears in the next check-in with a one-line revert command, and a revert stops that part.
5. Checks, leak reads and merge rules stay as they are; only the waits on the owner go.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->

## Notes

### Build order (the plan is final; TD2073, TD2127, TD2128)

E1 to E5 come first, with one spec check on E1 to E3 before their code. They are required build items.

- E1: one comparison of a whole requirement unit, sub-bullets included, of the approved text at revise, review, merge and in the requirement guard. DLF-1.3 is approved as part of the DLF-1 unit, and the other lines of the unit are checked as unchanged. A record is used once per ID and command, so two approved IDs both work. Record tags name IDs, not whole pages. The record is refused after a revert, a reject, a stop or a retire.
- E2: a freeze interrupted between its commit and its saved record can be recovered. The mark is kept, the start answer is still asked, and no approval is rebuilt.
- E3: adopt marks no goal. It refuses a goal with any sign of a mark (goal file, history it can reach, local record, handover ref) and refuses when it cannot read the history in full. Where a goal needs the mark, its start review is sent, and merge refuses until it is answered.
- E4: decisions are kept in an append-only file with its own lock, read again under the merge and revert lock, and handed over with the pre-flight and plan-review files. A missing file refuses.
- E5: a stop holds at every path that sets a goal queued or running.

The other build items are listed under Build list below.

### Rulings

- The merge and release rules the owner set stay, and the PR and the metric name them as kept owner rules, beside the metric.
- The leak read is not a build item; the automatic private-name scan stays as a filter. The DLF-1.3 text stays as approved.
- The CI release workflow file is not part of this goal and is filed as a deliver-first line; the local release step reads the holds.
- The rule ships on, with a documented off switch in settings ("on" as ruled under the spec check below: on in this repository, off by default in the package). The first goal after the merge is named the pilot and gets a red-team line on whether the one review held.
- Past the start review, a part that would need an owner-contradicting decision is dropped and filed (top's reading; not added to any page).
- Page wording approved by top under its DOC-2 delegation (TD2128), listed for the owner:
  - Delivery, DEL-3: "My decisions on a goal are made once, at its start; later ones are made on the recommendation, with the safe option for safety, and listed for me to revert (DLF-1.3)."
  - Operation, OPS-1: "**Full auto:** top decides process choices and numbers each decision. On a goal past its start review, a safety item found later takes the safe option without asking (DLF-1.3); outside that, the safety classes wait for my typed words."
  - Operation, non-goal: "Full auto never answers for me on destructive, money, security or owner-contradicting decisions. On a goal past its start review, a safety item found later takes the safe option without asking (DLF-1.3)."
  - Operation, metric: "With full auto on, a goal needs me only at its start review; the merge and release rules I set stay. Minutes a goal waits for me after its start review: target 0."
- The owner approved the DLF-1 heading and metric ("Approve both", o1045), so they no longer hold the merge:
  - DLF-1 heading: "Deliver first: a goal waits for me once, at its start"
  - DLF-1 metric: "**Metric.** Minutes a goal waits for me after its start review. Target 0."
- Revert rule, a required build item (TD2128): each decision records what it let go on, and its revert line says "stops the goal" when that is the whole goal.
- The Delivery wording above is the one top approved; it takes the place of the earlier DEL-3 draft under Words used for the page edit.
- The owner recorded two approvals in their own terminal. Nothing in this goal waits on the owner now, and the DEL-3 edit no longer holds the merge (this replaces the TD2135c hold).
  - o1048 (v110-one-review, DLF-1, Deliver-first, OPS-1, Operation): the DLF-1 revise to the TD2136 unit and the Operation page lines B, C and D rest on it.
  - o1046 (v110-one-review, DEL-3, TD2128-A): the DEL-3 edit rests on it.
  - Each record counts once per command, so each is used in one revise call.
- Order (operation): the o1047 unreview of DLF-1 runs only when v110-no-leak-gate's build starts, after this goal merges, because that goal's build and its line 4 wait for the merge. This goal's DLF-1 revise therefore starts from the Reviewed unit the TD2136 text was checked against.

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

### Target text: the DLF-1 unit

Top approved this unit under TD2136 with option K: the DLF-1.3 Metric and Test lines stay unchanged, so the part marked open below is settled. It rests on o1038, o1045, TD2128 E and F, and TD2136; its revise cites o1048. It governs over the plan's sentence that puts the approved metric under DLF-1.3. The pull request names the short window in which the leak-read clause is stale. The file is copied as written:

```
# v110-one-review: resulting DLF-1 unit (operation-mac, 17:11, TD2134 option A; for top's DOC-2 check before the worker uses it)

Base: docs/wiki/Deliver-first.md on main 7784d862f. Exactly three changes; every other line of the unit (lines 18-52) and the page is unchanged. The history row (line 76) is untouched.

1. Line 18 heading (o1045, TD2128 F):
BEFORE: Deliver first: a goal never waits for me, unless it's a safety class
AFTER:  Deliver first: a goal waits for me once, at its start

2. Line 25 DLF-1.1 metric AND line 66 under Success metrics (o1045, TD2128 E):
BEFORE: **Metric.** Minutes a goal spends waiting for my word on anything outside DLF-1.3. Target 0.
AFTER:  **Metric.** Minutes a goal waits for me after its start review. Target 0.

3. Lines 30-36, DLF-1.3's heading, its five bullets and 'Every other stop in the loop is removed or turned into DLF-1.1's issue line.', are replaced by the o1038 text, verbatim:
  - DLF-1.3 **One review, at the start.** A goal waits for me once: at its start, where I approve its done lines and the safety items it is known to touch (deleting what can't be restored, money, security and sandbox settings, private data, steward merges, a change to what a feature promises, a test loosened or deleted). After that nothing waits for me. A safety item found later takes the safe option without asking: it is fixed in the build, or that part is dropped and filed as a DLF-1.1 line; nothing is waived or loosened that the start review didn't approve. The leak read before any push and the PR's reached-test run before a merge stay as automatic checks, not waits for me. Every decision made in my place is listed in the next check-in with a one-line revert.

OPEN for top: DLF-1.3's Metric and Test lines (37-38):
  - **Metric.** Goals merged past one of these. Target 0.
  - **Test.** A goal whose only break loosens a test does not merge, and the board names that as the reason.
'Goals merged past one of these' loses its list once the bullets go. Option K: keep both lines unchanged ('these' then reads as the safety items DLF-1.3 names). Option R: reword 'one of these' to 'a safety item DLF-1.3 names', which needs your DOC-2 approval. operation-mac recommends K (says no more than o1038).

Unchanged on purpose: Non-goals line 46/60 'It never skips the leak read ...' and DLF-1.3's leak-read clause: v110-no-leak-gate line 4 deletes them after one-review merges (o1040). The PR body names that stale window (TD2134).
```

### Red-team dispositions (plan file sha1 defb36a61622)

36 breaks, named by number, principle and short id; their text is not repeated here. All 36 are accepted in the tool's record (operation: principles 1, 3, 4, 6 and 8 under o1000; 2 and 7 under o1037). In that record, accepted means the disposition below, never a waiver. REQ is a required build item, DF is filed as a deliver-first line, and PW means the break showed the plan wrong as written. All 9 breaks of principle 6 are required build items.

| break | principle | short id | REQ or DF | build item | disposition |
|---|---|---|---|---|---|
| 1 | 8 | b1p87f0ae6 | REQ (PW) | CEO B2, E6, DX D1 | the start message is sent once, after its items are final, after plan and red team and before the build (B2, E6) |
| 2 | 8 | b2p831ef23 | REQ (PW) | RT1 | a safety item names exact files or an existing folder |
| 3 | 6 | b3p667b05d | REQ (PW), build item CEO B1, E7, accepted by o1000 means a disposition, not a waiver | CEO B1, E7 | labels raise the class, and unknown stays safety (B1, E7) |
| 4 | 2 | b4p2507a43 | REQ (PW) | E14, RT18 | a fix's row is tied to the finding and was red without the fix; a fresh reader gives a verdict on the fix (E14) |
| 5 | 8 | b5p893dca2 | REQ (PW) | RT2 | a rule for ordinary test updates that loosens no check |
| 6 | 8 | b6p8f4ac32 | REQ (PW) | RT16, CEO B4 | after a merge the revert command opens a revert goal for that part, and the owner's revert command is its start review (TD2127); each decision records what it let go on, and its revert line says what it stops, "stops the goal" when that is the whole goal (TD2128, B4) |
| 7 | 8 | b7p8144c52 | REQ (PW) | RT17 | the DLF-1.4 accept list is named as a kept owner rule, in the PR and beside the metric (TD2127) |
| 8 | 1 | b8p1913e68 | REQ (PW) | RT11 | only wording approved by top or the owner lands; any other line stays as it is |
| 9 | 1 | b9p1108665 | REQ (PW) | RT5 | README and Principles are regenerated |
| 10 | 1 | b10p12ee017 | DF | filed later | the other requirement lines that still describe waits |
| 11 | 6 | b11p66acb23 | REQ, build item RT4, accepted by o1000 means a disposition, not a waiver | RT4 | the config file is among the settings paths |
| 12 | 6 | b12p67426f6 | REQ, build item E12, CEO B1, accepted by o1000 means a disposition, not a waiver | E12, CEO B1 | the diff scan covers every class a diff can show; the gate is on every later command; an action asked or reported during the build that is not positively cleared is not taken (E12) |
| 13 | 6 | b13p6fb9a58 | REQ, build item E11, accepted by o1000 means a disposition, not a waiver | E11 | a safety stop keeps the branch off origin (E11) |
| 14 | 6 | b14p6dd986e | REQ, build item E13, accepted by o1000 means a disposition, not a waiver | E13 | closing a finding and its statements need a verified operation identity (E13) |
| 15 | 6 | b15p64186be | REQ, build item E13, CEO B8, accepted by o1000 means a disposition, not a waiver | E13, CEO B8 | revert and decide are operation-only, mail text is treated as untrusted, and the owner has a way back from a mistaken hold (E13, B8) |
| 16 | 6 | b16p67ee30f | REQ, build item E15, accepted by o1000 means a disposition, not a waiver | E15 | the shared owner-record reader refuses start records unless a use is allowed (E15) |
| 17 | 2 | b17p2d20eca | REQ | CEO B6, RT17 | with 28 |
| 18 | 2 | b18p22104b7 | REQ + DF part | RT12; wording filed later | on a marked goal the safety-class check is met by the start review or the safe option, and the check stays; deliver-first for the CBS-1.2 wording |
| 19 | 2 | b19p2ede9b9 | REQ | DX D9 | a named acknowledgement of decision ids (D9) |
| 20 | 2 | b20p242ae28 | REQ | RT13 | the new rows name DLF-1.3 |
| 21 | 3 | b21p32146d5 | REQ + DF part | DX D17; time limits filed later | holds and open findings show age, responsible session and next step (D17); deliver-first for time limits and missed-with-cause |
| 22 | 8 | b22p898a825 | REQ | RT14 | one message with a recommendation per item, one code, and what happens without an answer |
| 23 | 1 | b23p12524c0 | REQ | RT15 | a written DEL-21 comparison with GitHub required checks and environment reviewers, before the E1-E5 code |
| 24 | 1 | b24p1b389b6 | REQ (PW) | RT11 | approval comes before the DLF-1 revision (with 8) |
| 25 | 1 | b25p1902119 | REQ | RT5 | with 9 |
| 26 | 8 | b26p8ef5b5d | REQ (PW) | RT17 | hand merge and cut or leave are named as kept owner rules (TD2127) |
| 27 | 8 | b27p830d75f | REQ (PW) | RT17 | modes the owner switched off are named as kept owner rules (TD2127) |
| 28 | 2 | b28p23ff37a | REQ (PW) | CEO B6, RT17 | the kept owner rules are named beside the metric, with waiting time by cause (B6) |
| 29 | 6 | b29p6ce5a29 | REQ (PW), build item CEO B1, E7, accepted by o1000 means a disposition, not a waiver | CEO B1, E7 | a proposed action counts as not safety only on positive grounds; otherwise it takes the safe option (with 3) |
| 30 | 7 | b30p7b208de | REQ (PW) | E2, E3, DX D15 | recovery of a lost record that keeps approvals and restrictions (E2, E3, D15) |
| 31 | 7 | b31p75d6ee2 | REQ | E1, E4 | approval evidence travels with a handover (E1, E4) |
| 32 | 2 | b32p2cbff9b | REQ | E4 | safe concurrent writes of decisions (E4) |
| 33 | 6 | b33p667f29a | REQ, build item E13, accepted by o1000 means a disposition, not a waiver | E13 | revert needs operation authority and goal ownership (E13) |
| 34 | 8 | b34p8145e13 | REQ (PW) | RT16 | with 6; an ongoing outside action is stopped or gets corrective work |
| 35 | 3 | b35p3c0770c | REQ (PW) | RT3 | "no estimate" is kept apart from the budget, with a stated cap rule |
| 36 | 4 | b36p49b9bbc | DF | filed later | step token budgets |

### Build list

E1 to E5 are under Build order above. Every item below is required unless it says it is filed later.

- E6: the start message is held until its items are final.
- E7: separate scan rules for stop text and for diffs, using changed Reviewed units rather than wiki paths, checked on past breaks and diffs before the build; an unknown action is held under operation.
- E8: merge scans the head it merges for new uncovered changes; a hand or already-merged pull request is checked before release; where that cannot be enforced the output says so; a new finding or revert marks the open pull request.
- E9: release holds are shared across machines and read by every local release path; a replacement goal is new or unmerged; making a hold and publishing are ordered.
- E10: the diff is read with external diff tools off, as text, decoded safely, with NUL-separated names; an unreadable diff refuses.
- E11: findings keep hashes and blob ids, not content; stored text passes the existing secret and private-name checks; a safety stop does not push the branch.
- E12: the build gate also guards flow runs, record, pr and every merge, with or without the principles page; merge refuses an unanswered marked goal.
- E13: answer, closing a finding, revert and the delivered mark are operation-only.
- E14: a fix's row names its finding and has a red run without the fix; drop and revert follow renames and copies.
- E15: a start record is recognised by its content wherever owner records are read, and its uses are recorded in one place.
- E16: for a marked goal, deliver-first is read from the committed base config, and off wins.
- E17: one exact reply form after quoted text is removed; operation can resend; start mail goes first under the daily limit.
- E18: a stated drop rule for goals released as leave or by hand; the list is paged and only printed ids are marked.
- E19: a missing new script does not break an unmarked goal; a handover checks the receiver's version.
- CEO B1: an action that is not positively cleared is treated as safety; a label raises the class; each not-safety ruling on an action is listed with its reason, with toy cases for money, deletion and steward-merge stops in varied wording.
- CEO B2: the start message is sent only after its items are written, and a toy expects one send.
- CEO B3: no removal or revert goal targets a fix or drop decision.
- CEO B4: each revert line says what it can stop.
- CEO B5: the Operation page keeps the protection against full auto answering a question that contradicts the owner.
- CEO B6: the board shows blocked minutes by who they wait for and why, beside the owner metric, with goals stopped and parts dropped.
- CEO B7: a queued merge that cannot be withdrawn is reported with the next step.
- CEO B8: the owner has a recorded way back from a mistaken revert.
- CEO B9: a refusal for a pending removal names it and how to clear it; operation can name a replacement.
- CEO B10: safety and irreversible decisions are listed first.
- DX D1: an items-pending state; one command records the items and then sends once.
- DX D2: each operation action has a named command, with who may run it, exit codes and an example; a refusal prints the command.
- DX D3: one exact reply form; a refusal gives the current code, the forms and whether the answer is unused.
- DX D4: a read-only command shows the start review; the freeze and the build refusal print it and how to answer.
- DX D5: new refusals carry a stable code, values, fix, recovery, side effects and a non-zero exit.
- DX D6: a failed queued-merge withdrawal is saved as pending, holds releases, exits non-zero and names who finishes it.
- DX D7: each revert command is on its own line, unwrapped, with its folder quoted.
- DX D8: revert has a read-only preview.
- DX D9: the delivered mark is a named acknowledgement of decision ids.
- DX D10: a read-only scan preview.
- DX D11: command names that do not clash; class values are printed.
- DX D12: each new stored, mailed or printed field passes the private-name scan.
- DX D13: the goal's mark, effective mode and controlling setting are shown; an older receiver is refused at handover.
- DX D14: accepting an answer can be retried with the same record after a failed push.
- DX D15: a lost owning record has a recovery that keeps approvals and findings.
- DX D16: one end-to-end How-to example; the Machines and Release How-to pages are updated.
- DX D17: a hold shows its age, last progress, responsible session and next command.
- RT1: a safety item names exact files or an existing folder.
- RT2: a rule for ordinary test updates that loosens no check.
- RT3: "no estimate" is kept apart from the budget, with a stated cap rule.
- RT4: the config file is among the settings paths.
- RT5: README and Principles are regenerated.
- RT6: filed later (not one of the 36): the CI release workflow reads the holds.
- RT7: the answer command records the action taken.
- RT8: the merge lock is held only around the last check and the merge request.
- RT9: a re-review step for the revised DLF-1 unit.
- RT10: filed later (break 36): step token budgets.
- RT11: only wording approved by top or the owner lands, and approval comes before the DLF-1 revision.
- RT12: on a marked goal the safety-class check is met by the start review or the safe option, and the check stays.
- RT13: the new rows name DLF-1.3.
- RT14: one start message with a recommendation per item, one code, and what happens without an answer.
- RT15: a written DEL-21 comparison with GitHub required checks and environment reviewers, before the E1 to E5 code.
- RT16: after a merge, the owner's revert command opens a revert goal for that part and is its start review; each decision records what it let go on, and its revert line says what it stops.
- RT17: the kept owner rules (hand merge with auto_merge off, cut or leave, the DLF-1.4 accept list, modes the owner switched off) are named in the PR and beside the metric.
- RT18: a fresh reader gives a verdict on each fix.

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

### Build record: slices

- 78d2c1b05: E4 and E5. 3af6c6f17: E3. 2b7969ae5: E2. Next: E1.
- E2 readings, sent to operation: a decisions file holding only its first mark entry, with no record, counts as the empty one of B6; a queued record's report lines are not later activity.
- operation-mac accepted E3 (3af6c6f17) and E2 (2b7969ae5), both E2 readings included.
- B7 at merge: the hold reads the mark committed on the goal branch when the record lost it; its toy case was seen red with that read switched off.
- TD2180 (speed, scope frozen): only what the recorded plan and dispositions require is built; anything new becomes a deliver-first line for after the v1.1.0 cut unless it blocks the merge. The removal of dlf's private-data wait stays in this build.
- Filed deliver-first: v110-one-review-choice-1 (three toys fail in an isolated local clone on main while GitHub passes them). Explicit pre-scans under TD2170: 1, clean; the filing tool scans the posted text again.
- test-monitoring.sh, run to completion on untouched main 7784d862f in the isolated clone: 38 pass, 2 fail, the same two "watch.py alone" cases as on this branch (the toy's copied list lacks batch.py). Pre-existing. An earlier run here that showed 7 fails did not repeat, and one earlier run on main hit the 7 minute limit.

### Later work

- From the DEL-21 comparison (RT15): a required status check could add to E3's merge hold on GitHub's side. It needs a repository protection setting, which is the owner's.
