# Plan: v110-one-review

## Implementation plan

Goal: a goal asks the owner once, at its start, and after that no step of the goal waits on the owner. Owner o1037, o1038 (the five done lines and the DLF-1.3 wording), o1039. Operation's ruling TD2103 (the DEL-3 wording; o1038 governs over cap-gate's lines), listed for the owner to revert. o1040 removed the leak gate; a later goal deletes the clauses that mention it, and this plan neither adds nor removes a leak-read requirement. The time budget is 240 minutes (operation kept it); the tool's estimate is 694 minutes and the ETA 870 minutes.

Base: main 7784d862f.

### Depends on (order)
1. Operation's build order: main-red, then G1's pull request, then this goal, then cap-gate, then On time; detector-fix after this goal. This goal takes main after the goals before it.
2. Before the build, operation adds skills/workflow-release to the touches (needed by done lines 2 and 4).
3. Rows are added only through `regression.py add`.

### Which goals the rule covers
- Every goal frozen after this ships gets a stored "one review" mark at its freeze, from each entry point: `goal.py new`, `goal.py adopt` and the monitored start (`watch.py go`, which also starts queued goals). The mark does not depend on the start message.
- Not marked: goals with deliver-first off and goals set to always ask. A goal frozen earlier is marked only when the owner answers a start review sent for it.
- Unmarked goals behave as today.

### 1. The start review (done line 1)
- One message: the frozen done lines, the numbered safety items, and the answer forms.
- A safety item is one of DLF-1.3's seven classes, one concrete action and the paths it touches (files, or one folder below a skill's scripts folder). A scan reports every class that matches the goal sentence, the done lines and the touched paths; the operation writes each hit's action and paths and may add items. No hit is removed. A hit with no concrete action is shown as "not approvable". The message says the scan is a floor.
- A planned change to a Reviewed requirement is a numbered item with its page, ID and exact new text.
- The message carries a 6-character code over the done lines and every item. Answers: `approve start SLUG CODE`, `approve start SLUG CODE except N,N`, `reject start SLUG CODE`.
- `goal.py start SLUG --owner-record ID` accepts a record only when its text is one of those forms with the current code, it is later than the message, it is not delegated or from a peer, it is the owner's own words when the message has any item, and no other action has used it. It stores the record and each item as approved or refused. A refused item takes the safe option. A reject stops the goal. It is accepted once. The record serves no other action, except that it is the requirement record for exactly the approved requirement items.
- The message is sent at the freeze by its own send in the mail code, once per code, and stays under "Needs you" until answered. When mail is off, unset, over budget or fails, the freeze says it was not mailed and why.
- Idea and plan may run before the answer. The build step and every later step refuse until the answer is recorded.
- Pre-flight questions are not owner asks for marked goals. Operation decides budget (keep, or raise up to the DLF-1.2 cap), plan approval and quota, and each answer is a listed decision. A private-name question is answered by renaming or dropping, never by editing the list. A memory question holds the goal under operation; the floor stays.
- The monitored start records ETA, budget and size as `goal.py new` does. With no estimate, the time budget is recorded as the estimate.

