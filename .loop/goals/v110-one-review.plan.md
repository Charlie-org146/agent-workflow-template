# Plan: v110-one-review

## Implementation plan

Goal: a goal asks the owner once, at its start, and after that no step of the goal waits on the owner. Owner o1037, o1038 (the five done lines and the DLF-1.3 wording), o1039. Operation's ruling TD2103 (the DEL-3 wording; o1038 governs over cap-gate's lines), listed for the owner to revert. o1040 removed the leak gate; a later goal deletes the clauses that mention it, and this plan neither adds nor removes a leak-read requirement. The time budget is 240 minutes (operation kept it); the tool's estimate is 694 minutes and the ETA 870 minutes.

Base: main 7784d862f.

### Depends on (order)
1. Operation's build order: main-red, then G1's pull request, then this goal, then cap-gate, then On time; detector-fix after this goal. This goal takes main after the goals before it.
2. skills/workflow-release is in the touches (operation added it). Before the build, operation also adds .loop/config.json, .loop/START.md, skills/workflow-setup/scripts/settings.py and docs/wiki/How-to-use-Delivery.md.
3. Rows are added only through `regression.py add`.

### Which goals the rule covers
- A new setting, `one_review`, read from the base branch's committed config, never from a goal's branch. It is off by default and on in this repo's config. Test fixtures without it behave as today.
- With it on, every goal frozen from then on gets a stored "one review" mark at its freeze, from each entry point: `goal.py new`, `goal.py adopt` and the monitored start (`watch.py go`, which also starts queued goals). The mark does not depend on the start message.
- An older goal, adopted or not, is marked only when the owner answers a start review sent for it.
- Deliver-first and always-ask are read again at every decision. While deliver-first is off for a goal, or it is set to always ask, its stops wait for the owner as today. Switching them does not clear an open finding or a stop.
- Unmarked goals behave as today.

### 1. The start review (done line 1)
- One message: the frozen done lines, the numbered safety items, and the answer forms.
- A safety item is one of DLF-1.3's seven classes, one concrete action, and the files it touches. Where the files are not known yet, an item may name a folder inside a skill's scripts folder, never the scripts folder or the repository. An action outside the repository's files names none. A scan reports every class that matches the goal sentence, the done lines and the touched paths; operation writes each hit's action and files and may add items. Every hit appears; one with no concrete action is shown as "not approvable" and the approve forms approve all the others. The message lists the items found and those operation added.
- A planned change to a Reviewed requirement is a numbered item with its page, ID and exact new text.
- The message carries a 6-character code over the done lines and every item. Answers: `approve start SLUG CODE`, `approve start SLUG CODE except N,N`, `reject start SLUG CODE`.
- `goal.py start SLUG --owner-record ID` accepts a record only when its text is one of those forms with the current code, it is later than the message, it is not delegated or from a peer, it is the owner's own words when the message has any item, and no other action has used it. It stores the record and each item as approved or refused. A refused item takes the safe option. A reject stops the goal. It is accepted once. One shared check marks a start answer record, and the ETA and budget record, plan-accept, plan approve, release promote and schedule order paths refuse it. As a requirement record, its tags name the goal and only the approved pages and IDs; the pr text comparison in section 2 holds it to the approved text.
- The message is sent at the freeze by its own send in the mail code, once per code, and stays under "Needs you" until answered. The ordinary mail pass counts that line as already sent, so no second mail with other answer words goes out, and a marked goal adds no pre-flight lines. A mail reply carrying a start form is recorded as the owner's words, as mail replies are today. When mail is off, unset, over budget or fails, the freeze says it was not mailed and why.
- Idea and plan may run before the answer. The build step and every later step refuse until the answer is recorded.
- Pre-flight questions are not owner asks for marked goals. An operation-only command for marked goals answers budget (keep, or raise up to the DLF-1.2 cap), plan approval and quota, stores the answers where the ETA reads them, and lists each as a decision. A private-name question is answered by renaming or dropping, never by editing the list. A memory question holds the goal under operation; the floor stays.
- For a marked goal, the monitored start records ETA and budget as `goal.py new` does, and its review steps keep full depth. For a marked goal from any entry point with no estimate, the time budget is recorded as the estimate. Unmarked goals are not changed.

