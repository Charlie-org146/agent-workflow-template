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

The other required items of the reviews (CEO B1 to B10, DX D1 to D17, eng E6 to E19) are summarised in the recorded plan reply.

### Rulings

- The merge and release rules the owner set stay, and the PR and the metric name them as kept owner rules, beside the metric.
- The leak read is not a build item; the automatic private-name scan stays as a filter. The DLF-1.3 text stays as approved.
- The CI release workflow file is not part of this goal and is filed as a deliver-first line; the local release step reads the holds.
- The rule ships on, with a documented off switch in settings. The first goal after the merge is named the pilot and gets a red-team line on whether the one review held.
- Past the start review, a part that would need an owner-contradicting decision is dropped and filed (top's reading; not added to any page).
- Page wording approved by top under its DOC-2 delegation (TD2128), listed for the owner:
  - Delivery, DEL-3: "My decisions on a goal are made once, at its start; later ones are made on the recommendation, with the safe option for safety, and listed for me to revert (DLF-1.3)."
  - Operation, OPS-1: "**Full auto:** top decides process choices and numbers each decision. On a goal past its start review, a safety item found later takes the safe option without asking (DLF-1.3); outside that, the safety classes wait for my typed words."
  - Operation, non-goal: "Full auto never answers for me on destructive, money, security or owner-contradicting decisions. On a goal past its start review, a safety item found later takes the safe option without asking (DLF-1.3)."
  - Operation, metric: "With full auto on, a goal needs me only at its start review; the merge and release rules I set stay. Minutes a goal waits for me after its start review: target 0."
- The DLF-1 metric and the DLF-1 heading wait for the owner. They hold the merge, not the build, and are built as separable edits. If the owner declines, both lines stay as they are and the PR notes the mismatch.

### Red-team dispositions (plan file sha1 defb36a61622)

36 breaks, named by number, principle and short id; their text is not repeated here. All 36 are accepted (operation: principles 1, 3, 4, 6 and 8 under o1000; 2 and 7 under o1037). PW means the break showed the plan wrong as written.

| break | principle | short id | disposition |
|---|---|---|---|
| 1 | 8 | b1p87f0ae6 | required (PW): the start message is sent once, after its items are final, after plan and red team and before the build (B2, E6) |
| 2 | 8 | b2p831ef23 | required (PW): a safety item names exact files or an existing folder |
| 3 | 6 | b3p667b05d | required (PW): labels raise the class, and unknown stays safety (B1, E7) |
| 4 | 2 | b4p2507a43 | required (PW): a fix's row is tied to the finding and was red without the fix; a fresh reader gives a verdict on the fix (E14) |
| 5 | 8 | b5p893dca2 | required (PW): a rule for ordinary test updates that loosens no check |
| 6 | 8 | b6p8f4ac32 | required (PW): after a merge the revert command opens a revert goal for that part, and the owner's revert command is its start review (TD2127); each decision records what it let go on, and its revert line says what it stops, "stops the goal" when that is the whole goal (TD2128, B4) |
| 7 | 8 | b7p8144c52 | required (PW): the DLF-1.4 accept list is named as a kept owner rule, in the PR and beside the metric (TD2127) |
| 8 | 1 | b8p1913e68 | required (PW): only wording approved by top or the owner lands; any other line stays as it is |
| 9 | 1 | b9p1108665 | required (PW): README and Principles are regenerated |
| 10 | 1 | b10p12ee017 | deliver-first: the other requirement lines that still describe waits |
| 11 | 6 | b11p66acb23 | required: the config file is among the settings paths |
| 12 | 6 | b12p67426f6 | required: the diff scan covers every class a diff can show; the gate is on every later command; an action asked or reported during the build that is not positively cleared is not taken (E12) |
| 13 | 6 | b13p6fb9a58 | required: a safety stop keeps the branch off origin (E11) |
| 14 | 6 | b14p6dd986e | required: closing a finding and its statements need a verified operation identity (E13) |
| 15 | 6 | b15p64186be | required: revert and decide are operation-only, mail text is treated as untrusted, and the owner has a way back from a mistaken hold (E13, B8) |
| 16 | 6 | b16p67ee30f | required: the shared owner-record reader refuses start records unless a use is allowed (E15) |
| 17 | 2 | b17p2d20eca | required: with 28 |
| 18 | 2 | b18p22104b7 | required for behaviour: on a marked goal the safety-class check is met by the start review or the safe option, and the check stays; deliver-first for the CBS-1.2 wording |
| 19 | 2 | b19p2ede9b9 | required: a named acknowledgement of decision ids (D9) |
| 20 | 2 | b20p242ae28 | required: the new rows name DLF-1.3 |
| 21 | 3 | b21p32146d5 | required: holds and open findings show age, responsible session and next step (D17); deliver-first for time limits and missed-with-cause |
| 22 | 8 | b22p898a825 | required: one message with a recommendation per item, one code, and what happens without an answer |
| 23 | 1 | b23p12524c0 | required: a written DEL-21 comparison with GitHub required checks and environment reviewers, before the E1-E5 code |
| 24 | 1 | b24p1b389b6 | required (PW): approval comes before the DLF-1 revision (with 8) |
| 25 | 1 | b25p1902119 | required: with 9 |
| 26 | 8 | b26p8ef5b5d | required (PW): hand merge and cut or leave are named as kept owner rules (TD2127) |
| 27 | 8 | b27p830d75f | required (PW): modes the owner switched off are named as kept owner rules (TD2127) |
| 28 | 2 | b28p23ff37a | required (PW): the kept owner rules are named beside the metric, with waiting time by cause (B6) |
| 29 | 6 | b29p6ce5a29 | required (PW): a proposed action counts as not safety only on positive grounds; otherwise it takes the safe option (with 3) |
| 30 | 7 | b30p7b208de | required (PW): recovery of a lost record that keeps approvals and restrictions (E2, E3, D15) |
| 31 | 7 | b31p75d6ee2 | required: approval evidence travels with a handover (E1, E4) |
| 32 | 2 | b32p2cbff9b | required: safe concurrent writes of decisions (E4) |
| 33 | 6 | b33p667f29a | required: revert needs operation authority and goal ownership (E13) |
| 34 | 8 | b34p8145e13 | required (PW): with 6; an ongoing outside action is stopped or gets corrective work |
| 35 | 3 | b35p3c0770c | required (PW): "no estimate" is kept apart from the budget, with a stated cap rule |
| 36 | 4 | b36p49b9bbc | deliver-first: step token budgets |