### 2. Decisions after the start (done lines 2 and 3)
- Every stop on a marked goal writes a numbered decision: kind, question, what was taken, safety class, files, state.
- A stop is sorted on its own inputs only: a break, plan question, choice or reading on its text and the files it names; a failed test on that test's diff; a budget, pre-flight or process hold on its text. A class match, or today's "unclassifiable", makes it a safety stop. A needed diff that cannot be read refuses without using a try.
- At pr, the whole branch diff is scanned once for loosened tests, settings paths, private data and changed Reviewed requirements; each new class and file with no approved item or earlier finding opens one finding.
- Not safety: operation's recommendation is taken, with today's deliver-first line.
- Safety inside an approved item (same class, paths inside the item's, the same action, named by operation) proceeds under that item. Anything broader, new or unsure is outside.
- Safety outside: the finding is open at once, and pr and merge refuse while it is open. Only operation closes it:
  - Fix: a commit on the goal branch after the finding, and a regression row this goal adds or changes that has a recorded red run and passes in the reached-test run on the head. If the commit leaves the branch, the finding reopens.
  - Drop: a list of whole files. pr and merge refuse unless the head has no change in them against its merge base. Operation states each done line is still met. The part is filed as a DLF-1.1 line.
  - Declined: only for an action asked about and never performed. Named files must be unchanged; it reopens if they change or the action is asked again.
  - Stop: when the part is not whole files, a done line needs it, or operation is unsure. The goal stops without merging, files why and is shown as stopped.
- `plan-accept` refuses a safety-class break on a marked goal. A non-safety break needs no accept.
- On a marked goal, pr also refuses a changed Reviewed requirement whose head text is not an approved item's text. Today's requirement guard is unchanged.
- `goal.py decide SLUG --finding TEXT --class C [--files ...]` opens a finding from a mail or report. A safety finding with no unmerged goal is kept in a repository list shown with the decisions; about merged code, it queues a fix or removal goal and holds releases (section 3).
- Other waits on a marked goal (`goal.py wait`, a worker's waiting report, repeated refusals, a bad flow marker, the merge round cap, three failed tries, a refused automatic release) are holds addressed to operation; `goal.py answer` works as today and the answer is a listed decision.
- Full auto on a marked goal: a question held for a safety reason gets a fixed reply not to take the action, and opens a finding; one held for an unknown kind or no recommendation becomes an operation hold; an ETA question follows DLF-1.2. Always-ask goals are unmarked.
- Mails, headline counts and "Needs you" lines about a marked goal's own stops are addressed to operation. The merge and release rules the owner set (merging by hand, cut or leave, a protected release PR's approval) move to a "Your merge and release steps" section with today's mails. Worker prompts are reworded to match.

### 3. Check-in and revert (done line 4)
- "Decided for you" in the check-in, for every followed repo: one line per decision, ending in a command that runs as printed and saying what it will stop. A decision stays listed until an owner-facing check-in with it has been delivered (a successful check-in mail, or the check-in's new owner flag, which background runs never pass) and its goal's release is cut or the stopped goal retired. No last-N cut. Marked goals' full-auto answers appear only here.
- `goal.py revert SLUG N` needs no owner record, logs who ran it, and a repeat changes nothing. It only stops work: it does not undo a safety fix, bring back a dropped part or reopen a safety item.
- A decision that let named files go on: step, record, pr and merge refuse until the head has no change in those files and each done line is still met; the files are filed as a DLF-1.1 line. Otherwise the goal stops without merging.
- Any other decision: the goal stops without merging and files why.
- Merge and revert take one lock; merge checks again just before it merges, on the single, batch and armed-watcher paths; a revert withdraws an armed or queued merge. A merge by hand runs no check, and the check-in says so.
- After a merge, a revert says it cannot take back what merged or shipped. With named files, it files a line marked "reverted" and queues a removal goal; any other decision is only recorded.
- While a removal is pending, the manual cut and the automatic release refuse every release unless the released commit contains the merged removal; accept and accept-all do not clear it. A published release is reported as such. With merge_queue on, the CI release path is outside these checks, and the output says so.

### 4. What stays (done line 5)
No existing check, leak read, test cap, requirement guard, auto_merge rule, release PR approval or major-release rule changes. New code adds refusals or readdresses a wait. A refusal whose fix needs the owner stays a refusal; on a marked goal its text says to fit within it, drop or stop.

### 5. Metric, inventory and pages
- Each wait records who it is addressed to. Metric on the board: minutes a marked goal waits for the owner after its start review, target 0. Operation holds, stopped time and the owner's merge and release rules do not count.
- Inventory check: it finds every call in delivery, monitoring and release that sets a goal waiting and every message that asks for the owner or an owner record, and requires each to be listed with its outcome on marked goals. An unlisted one fails.
- DLF-1.3 is replaced with the owner's text. The approved metric goes under it; its safety metric and Test line stay. DLF-1.1 and the DLF-1 heading are not edited; their two mismatches with the new text are filed as one DLF-1.1 later line. The DLF-1 revision cites o1038; if the tool refuses that record, the build stops and asks operation.
- The Delivery page's DEL-3 line takes TD2103's wording; the Operation page's owner-question lines change the same way; Home.md is regenerated.
- Cap-gate: its frozen lines 4 and 5 have a blocked review wait for the owner's recorded answer, and frozen lines do not change. TD2103 has cap-gate's build take the safe option under them. This goal does not edit cap-gate. See question 1.

### Where the code goes
Two new standard-library scripts in workflow-delivery: `start_review.py` (the mark, the scan, the message, the answer, the build gate) and `decisions.py` (the ledger, the safety outcomes, the revert and its refusals, the inventory table). Callers change by a few lines. A caller with no room gives up one whole function that refuses nothing to one of the new scripts. When a new script is missing, a marked goal refuses and names the file; nothing falls back to passing.

### Checks
New toys: `dev/toy/test-one-review-start.py` and `dev/toy/test-one-review-decide.py`, each in temporary git folders with their own home, a stand-in `gh` and mail sender, no network. Each case is seen red on its own assertion before its fix (TD2007).

| # | Covers |
|---|---|
| 1 | each entry point: the mark, one message with done lines, every matching class and the code; a resend after a code change; the not-mailed output; the build refuses without an answer |
| 2 | answers: approve, approve except, reject; each refused kind of record |
| 3 | after the answer: a break, plan question, reading, budget overrun with and without an estimate, pre-flight question, held full-auto question, mail finding and each process hold leave nothing addressed to the owner |
| 4 | a design choice on a goal that touches a wiki page opens no finding; the pr scan opens one per new class and file |
| 5 | pr and merge refuse for an open finding, a dropped file still changed, a fix commit that left the branch, and an unapproved requirement text |
| 6 | the listing after a background run and after merge and automatic release; the printed command runs; the revert refusals, the stop cases, the merge re-check, and another goal's release held after a post-merge revert |
| 7 | an unmarked goal behaves as today; an unlisted wait fails the inventory check |

Rows `orv-start-review`, `orv-no-owner-wait`, `orv-safe-option`, `orv-checkin-revert` and `orv-checks-stay` are added, each "Given ..." and under 400 characters. Existing rows are not edited; they now cover unmarked goals. Done line 5 is also held by the goal's full run against main's known list.

### Questions (for operation, each with its recommendation)
1. Cap-gate: its lines 4 and 5 say the owner answers, so a build under them that takes the safe option would not meet them. Recommended: before it builds, replace it with a goal whose lines say the safe option.
2. Add skills/workflow-release to the touches now. Recommended: yes.

### Deliver-first lines
None yet.

### Verify by hand
1. Start a toy goal that touches a settings file. Expect: one message with the done lines, a numbered safety item and a code, under "Needs you"; the build refuses.
2. Answer with the approve form and run it through a red-team break and a budget overrun. Expect: no owner wait; both appear under "Decided for you" with a revert command.
3. Run one printed revert command. Expect: the output says what is stopped, and pr refuses.

### Files
Files: skills/workflow-delivery/scripts/start_review.py, skills/workflow-delivery/scripts/decisions.py, skills/workflow-delivery/scripts/goal.py, skills/workflow-delivery/scripts/goal_steps.py, skills/workflow-delivery/scripts/guards.py, skills/workflow-delivery/scripts/dlf.py, skills/workflow-delivery/scripts/dlf_cut.py, skills/workflow-delivery/scripts/fit.py, skills/workflow-delivery/scripts/flow.py, skills/workflow-delivery/scripts/proctree.py, skills/workflow-delivery/SKILL.md, skills/workflow-delivery/references/commands.md, skills/workflow-monitoring/scripts/watch.py, skills/workflow-monitoring/scripts/batch.py, skills/workflow-monitoring/scripts/replan.py, skills/workflow-monitoring/scripts/auto.py, skills/workflow-monitoring/scripts/notify.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/mend.py, skills/workflow-monitoring/scripts/sessions.py, skills/workflow-monitoring/scripts/board_model.py, skills/workflow-monitoring/scripts/live_board.py, skills/workflow-monitoring/scripts/machines.py, skills/workflow-monitoring/SKILL.md, skills/workflow-release/scripts/merge.py, skills/workflow-release/scripts/release.py, skills/workflow-release/scripts/autorelease.py, skills/workflow-release/SKILL.md, skills/loop-files.md, listing.json, dev/toy/test-one-review-start.py, dev/toy/test-one-review-decide.py, .loop/regression.tsv, docs/wiki/Deliver-first.md, docs/wiki/How-to-use-Deliver-first.md, docs/wiki/Delivery.md, docs/wiki/Operation.md, docs/wiki/How-to-use-Operation.md, docs/wiki/Home.md, docs/wiki/Tests.md
Lines: about 1400
Gates: the planning gate, the build gate, the ship gate
Classes: guard change (new refusals at build, pr, merge and release; owner waits readdressed; owner o1038)

### Byte table
"Now" is the base; "after" is an estimate, measured again after the goals before this one merge. A script that would reach 20,480 B stops the build.
Bytes: skills/workflow-delivery/scripts/start_review.py: now 0, after 12,000, left 8,480
Bytes: skills/workflow-delivery/scripts/decisions.py: now 0, after 17,000, left 3,480; if it cannot fit, the inventory table moves to a data file, asked of operation first
Bytes: skills/workflow-delivery/scripts/guards.py: now 20,310, after 20,400, left 80; one whole function moves out first
Bytes: skills/workflow-monitoring/scripts/auto.py: now 20,434, after 20,430, left 50; the held-question outcome is called from one line, and one whole function moves out first
Bytes: skills/workflow-monitoring/scripts/checkin.py: now 18,873, after 19,400, left 1,080
Bytes: skills/workflow-monitoring/scripts/notify.py: now 18,753, after 19,600, left 880
Bytes: skills/workflow-monitoring/scripts/watch.py: now 18,771, after 19,100, left 1,380
Bytes: skills/workflow-monitoring/scripts/batch.py: now 18,988, after 19,100, left 1,380
Bytes: skills/workflow-monitoring/scripts/sessions.py: now 18,977, after 19,150, left 1,330
Bytes: skills/workflow-monitoring/scripts/mend.py: now 18,958, after 19,100, left 1,380
Bytes: skills/workflow-monitoring/scripts/machines.py: now 18,927, after 19,050, left 1,430
Bytes: skills/workflow-monitoring/scripts/board_model.py: now 18,965, after 19,250, left 1,230
Bytes: skills/workflow-delivery/scripts/proctree.py: now 18,995, after 19,050, left 1,430
Bytes: skills/workflow-release/scripts/autorelease.py: now 18,926, after 19,150, left 1,330
Bytes: skills/workflow-release/scripts/release.py: now 18,339, after 18,600, left 1,880

## Review record
Not reviewed yet.