### 2. Decisions after the start (done lines 2 and 3)
- Every stop on a marked goal writes a numbered decision: kind, question, what was taken, safety class, files, state. The ledger is part of the goal's run record, so a handover and adopt carry it. pr and merge refuse a marked goal whose ledger is missing. A revert is run where the goal's record is.
- For marked goals, a new scan that reports every matching class sorts each stop from what the stop carries: a break, plan question, choice or reading, its text and any files it names; a failed test, that test's diff; a budget, pre-flight or process hold, its text. A match makes a safety stop; no match is not safety. A needed diff that cannot be read refuses without using a try. Today's classifier is unchanged for unmarked goals.
- At pr, the whole branch diff is scanned once for loosened tests, settings paths, private data and changed Reviewed requirements; each new class and file with no approved item or earlier finding opens one finding.
- Not safety: operation's recommendation is taken, with today's deliver-first line.
- Safety inside an approved item proceeds under that item: the same class, the same action as operation states it, and every file the finding names inside the item's files. A finding that names files is never inside an item that names none. Anything broader, new or unsure is outside.
- Safety outside: the finding is open at once and keeps the content it was found on. pr refuses while one is open; the check comes after the reached-test run and before the push. merge refuses too. Only operation closes it:
  - Fix: a commit on the goal branch after the finding that changes a file the finding names, a regression row that this goal adds or changes, with a recorded red run, passing in that reached-test run, and a rescan of the finding's files with no uncovered match. If the commit leaves the branch, or those files change into a new match, the finding opens again.
  - Drop: the part is taken out. For a part in files, it covers every file the finding names, as whole files, and the head has no change in them against its merge base; each done line is stated as still met. For an action that was asked about, the fixed reply not to take it has been sent, any named files are unchanged against the merge base, and operation records that it was not taken; it opens again if asked again or those files change. Either way the part is filed as a DLF-1.1 line.
  - Stop: when the part cannot be taken out as above, a done line needs it, or operation is unsure. The goal stops without merging, files why and is shown as stopped.
- A stop of this kind is permanent: step, record, pr, merge, resume and the mender refuse that goal, and the check-in keeps showing it until it is retired.
- `plan-accept` refuses a safety-class break on a marked goal. A non-safety break needs no accept. A safety break with its finding open passes the build gate, so its fix can be built; pr and merge refuse until the finding closes. The gate still needs a recorded review of the current plan.
- On a marked goal, pr also refuses a changed Reviewed requirement whose head text is not an approved item's text. Today's requirement guard is unchanged.
- `goal.py decide SLUG --finding TEXT --class C [--files ...]` opens a finding from a mail or report. A safety finding with no unmerged goal is kept in a repository list shown with the decisions; about merged code, it queues a fix or removal goal and holds releases (section 3).
- Waits on a marked goal (`goal.py wait`, a worker's waiting report, repeated refusals, a bad flow marker, the merge round cap) are holds addressed to operation; `goal.py answer` works as today and the answer is a listed decision. Three failed tries and a refused automatic release stay as they are today (stopped or failed); they are listed, readdressed to operation, and a resume or retry is a listed decision.
- Full auto on a marked goal: a question held for a safety reason gets a fixed reply not to take the action, logged with its own verdict word so health does not count it as an answered safety question, and opens a finding; one held for an unknown kind or no recommendation becomes an operation hold; an ETA question follows DLF-1.2.
- Mails, headline counts and "Needs you" lines about a marked goal's own stops are addressed to operation. The merge and release rules the owner set (merging by hand, cut or leave, a protected release PR's approval) move to a "Your merge and release steps" section with today's mails. Worker prompts are reworded to match.

