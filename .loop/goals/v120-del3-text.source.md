DEL-3.1 One fixed list says what waits for me, and nothing else does. The list:
- The safety classes: deleting what can't be restored, money, security and sandbox settings, private data, steward merges.
- What my features promise: writing or changing a principle, a feature or its limits, marking a feature Reviewed, and loosening a test.
- Freezing a release's brief.
- Shipping a major release, or merging a major template update into another repo.
- Posting anything to a project outside my own repos.
The list lives in one file that every session reads, and only my words change it.
Metric: Questions to me about anything not on the list, per release. Target 0. Today: not counted; many last night.
Test: A goal hits a choice that isn't on the list. It goes ahead on the recommendation and asks nothing. A choice that is on the list waits and asks.

DEL-3.2 In full auto, anything not on the list takes the recommended path at once. The recommendation doesn't have to be the best one. A wrong call is corrected by a later decision, never prevented by waiting. Each one is recorded: what was decided, the options, why, and how to undo it.
Metric: Time from a choice not on the list to acting on it. Target 2 minutes or less. Today: not measured; choices waited for me last night.
Test: Present a goal with a two-option choice not on the list. Within 2 minutes it acts on the recommended option, and its record shows the options, the reason and the undo.

DEL-3.3 A bug found while building is fixed without asking me. A gap between what a feature promises and what it does is filed as one issue and fixed as a patch goal, which merges on green. If the only fix would change what a feature promises or loosen a test, that one goes on the list and waits.
Metric: Bugs found during a release that waited for my word without being on the list. Target 0. Last night 7 were found; most were filed and worked around without me, but some fixes were asked.
Test: A goal's lane finds a bug in a tool. One issue is opened, a patch goal starts and merges on green, and no question reaches me.

DEL-3.4 When something on the list needs me, it's asked once, early, and in one batch. Questions a release can foresee are gathered when its brief is frozen. Each is one decision in plain words, numbered, with a recommendation, the exact words that answer it, and what happens if I don't answer. None is asked twice. My typed words count in whichever operation session I type them: that session writes them into the one record of my words that every machine reads. A message relayed between sessions is never my words.
Metric: Times I had to type the same answer again in a second session. Target 0. Last night: at least 4.
Test: I type an answer in operation-top. The Mac's guard finds it in the record of my words, with the session it was typed in, and acts without asking me to type it there.

DEL-3.5 What was decided for me is listed, and each item can be undone. The board's "Decided for you" list shows each decision made since my last message, with its reason and the exact words that undo it.
Metric: Decisions made for me that show on the list with an undo. Target 100%. Today: decisions are in the operation log, not on the board.
Test: After two decisions are made for me, the board lists both with their reasons, and typing one undo line reverses that decision.

DEL-3.6 Standing rules answer a class of decisions. I can set a rule once, in my own words, that answers every decision of one kind: for example, which plan breaks the operation may accept, a release deadline after which unfinished work moves to the next release, or how far a goal's budget may be extended. A standing rule counts as my words for every case it covers, the record tool accepts it for each use, and every use is listed in the next check-in with what it decided. Only my words make, change or end a rule, and no rule covers the fixed list in DEL-3.1.
Metric: Questions to me that an existing standing rule answers. Target 0. Today: not counted; on 2026-11-22 the record tool would not let one record serve more than one use.
Test: With a standing rule for low-risk breaks set, two goals hit such a break: both are accepted under the rule with no question to me, both show in the next check-in, and a break on the DEL-3.1 list still waits.

DEL-3.7 One line I type covers every record it names. When my line names features, goals or pages, it is recorded once, covering all of them, so the record tool never refuses it for missing coverage, and one line can mark several features. I never type the same words twice.
Metric: Lines I type that the record tool refuses for coverage, or that I had to retype. Target 0. Today: four on 2026-11-22 (two refused, two retyped).
Test: A line naming two features and one goal marks both features reviewed and covers the goal, with one record and no refusal.

DEL-3.8 A limit moves work; it doesn't stop it. When a goal reaches its time budget, or a release reaches its deadline, the loop follows the standing rule for it (extend once, or move the unfinished work to the next release) and says so, instead of halting until I answer. With no rule set, it asks once, early, before the limit is reached.
Metric: Goals halted at a limit waiting for me. Target 0. Today: one on 2026-11-22 (the file-limit fix at 257 of 240 minutes).
Test: A goal reaches 100% of its budget with an "extend once" rule set: it extends, records it, and goes on. With no rule, it asked me at 80%.

DEL-3.9 The machines never go deaf. Each machine's operation session keeps reaching its workers without my typing on that machine. If something pauses its messages (a message cap, a loop guard, a lost link), the board shows it within one check-in, with the exact step that clears it.
Metric: Minutes a machine's workers were unreachable without the board saying so. Target 0. Today: twice on 2026-11-22, found only when work stalled.
Test: Pause a machine's messages to its workers: the next check-in names the pause and the step that clears it, and work resumes after that step without my retyping anything.

DEL-3.10 Nothing waits silently. Every goal that waits (for a test slot, a session, a review or another goal) shows on the board with what it waits for and since when. Past a set time (a setting, default 30 minutes) the operation acts: it gives the goal the next free slot, or says why not.
Metric: Goals waiting longer than the set time with no action. Target 0. Today: one on 2026-11-22 (a finished goal waited about 12 hours for a test slot).
Test: A goal waits 31 minutes for a slot: the board shows the wait, and the operation either schedules it or records why it can't.