### 3. Check-in and revert (done line 4)
- "Decided for you" in the check-in, for every followed repo: one line per decision, ending in a command that runs as printed and saying what it will stop. A decision stays listed until both: the check-in has been run with its new owner flag with that decision in it (the flag is for the operation session's run that it shows the owner; the skill text says so, and no timer or pass sets it), and the goal's release is cut or its stopped goal retired. Every such decision is listed. Marked goals' full-auto answers appear only here.
- `goal.py revert SLUG N` needs no owner record, logs who ran it, and a repeat changes nothing. It only stops work: it does not undo a safety fix, bring back a dropped part or reopen a safety item.
- A decision that let named files go on: pr and merge refuse until the head has no change in those files against its merge base and operation records that each done line is still met; step and record stay open so the part can be taken out. The files are then filed as a DLF-1.1 line. If they cannot be taken out or a done line needs them, the goal stops without merging.
- Every other decision, a fix or a drop included: the goal stops without merging and files why.
- Merge and revert take one lock, held only around the last check and the merge request; the single, batch and armed-watcher paths check again just before they merge. A revert of an armed or queued merge withdraws it (`gh pr merge --disable-auto`, or taking the PR out of the merge queue); if that fails the revert says so and follows the after-merge rules once the merge lands. The check-in shows how each marked goal was merged.
- After a merge, a revert says it cannot take back what merged or shipped. With named files, it files a line marked "reverted" and queues a removal goal; any other decision is only recorded.
- A removal or fix goal queued by a revert or by a finding about merged code is pending until its merge is in the commit being released. While one is pending, the manual cut, the automatic release and release promote refuse; accept and accept-all do not clear it. A published release is reported as such. The revert output names the release paths it holds.

### 4. What stays (done line 5)
Every existing check stays: the private-name scan before a push, the reached-test run before a merge, the test caps, the requirement guard, the auto_merge rule, release PR approval and the major-release rules. New code adds refusals or readdresses a wait. A refusal whose fix needs the owner stays a refusal; on a marked goal its text says to fit within it, drop or stop. The row `orv-checks-stay` runs the private-name refusal before a push and the reached-test refusal before a merge on a marked goal.

### 5. Metric, inventory and pages
- Each wait records who it is addressed to. Metric on the board: minutes after its start review that a marked goal spends in waits addressed to the owner by a stop of its own, target 0.
- Inventory check: it finds every call in delivery, monitoring and release that sets a goal waiting and every message that asks for the owner or an owner record, and requires each to be listed with its outcome on marked goals. An unlisted one fails.
- DLF-1.3 is replaced with the owner's text. The approved metric goes under it; its safety metric and Test line stay. DLF-1.1 and the DLF-1 heading are not edited; their two mismatches with the new text are filed as one DLF-1.1 later line. The DLF-1 revision cites o1038; if the tool refuses that record, the build stops and asks operation.
- On the Delivery page, the DEL-3 bullet "My decisions wait for me or are auto-approved where allowed" takes TD2103's wording. On the Operation page, the "Full auto" bullet under OPS-1, the non-goal "Full auto never answers for me ..." and the metric "a run needs me only for the safety-class decisions ..." change the same way. The How-to pages for Delivery, Operation and Deliver first are updated; Home.md is regenerated.
- Cap-gate: its frozen lines 4 and 5 have a blocked review wait for the owner's recorded answer, and frozen lines do not change. This goal does not edit cap-gate. Operation has taken the question to top (question 1).

### Where the code goes
Three new standard-library scripts: in workflow-delivery, `start_review.py` (the mark, the scan, the message, the answer, the build gate) and `decisions.py` (the ledger, the safety outcomes, the revert and its refusals, the inventory table); in workflow-monitoring, `review_view.py` (the check-in section, the readdressed lines, the metric). Callers change by a few lines. A script with too little room first gives up whole functions that refuse nothing to one of the new scripts: guards.py `pending_items`; auto.py `eta_new`; layers.py `one_line`; board_log.py `principles` and `unread`; board_status.py `fresh_tokens`. When a new script is missing, a marked goal refuses and names the file. operate.py is not edited. proctree.py is not edited.

Owner-wait surfaces and their change for marked goals: check-in Needs you and headline (checkin.py), board needs and waiting text (board.py, board_model.py, board_lines.py, board_status.py, live_board.py), report and dashboard (monitor.py), layer owner needs (layers.py), held-time matching (board_log.py, which also matches the new operation wording), mails (notify.py, mailbox.py), worker prompts and reports (watch.py, mend.py, sessions.py), pre-flight (replan.py), release asks (release.py, autorelease.py). Existing strings are not reworded; marked goals get new ones.

### Checks
New toys: `dev/toy/test-one-review-start.py` and `dev/toy/test-one-review-decide.py`, each in temporary git folders with their own home, a stand-in `gh` and mail sender, no network. Each case is seen red on its own assertion before its fix (TD2007).

| # | Covers |
|---|---|
| 1 | each entry point: the mark, one message with done lines, every matching class and the code; a resend after a code change; the not-mailed output; the build refuses without an answer |
| 2 | answers: approve, approve except, reject; each refused kind of record |
| 3 | after the answer: a break, plan question, reading, budget overrun with and without an estimate, pre-flight question, held full-auto question, mail finding and each process hold leave nothing addressed to the owner |
| 4 | a design choice on a goal that touches a wiki page opens no finding; the pr scan opens one per new class and file |
| 5 | pr and merge refuse for an open finding, a dropped file still changed, a fix commit that left the branch, and an unapproved requirement text |
| 6 | the listing after a background run and after merge and automatic release; the printed command runs; the revert refusals, the stop cases, the merge re-check, a withdrawn queued merge, and another goal's release and a promote held after a post-merge revert |
| 7 | an unmarked goal and a fixture without the setting behave as today; deliver-first switched off mid-goal; a handover carries the ledger and a missing one refuses; a stopped goal refuses resume and the mender; an unlisted wait fails the inventory check |
| 8 | on a marked goal, the private-name refusal before a push and the reached-test refusal before a merge |

Rows `orv-start-review`, `orv-no-owner-wait`, `orv-safe-option`, `orv-checkin-revert` and `orv-checks-stay` are added, each "Given ..." and under 400 characters. Existing rows are not edited. Done line 5 is also held by the goal's full run against main's known list.

### Questions (for operation, each with its recommendation)
1. With top: cap-gate's lines 4 and 5 say the owner answers. Recommended: before cap-gate builds, replace it with a goal whose lines say the safe option.
2. Add .loop/config.json, .loop/START.md, skills/workflow-setup/scripts/settings.py and docs/wiki/How-to-use-Delivery.md to the touches before the build. Recommended: yes.
3. DLF-1.3 still names the leak read before a push; o1040 removed the leak pairs. This plan keeps the automatic private-name scan before a push, and the later no-leak-gate goal edits the sentence. Recommended: confirm that reading.

### Deliver-first lines
None yet.

### Verify by hand
1. Start a toy goal that touches a settings file. Expect: one message with the done lines, a numbered safety item and a code, under "Needs you"; the build refuses.
2. Answer with the approve form and run it through a red-team break and a budget overrun. Expect: no owner wait; both appear under "Decided for you" with a revert command.
3. Run one printed revert command. Expect: the output says what is stopped, and pr refuses.

### Files
Files: skills/workflow-delivery/scripts/start_review.py, skills/workflow-delivery/scripts/decisions.py, skills/workflow-delivery/scripts/goal.py, skills/workflow-delivery/scripts/goal_steps.py, skills/workflow-delivery/scripts/guards.py, skills/workflow-delivery/scripts/dlf.py, skills/workflow-delivery/scripts/dlf_cut.py, skills/workflow-delivery/scripts/fit.py, skills/workflow-delivery/scripts/flow.py, skills/workflow-delivery/SKILL.md, skills/workflow-delivery/references/commands.md, skills/workflow-monitoring/scripts/watch.py, skills/workflow-monitoring/scripts/batch.py, skills/workflow-monitoring/scripts/replan.py, skills/workflow-monitoring/scripts/auto.py, skills/workflow-monitoring/scripts/notify.py, skills/workflow-monitoring/scripts/checkin.py, skills/workflow-monitoring/scripts/mend.py, skills/workflow-monitoring/scripts/sessions.py, skills/workflow-monitoring/scripts/board_model.py, skills/workflow-monitoring/scripts/live_board.py, skills/workflow-monitoring/scripts/machines.py, skills/workflow-monitoring/SKILL.md, skills/workflow-release/scripts/merge.py, skills/workflow-release/scripts/release.py, skills/workflow-release/scripts/autorelease.py, skills/workflow-release/SKILL.md, skills/loop-files.md, listing.json, dev/toy/test-one-review-start.py, dev/toy/test-one-review-decide.py, .loop/regression.tsv, docs/wiki/Deliver-first.md, docs/wiki/How-to-use-Deliver-first.md, docs/wiki/Delivery.md, docs/wiki/Operation.md, docs/wiki/How-to-use-Operation.md, docs/wiki/Home.md, docs/wiki/Tests.md, skills/workflow-monitoring/scripts/review_view.py, skills/workflow-monitoring/scripts/board.py, skills/workflow-monitoring/scripts/board_lines.py, skills/workflow-monitoring/scripts/board_status.py, skills/workflow-monitoring/scripts/board_log.py, skills/workflow-monitoring/scripts/monitor.py, skills/workflow-monitoring/scripts/layers.py, skills/workflow-monitoring/scripts/mailbox.py, skills/workflow-monitoring/scripts/schedule.py, skills/workflow-release/scripts/review.py, skills/workflow-setup/scripts/settings.py, .loop/config.json, .loop/START.md, docs/wiki/How-to-use-Delivery.md
Lines: about 1600
Gates: the planning gate, the build gate, the ship gate
Classes: guard change (new refusals at build, pr, merge and release; owner waits readdressed; owner o1038)

### Byte table
"Now" is the base; "after" is an estimate, measured again after the goals before this one merge. A script that would reach 20,480 B stops the build.
Bytes: skills/workflow-delivery/scripts/start_review.py: now 0, after 13,000, left 7,480
Bytes: skills/workflow-delivery/scripts/decisions.py: now 0, after 18,000, left 2,480; if it cannot fit, the inventory table moves to a data file, asked of operation first
Bytes: skills/workflow-monitoring/scripts/review_view.py: now 0, after 12,000, left 8,480
Bytes: skills/workflow-delivery/scripts/guards.py: now 20,310, after 20,100, left 380; pending_items moves out first
Bytes: skills/workflow-delivery/scripts/dlf.py: now 17,030, after 17,600, left 2,880
Bytes: skills/workflow-monitoring/scripts/auto.py: now 20,434, after 20,000, left 480; eta_new moves out first
Bytes: skills/workflow-monitoring/scripts/layers.py: now 20,439, after 20,200, left 280; one_line moves out first
Bytes: skills/workflow-monitoring/scripts/board_log.py: now 20,466, after 20,300, left 180; principles and unread move out first
Bytes: skills/workflow-monitoring/scripts/board_status.py: now 20,423, after 20,350, left 130; fresh_tokens moves out first
Bytes: skills/workflow-monitoring/scripts/board_lines.py: now 18,997, after 19,200, left 1,280
Bytes: skills/workflow-monitoring/scripts/board.py: now 18,765, after 19,000, left 1,480
Bytes: skills/workflow-monitoring/scripts/monitor.py: now 18,672, after 18,900, left 1,580
Bytes: skills/workflow-monitoring/scripts/checkin.py: now 18,873, after 19,500, left 980
Bytes: skills/workflow-monitoring/scripts/notify.py: now 18,753, after 19,700, left 780
Bytes: skills/workflow-monitoring/scripts/mailbox.py: now 18,994, after 19,150, left 1,330
Bytes: skills/workflow-monitoring/scripts/watch.py: now 18,771, after 19,200, left 1,280
Bytes: skills/workflow-monitoring/scripts/batch.py: now 18,988, after 19,150, left 1,330
Bytes: skills/workflow-monitoring/scripts/replan.py: now 18,617, after 18,850, left 1,630
Bytes: skills/workflow-monitoring/scripts/live_board.py: now 18,464, after 18,700, left 1,780
Bytes: skills/workflow-monitoring/scripts/sessions.py: now 18,977, after 19,150, left 1,330
Bytes: skills/workflow-monitoring/scripts/mend.py: now 18,958, after 19,150, left 1,330
Bytes: skills/workflow-monitoring/scripts/machines.py: now 18,927, after 19,100, left 1,380
Bytes: skills/workflow-monitoring/scripts/board_model.py: now 18,965, after 19,250, left 1,230
Bytes: skills/workflow-release/scripts/autorelease.py: now 18,926, after 19,200, left 1,280
Bytes: skills/workflow-release/scripts/release.py: now 18,339, after 18,650, left 1,830
Bytes: skills/workflow-release/scripts/review.py: now 18,988, after 19,150, left 1,330
Bytes: skills/workflow-setup/scripts/settings.py: now 19,784, after 20,050, left 430

## Review record
Not reviewed yet.
