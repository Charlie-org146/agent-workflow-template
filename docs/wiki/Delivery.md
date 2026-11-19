<!-- workflow-docs -->
# Delivery

Milestone: https://github.com/jcl2018/agent-workflow-template/milestone/1

Review: **Unreviewed** <!-- kept v2-health-green@72bcc265 -->

How to use: [How-to-use-Delivery](How-to-use-Delivery)

## Problem
- I have more changes to make than time to babysit them: I want to hand over one sentence and walk away.
- Without a loop, a change stalls at whatever step I stopped watching: no review, no tests, no release.
- I need every change to arrive the same way: reviewed, tested, documented and released, with a record of what happened.

## Requirements

### Functional
- DEL-1: **Reviewed 2026-11-19** The loop <!-- reviewed c440f7e8 -->
  - I give one sentence and its done lines, and a worker runs it unattended through freeze, idea, plan, build, review, qa, ship, pull request and release.
  - Each step maps to a skill I choose.
  - It won't start until the flow is set up.
  - Review is the only gate a person has to pass.
- DEL-2: **Reviewed 2026-11-19** Done lines are frozen <!-- reviewed b52a8a69 -->
  - Done lines can't change once the goal starts; a change means a new goal.
- DEL-3: **Reviewed 2026-11-19** It only stops for me when it must <!-- reviewed a1527d67 -->
  - A decision that is mine waits under Needs you, or is auto-approved and logged where the repo allows.
  - Plan and review run at full depth unless the repo or I choose condensed.
  - Tests never shrink.
- DEL-4: **Reviewed 2026-11-19** The pull request is the record <!-- reviewed 178f325a -->
  - Every pull request carries the done lines, the plan, how to verify by hand, and each step's result.
- DEL-17: **Reviewed 2026-11-19** A goal's ETA is a hard limit <!-- reviewed 6312b8c9 -->
  - Every goal records an ETA when it is frozen.
  - Past it, the goal finishes its current step, starts no new one, and I choose: ship now, extend once, or defer.
  - Decisions a goal can foresee are asked once, up front, each with a recommendation.
  - Time spent waiting for a queue, for memory or for me does not count.
- DEL-18: **Reviewed 2026-11-19** Everything goes through a goal <!-- reviewed 6a0a9551 -->
  - Every change to a repo's main branch arrives through a goal: its pull request and its release commit.
  - Nothing else writes to main, and health's Traceability group flags a commit on main that no goal accounts for.
- DEL-19: **Reviewed 2026-11-19** Every goal serves a requirement <!-- reviewed 4769ca73 -->
  - A goal is frozen only when it names the Reviewed requirement it builds, fixes or keeps true.
  - Work that no requirement covers starts as a goal that changes the PRD, with the new text in its done lines and my approval; the build follows as a second goal.
  - A goal that names none is refused at freeze, and health's Traceability group flags any that slipped through.

### Non-functional
- DEL-7: **Reviewed 2026-11-19** It survives failure <!-- reviewed 0d16d801 -->
  - A failed step is retried, and after three failed tries the goal stops with a reason.
  - A stopped or crashed goal resumes from its last recorded step.
  - Past its time or token budget a goal starts no new step and waits under Needs you; only my recorded words raise a limit.
  - A step that fails because its session or tool is unusable restarts in a fresh session with its notes.
- DEL-9: **Reviewed 2026-11-15** Nothing private ships <!-- reviewed e53156c1 -->
  - Every commit and pull request passes the private-name scan before it is pushed.
  - The list may scope a line to public repos (`@public REGEX`) or to named repos (`@repos=a,b REGEX`); a line with no scope applies to every repo.
- DEL-12: **Reviewed 2026-11-13** Windows-safe on merge <!-- reviewed b8e35707 -->
  - A pull request that adds a POSIX-only call without its guard (fcntl, os.getuid, os.killpg, signal.SIGHUP, os.kill(pid, 0)) fails its lane, so main cannot break native Windows unseen.
  - A long pull request body, issue text or release notes goes to gh in a file (`--body-file`, `--notes-file`), never on the command line, so a pull request with a body over 32,000 characters opens on native Windows.
- DEL-14: **Reviewed 2026-11-19** Every goal feeds back what it found <!-- reviewed c6dd98cb -->
  - When a goal ships, each finding it did not fix is filed once: a break of a Reviewed requirement as an issue labelled defect, and an improvement, idea or saving as an issue labelled backlog on its feature's Backlog milestone.
- DEL-16: **Reviewed 2026-11-19** Each step runs on the agent I pick <!-- reviewed b7211537 -->
  - A private setting maps each step and goal size to an agent profile.
  - A missing or signed-out agent falls back to the default with a warning.
  - The run record names the agent, model and tokens of every step.

## Non-goals
- It doesn't decide what to build.
- It never changes a done line once started.
- It doesn't run several goals at once (Monitoring does).

## Success metrics
- Every merged pull request carries its done lines, plan, verify steps and step results.
- A goal that fails three tries stops and says why.
- No goal merges while a wiki page its own diff made stale is still stale. Routing subprocesses disable Git and GitHub terminal prompts so unattended commands fail instead of waiting for input.

## Revisions

### Retired

- DEL-10: moved to MCH-8
- DEL-11: moved to MCH-8
- DEL-13: moved to REL-12
- DEL-15: moved to REL-13
- DEL-5: moved to REL-10
- DEL-6: merged into DEL-3
- DEL-8: merged into DEL-7

### DEL-1

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | The loop <br> I give one sentence and its done lines, and a worker runs it unattended through freeze, idea, plan, build, review, qa, ship, pull request and release. <br> Each step maps to a skill I choose. <br> It won't start until the flow is set up. <br> Review is the only gate a person has to pass. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-08 | The loop <br> I give one sentence and its done lines; a worker runs it unattended. <br> Steps, in order: freeze, idea, plan, build, review, qa, ship, pull request, release. <br> Review is the only gate. <br> Each step maps to a skill I choose, in a private setting outside the repo. <br> It won't start without the flow set up, and stops with a reason after 3 failed tries. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-2

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Done lines are frozen <br> Done lines can't change once the goal starts; a change means a new goal. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-08 | Frozen done lines <br> Done lines can't change once the goal starts; a change means a new goal. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-3

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | It only stops for me when it must <br> A decision that is mine waits under Needs you, or is auto-approved and logged where the repo allows. <br> Plan and review run at full depth unless the repo or I choose condensed. <br> Tests never shrink. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-08 | Decisions <br> A decision for me waits under Needs you, or, where the repo allows, is auto-approved and logged. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-4

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | The pull request is the record <br> Every pull request carries the done lines, the plan, how to verify by hand, and each step's result. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-08 | The pull request <br> Carries the done lines, the plan, how to verify by hand, and each step's result. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-5

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Release <br> Every goal ends with release. With auto_merge on it is fully automatic: it bumps the version, writes the release note, refuses to merge while a page its own changes made stale is still stale (a page left stale by another goal's commit is reported as a finding, and health still flags it), runs my routines, merges, publishes the release and the wiki. With auto_merge off it makes a draft release for me to publish and merges nothing. Any failure shows under Needs you. | v2 regroup: moved:REL-10 | o47: "Yes, start it end." |
| r1 | 2026-11-14 | Release <br> Every goal ends with release. With auto_merge on it is fully automatic: it bumps the version, writes the release note, refuses to merge while a page its own changes made stale is still stale (a page left stale by another goal's commit is reported as a finding, and health still flags it), runs my routines, merges, publishes the release and the wiki. With auto_merge off it makes a draft release for me to publish and merges nothing. Any failure shows under Needs you. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-6

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Review depth fits the goal <br> Plan and review run at full depth by default (`review_depth: full`); a condensed plan and review happens only when `review_depth: condensed`, and I can override it per goal. Tests never shrink: every goal runs its test lane, the affected rows within the test budget (REG-7). | v2 regroup: merged:DEL-3 | o47: "Yes, start it end." |
| r1 | 2026-11-13 | Review depth fits the goal <br> Plan and review run at full depth by default (`review_depth: full`); a condensed plan and review happens only when `review_depth: condensed`, and I can override it per goal. Tests never shrink: every goal runs its test lane, the affected rows within the test budget (REG-7). | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-7

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | It survives failure <br> A failed step is retried, and after three failed tries the goal stops with a reason. <br> A stopped or crashed goal resumes from its last recorded step. <br> Past its time or token budget a goal starts no new step and waits under Needs you; only my recorded words raise a limit. <br> A step that fails because its session or tool is unusable restarts in a fresh session with its notes. | v2 rewrite: changed: last sentence is new (the planning-tool risk). | o47: "Yes, start it end." |
| r1 | 2026-11-10 | Resumable <br> A stopped or crashed goal resumes from its last recorded step, never from the start. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-8

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Budgeted <br> Each goal has a time and token budget, and going over shows on the board. <br> Each review and ship step has a time limit, a setting no lower than 15 minutes; a step that reaches it finishes with what it has done, records what it left, and the goal goes on instead of restarting. <br> A lane that stops at its preparation budget is recorded on the goal with the part that ran long, and the board and health list it beside the step and test budget hits. <br> A goal past its time budget (`time_budget_minutes`, active time) or its `token_budget` starts no new step, and a merge-and-rerun round past `max_merge_rounds` (default 8) is refused: the goal waits under Needs you, and only the operation session raises a limit. | v2 regroup: merged:DEL-7 | o47: "Yes, start it end." |
| r1 | 2026-11-15 | Budgeted <br> Each goal has a time and token budget, and going over shows on the board. <br> Each review and ship step has a time limit, a setting no lower than 15 minutes; a step that reaches it finishes with what it has done, records what it left, and the goal goes on instead of restarting. <br> A lane that stops at its preparation budget is recorded on the goal with the part that ran long, and the board and health list it beside the step and test budget hits. <br> A goal past its time budget (`time_budget_minutes`, active time) or its `token_budget` starts no new step, and a merge-and-rerun round past `max_merge_rounds` (default 8) is refused: the goal waits under Needs you, and only the operation session raises a limit. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-9

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-15 | Nothing private ships <br> Every commit and pull request passes the private-name scan before it is pushed. <br> The list may scope a line to public repos (`@public REGEX`) or to named repos (`@repos=a,b REGEX`); a line with no scope applies to every repo. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-10

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A goal started on another machine can be adopted <br> `goal.py adopt SLUG`, run in the goal's worktree on branch `loop/SLUG`, creates this machine's run record at step qa from the pushed branch, its frozen goal file and its open pull request; idea, plan and review are recorded `done on another machine`. <br> qa, ship and the pull request are never recorded from another machine's evidence: they run again here before release. <br> A record here that is running with no pid and no recorded step (a stale, never-started one) is replaced and the replacement logged; a record with a pid, a recorded step or a finished status makes adopt refuse. | v2 regroup: moved:MCH-8 | o47: "Yes, start it end." |
| r1 | 2026-11-13 | A goal started on another machine can be adopted <br> `goal.py adopt SLUG`, run in the goal's worktree on branch `loop/SLUG`, creates this machine's run record at step qa from the pushed branch, its frozen goal file and its open pull request; idea, plan and review are recorded `done on another machine`. <br> qa, ship and the pull request are never recorded from another machine's evidence: they run again here before release. <br> A record here that is running with no pid and no recorded step (a stale, never-started one) is replaced and the replacement logged; a record with a pid, a recorded step or a finished status makes adopt refuse. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-11

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Adopt never trusts an unpushed branch <br> A branch that is not on origin, a worktree missing its commits, a goal with no done line or no open pull request is refused with one line, and no run record is written. | v2 regroup: moved:MCH-8 | o47: "Yes, start it end." |
| r1 | 2026-11-13 | Adopt never trusts an unpushed branch <br> A branch that is not on origin, a worktree missing its commits, a goal with no done line or no open pull request is refused with one line, and no run record is written. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-12

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-13 | Windows-safe on merge <br> A pull request that adds a POSIX-only call without its guard (fcntl, os.getuid, os.killpg, signal.SIGHUP, os.kill(pid, 0)) fails its lane, so main cannot break native Windows unseen. <br> A long pull request body, issue text or release notes goes to gh in a file (`--body-file`, `--notes-file`), never on the command line, so a pull request with a body over 32,000 characters opens on native Windows. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-13

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | A review hold before auto merge <br> Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows a merge waiting on review. | v2 regroup: moved:REL-12 | o47: "Yes, start it end." |
| r1 | 2026-11-13 | A review hold before auto merge <br> Where a review hold is set, the release step merges only after the operation session records that it has read the diff, and the board shows a merge waiting on review. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-14

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Every goal feeds back what it found <br> When a goal ships, each finding it did not fix is filed once: a break of a Reviewed requirement as an issue labelled defect, and an improvement, idea or saving as an issue labelled backlog on its feature's Backlog milestone. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-13 | Leftover findings are filed by kind at ship <br> When a goal ships, each finding it did not fix is filed once. A break of a Reviewed requirement inside the goal's touches is fixed in place; outside them it is an open issue labelled `defect`. An improvement, idea or saving is an issue labelled `backlog` on its feature's milestone "Backlog: <Feature>" ("Backlog: Other" when it fits no feature). Filing writes to GitHub only with `--live`, which the goal passes after ship is recorded, and a finding already filed is not filed again. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-15

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Fast merge queue. PRs merge one after another, but each waits only as long as needed. <br> A pr lane that runs again after main moved reruns only the rows both the goal's diff and main's new commits reach; a row only main's new commits reach keeps its earlier result. <br> Goals at pr queue behind each other only when their touches overlap; goals with disjoint touches run their lanes at once. <br> Three or four ready pull requests with disjoint touches are verified together and merged in one go, and a failing batch splits to name the culprit. | v2 regroup: moved:REL-13 | o47: "Yes, start it end." |
| r1 | 2026-11-14 | Fast merge queue. PRs merge one after another, but each waits only as long as needed. <br> A pr lane that runs again after main moved reruns only the rows both the goal's diff and main's new commits reach; a row only main's new commits reach keeps its earlier result. <br> Goals at pr queue behind each other only when their touches overlap; goals with disjoint touches run their lanes at once. <br> Three or four ready pull requests with disjoint touches are verified together and merged in one go, and a failing batch splits to name the culprit. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-16

| rev | date | text | why | approved |
|---|---|---|---|---|
| r2 | 2026-11-18 | Each step runs on the agent I pick <br> A private setting maps each step and goal size to an agent profile. <br> A missing or signed-out agent falls back to the default with a warning. <br> The run record names the agent, model and tokens of every step. | v2 rewrite text (prd-rewrite-to-10) | o47: "Yes, start it end." |
| r1 | 2026-11-18 | Each step runs on the agent the config picks <br> A private config maps each step and each goal size to an agent profile (a command, a model and a cost per token): heavy work on Claude, cheap work on Codex or any other agent added as one more profile entry, with no code change. <br> Setup asks which agents are installed and logged in and writes the profiles; an agent that is missing or logged out falls back to Claude with a one-line warning. <br> Review stays on the heavy profile unless the config routes it by name; the run record names the agent, the model and the tokens of every step. | migration r1; date from its stamp | o30: "Yes, I want this to be implemented in the 2.0, so it's" |

### DEL-17

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | A goal's ETA is a hard limit <br> Every goal records an ETA when it is frozen. <br> Past it, the goal finishes its current step, starts no new one, and I choose: ship now, extend once, or defer. <br> Decisions a goal can foresee are asked once, up front, each with a recommendation. <br> Time spent waiting for a queue, for memory or for me does not count. | migration r1; date from the run day | o47: "Yes, start it end." |

### DEL-18

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Everything goes through a goal <br> Every change to a repo's main branch arrives through a goal: its pull request and its release commit. <br> Nothing else writes to main, and health's Traceability group flags a commit on main that no goal accounts for. | migration r1; date from the run day | o47: "Yes, start it end." |

### DEL-19

| rev | date | text | why | approved |
|---|---|---|---|---|
| r1 | 2026-11-18 | Every goal serves a requirement <br> A goal is frozen only when it names the Reviewed requirement it builds, fixes or keeps true. <br> Work that no requirement covers starts as a goal that changes the PRD, with the new text in its done lines and my approval; the build follows as a second goal. <br> A goal that names none is refused at freeze, and health's Traceability group flags any that slipped through. | migration r1; date from the run day | o47: "Yes, start it end." |

## Tests

| Test | Kind | Guards | Checks | Last result |
|---|---|---|---|---|
| [no-done-line-refused](Tests#t-no-done-line-refused) | requirement | DEL-1 | Given a goal with no done line, when it is started, then it is refused. | PASS 2026-11-19 |
| [no-flow-refused](Tests#t-no-flow-refused) | requirement | DEL-1 | Given no skill flow is set, when a goal is started, then it does not start. | PASS 2026-11-19 |
| [stop-after-3-tries](Tests#t-stop-after-3-tries) | requirement | DEL-1 | Given a goal, when three tries fail, then the goal stops and files a finding. | PASS 2026-11-09 |
| [pr-needs-flow](Tests#t-pr-needs-flow) | requirement | DEL-1 | Given a flow step not yet done, when a pull request is opened, then it is refused. | PASS 2026-11-09 |
| [starts-at-idea](Tests#t-starts-at-idea) | requirement | DEL-1 | Given a new goal, when it starts, then it starts at the idea step. | PASS 2026-11-09 |
| [steps-through-flow](Tests#t-steps-through-flow) | requirement | DEL-1 | Given a step reply, when it is recorded, then it is accepted only if the flow ran that step. | PASS 2026-11-09 |
| [no-prompts](Tests#t-no-prompts) | requirement | DEL-1 | Given any tool, when it runs, then it never waits on a terminal prompt. | PASS 2026-11-18 |
| [defect-flow-steps](Tests#t-defect-flow-steps) | requirement | DEL-1 | Given the flow, when it is checked, then it has no checks step and every step can be mapped, with a default suite and overrides. | PASS 2026-11-12 |
| [guards-extra](Tests#t-guards-extra) | requirement | DEL-1 | Given a stopped or waiting goal, when answer, record or a second reservation comes in, then answer refuses a stopped goal, a waiting goal can't advance, and two goals can't take one session. | PASS 2026-11-10 |
| [ptb-mend](Tests#t-ptb-mend) | requirement | DEL-1 | Given main moved only in the regression rows or a Tests page, when goal.py pr merges it, then the merge is mended and the PR goes on with no try spent, while a code-file conflict is reported and not counted against max_tries (it has its own cap, max_moved). | PASS 2026-11-12 |
| [ptb-dead-lane](Tests#t-ptb-dead-lane) | requirement | DEL-1 | Given a lane that ended with no exit status (killed from outside), when goal.py pr or a record sees it, then it reruns without spending a try, at most 3 times, and a real failure still spends one. | PASS 2026-11-12 |
| [ptb-plain-paths](Tests#t-ptb-plain-paths) | requirement | DEL-1 | Given a finding or stop text that carries an absolute path, when goal.py writes it, then the finding, the journal and findings.md hold no absolute path and keep the row id and file name. | PASS 2026-11-12 |
| [pr-moved-uncounted](Tests#t-pr-moved-uncounted) | requirement | DEL-1 | Given a goal whose pr try was lost to main moving, when it happens five times, then tries and max_tries stay unchanged and each says TRY NOT COUNTED; the sixth counts as an ordinary failed try. | PASS 2026-11-15 |
| [lane-memory-not-counted](Tests#t-lane-memory-not-counted) | requirement | DEL-1 | Given a lane that gave up waiting for memory, when the goal records the failed try, then no counted try is used and a real failure still costs one. | not run |
| [frozen-done-lines](Tests#t-frozen-done-lines) | requirement | DEL-2 | Given a running goal, when a frozen done line is changed, then the goal stops. | PASS 2026-11-09 |
| [pending-waits](Tests#t-pending-waits) | requirement | DEL-3 | Given a step that leaves a decision for the owner, when it ends, then the goal stops and waits. | PASS 2026-11-19 |
| [auto-approved](Tests#t-auto-approved) | requirement | DEL-3 | Given an auto-approved step, when it ends, then it is logged and nothing waits. | PASS 2026-11-09 |
| [depth-condensed-refused](Tests#t-depth-condensed-refused) | requirement | DEL-3 | Given review_depth full, when a plan or review reply says it ran condensed, then it is refused with no try used. | PASS 2026-11-18 |
| [depth-auto-approve-gate](Tests#t-depth-auto-approve-gate) | requirement | DEL-3 | Given review_depth full and auto-approve on, when a condensed review leaves a gate, then it is refused, not approved. | PASS 2026-11-18 |
| [depth-markers](Tests#t-depth-markers) | requirement | DEL-3 | Given private evidence markers, when a full review reply lacks one, then it is refused with no try used, without showing the marker. | PASS 2026-11-18 |
| [depth-recorded](Tests#t-depth-recorded) | requirement | DEL-3 | Given the default setting, when a goal runs its steps, then every recorded step names the depth it ran. | PASS 2026-11-18 |
| [depth-condensed-when-set](Tests#t-depth-condensed-when-set) | requirement | DEL-3 | Given review_depth condensed on the base branch, when a review runs condensed, then it is recorded as condensed. | PASS 2026-11-18 |
| [depth-base-branch](Tests#t-depth-base-branch) | requirement | DEL-3 | Given review_depth full on the base branch, when a worker sets condensed in its own worktree, then it is still held to full. | PASS 2026-11-18 |
| [depth-loop-flow](Tests#t-depth-loop-flow) | requirement | DEL-3 | Given markers in the default flow file, when LOOP_FLOW points elsewhere, then the markers still apply. | PASS 2026-11-18 |
| [del6-depth-by-size](Tests#t-del6-depth-by-size) | requirement | DEL-3 | Given review_depth condensed, when a small goal (up to 3 done lines, one area) and a larger goal run their plan and review, then the small one is told to run condensed and the larger one full. | not run |
| [del6-large-held-full](Tests#t-del6-large-held-full) | requirement | DEL-3 | Given review_depth condensed and a goal touching two areas, when its review replies condensed, then it is refused with no try used. | not run |
| [del6-owner-override](Tests#t-del6-owner-override) | requirement | DEL-3 | Given a large goal, when the owner sets its depth to condensed with goal.py set, then a condensed review is recorded; a worker can't set it. | not run |
| [del6-full-lane](Tests#t-del6-full-lane) | requirement | DEL-3 | Given a goal whose review ran condensed, when its qa step runs, then it runs the same land regression lane as a full-depth goal, with no row dropped for depth. | not run |
| [cut-needs-verify](Tests#t-cut-needs-verify) | requirement | DEL-4 | Given no Verify by hand steps, when a release is cut, then it is refused. | PASS 2026-11-18 |
| [pr-body-criterion](Tests#t-pr-body-criterion) | requirement | DEL-4 | Given a pull request, when its body is written, then it carries the goal, the done lines, the verify steps and each step's result. | PASS 2026-11-12 |
| [depth-in-pr-body](Tests#t-depth-in-pr-body) | requirement | DEL-4 | Given a goal whose steps are recorded, when its pull request opens, then the body lists every step with its depth. | PASS 2026-11-10 |
| [private-checks-stop](Tests#t-private-checks-stop) | requirement | DEL-4 | Given a required check no local status can satisfy, when the pr step opens the pull request, then it names that check and stops first (#4537). | not run |
| [eta-freeze](Tests#t-eta-freeze) | requirement | DEL-17 | Given a goal being frozen, when its fields and goal file are built, then they hold a hard ETA in whole minutes (at least 30) with its basis, and the goal file has an ETA line next to the done lines. | not run |
| [eta-gate](Tests#t-eta-gate) | requirement | DEL-17 | Given a goal that has spent its ETA, when a step or pr is asked for, then it is refused with one line naming goal.py set and an owner record, and a goal inside its ETA starts its step. | not run |
| [eta-needs-you](Tests#t-eta-needs-you) | requirement | DEL-17 | Given a goal past its ETA, when the refusal is recorded, then the goal waits with three choices (ship now, extend, defer) as an owner question that full auto never answers, so the check-in lists it under Needs you. | not run |
| [eta-owner-record](Tests#t-eta-owner-record) | requirement | DEL-17 | Given goal.py set with an ETA extension or a budget raise, when no owner-words record covers the goal or the record was used before, then it is refused and nothing changes; with a fresh covering record it is accepted. | not run |
| [eta-ship-defer](Tests#t-eta-ship-defer) | requirement | DEL-17 | Given a goal past its ETA and an owner record, when the owner chooses ship now or defer, then ship now records the steps left as skipped and lets the pull request go on, and defer retires the goal for the next release. | not run |
| [eta-checkin](Tests#t-eta-checkin) | requirement | DEL-17 | Given goals with and without an ETA, when the check-in builds its All sessions table, then each goal's cell shows its ETA clock time, ETA passed, or no ETA. | not run |
| [eta-health-missing](Tests#t-eta-health-missing) | requirement | DEL-17 | Given a live goal with no ETA, when health runs, then it warns (eta-missing), and the rule's negative control fires. | not run |
| [eta-health-extended](Tests#t-eta-health-extended) | requirement | DEL-17 | Given an ETA extension whose owner-words record is missing or does not cover the goal, when health runs, then it fails (eta-extended), and the rule's negative control fires. | not run |
| [eta-health-overrun](Tests#t-eta-health-overrun) | requirement | DEL-17 | Given a goal past its ETA that is not waiting under Needs you, when health runs, then it fails (eta-overrun), and the rule's negative control fires; a goal waiting for the owner's choice is clean. | not run |
| - | requirement | DEL-17 | no passing test | not enforced |
| - | requirement | DEL-18 | no passing test | not enforced |
| - | requirement | DEL-19 | no passing test | not enforced |
| [del8-floor-step](Tests#t-del8-floor-step) | requirement | DEL-7 | Given step_budget_minutes under 15, when a step reads it, then it is refused with a fix line. | PASS 2026-11-18 |
| [del8-step-recorded](Tests#t-del8-step-recorded) | requirement | DEL-7 | Given a step that hit its budget, when the goal's record is read, then it names the step and what it left. | not run |
| [del8-session-budget](Tests#t-del8-session-budget) | requirement | DEL-7 | Given a step run by the worker session, when it is asked for, then its instructions carry the step budget. | not run |
| [del8-session-overrun](Tests#t-del8-session-overrun) | requirement | DEL-7 | Given a session-run step that took longer than its budget, when it is recorded, then the overrun and what it left are kept. | not run |
| [del8-board](Tests#t-del8-board) | requirement | DEL-7 | Given a step or test run that hit its budget, when the monitoring report runs, then it lists the hit and what was left. | not run |
| [del8-health](Tests#t-del8-health) | requirement | DEL-7 | Given a step or test run that hit its budget, when health runs, then it lists the hit and what was left. | not run |
| [del8-prep-board](Tests#t-del8-prep-board) | requirement | DEL-7 | Given a lane that hit the preparation budget, when the monitoring report and health run, then both list the hit and the part that ran long in the same words as budget.py. | not run |
| [del7-kill-resume](Tests#t-del7-kill-resume) | requirement | DEL-7 | Given a goal whose review was killed mid-step, when it is resumed, then it reruns review from its recorded plan, never from the start, and moves on to qa. | not run |
| [del7-recorded-refused](Tests#t-del7-recorded-refused) | requirement | DEL-7 | Given a goal with recorded steps, when a recorded step is run again without --again, then it is refused with no try and names the step to resume from. | not run |
| [del8-goal-budget](Tests#t-del8-goal-budget) | requirement | DEL-7 | Given a repo with a time and token budget, when a goal is frozen, then the goal carries both budgets. | not run |
| [del8-board-over](Tests#t-del8-board-over) | requirement | DEL-7 | Given a running goal past its time and token budget, when the live board prints, then the goal's budget line says OVER time and OVER tokens. | not run |
| [del8-session-tokens](Tests#t-del8-session-tokens) | requirement | DEL-7 | Given a goal past token_budget whose steps run in a session, when the next step starts, then it is refused (not built: only headless goals are refused today). | not run |
| [held-time-over-still-stops](Tests#t-held-time-over-still-stops) | requirement | DEL-7 | Given a goal whose steps ran past its time budget, when a new step starts, then it is refused with BUDGET_MINUTES. | PASS 2026-11-14 |
| [test-caps-qa-refused](Tests#t-test-caps-qa-refused) | requirement | DEL-7 | Given a repo at max_regression_rows, when a goal adds a row, then qa refuses it with the row counts and the cap (TEST_CAPS); with the suite over max_suite_seconds it refuses with the seconds (owner record o51). | PASS 2026-11-16 |
| [eta-budget-raise](Tests#t-eta-budget-raise) | requirement | DEL-7 | Given goal.py set raising a goal's time or token budget, when no unused owner-words record covers the goal, then it is refused and nothing changes; with one it is accepted and keeps the record, and lowering a budget needs none (hard ETA, DEL-17). | not run |
| [eta-legacy-goal](Tests#t-eta-legacy-goal) | requirement | DEL-7 | Given a goal frozen before ETAs existed, when the owner gives it an ETA with an unused owner-words record, then it runs inside that ETA and is stopped past it like any other goal. | not run |
| [held-charge-idle](Tests#t-held-charge-idle) | requirement | DEL-7 | Given a session silent past the idle limit with no step running, when the minute budget is read through fit.budget_stop, then it is charged no more than the limit until its next step starts, while a step that is running is charged in full. | not run |
| [held-charge-show](Tests#t-held-charge-show) | requirement | DEL-7 | Given a goal with idle time, when goal.py show prints it, then it shows the charged minutes and the wall minutes. | not run |
| [routing-timeout-tree](Tests#t-routing-timeout-tree) | requirement | DEL-7 | Given a routed agent that has started a child and passes its timeout, when routing stops it, then the agent and its child are both gone, and the old subprocess.run(timeout) leaves the child running. | not run |
| [del9-merge-refuses](Tests#t-del9-merge-refuses) | requirement | DEL-9 | Given a pull request whose branch holds a private name, when merge.py runs, then nothing is merged. | PASS 2026-11-12 |
| [del9-scan-sites](Tests#t-del9-scan-sites) | requirement | DEL-9 | Given the delivery, release and monitoring scripts, when any function pushes or writes to GitHub, then it calls the private-name scan first. | not run |
| [del9-lane-part-no-path](Tests#t-del9-lane-part-no-path) | requirement | DEL-9 | Given a lane record whose LANE line ends with a local log path, when the pull request body's lane part is built, then it keeps the LANE line, the before-rows parts and the rows and drops the log path, so the private-name scan does not refuse every pull request from a machine whose home folder is on the list. | not run |
| [windows-safe-posix-names](Tests#t-windows-safe-posix-names) | requirement | DEL-12 | Given a script under skills/*/scripts, when it names fcntl outside the lock shim, os.getuid, os.killpg, os.getpgrp, os.O_NOFOLLOW, signal.SIGHUP, os.kill(pid, 0) or os.WNOHANG with no guard, then the lane fails naming its file and line, and the real tree passes (issue 2871). | not run |
| - | requirement | DEL-12 | no passing test | not enforced |
| [backlog-leftovers-filed](Tests#t-backlog-leftovers-filed) | requirement | DEL-14 | Given a ship reply with FILE defect and FILE backlog lines, when the goal records ship with --live, then a defect is filed on no milestone, backlog items on Backlog: <Feature> or Backlog: Other, and a line holding an email is skipped. | PASS 2026-11-16 FLAKY |
| [backlog-leftovers-once](Tests#t-backlog-leftovers-once) | requirement | DEL-14 | Given leftovers already filed, when ship is recorded again, then nothing is filed twice. | not run |
| - | requirement | DEL-16 | no passing test | not enforced |
| [agent-routing](Tests#t-agent-routing) | workflow | DEL-16 | Given a config that routes build to Codex and review to Claude, when a small goal runs, then build runs through the Codex command, review stays on Claude, the run record names both agents with their tokens, and a missing or write-blocked Codex falls back to Claude with one warning line. | not run |
| [scripts-no-hang](Tests#t-scripts-no-hang) | defect | [#35](https://github.com/jcl2018/agent-workflow-template/issues/35) closed (2026-11-09) | Given a script with no terminal, when it needs a prompt, then it fails with an error instead of hanging. | PASS 2026-11-12 |
| [guards-rule-start](Tests#t-guards-rule-start) | defect | [#147](https://github.com/jcl2018/agent-workflow-template/issues/147) closed (2026-11-11) | Given a reply-format rule added after a step started, when that step is recorded, then the rule doesn't bind it, and a step started after it is refused naming the rule and the release that added it. | PASS 2026-11-10 |
| [guards-no-try](Tests#t-guards-no-try) | defect | [#148](https://github.com/jcl2018/agent-workflow-template/issues/148) closed (2026-11-11) | Given a record refused for format (no DEPTH or STEP line) or a wrong HEAD, when it is refused, then no try is used, the goal keeps running and the fix is printed. | PASS 2026-11-12 |
| [guards-touches-finding](Tests#t-guards-touches-finding) | defect | [#157](https://github.com/jcl2018/agent-workflow-template/issues/157) closed (2026-11-11) | Given a goal that needs more touches, or a finished goal with a finding, when the operation runs goal.py touches or finding, then touches widen with a logged reason and the finished goal is not stopped. | PASS 2026-11-12 |
| [builtin-flow](Tests#t-builtin-flow) | defect | [#47](https://github.com/jcl2018/agent-workflow-template/issues/47) closed (2026-11-11) | Given a flow file whose steps are built-in and no probe, when a goal starts and its steps run, then delivery runs its own routine for each step, and with no flow file it still refuses. | PASS 2026-11-12 |
| [del1-new-here-main-refused](Tests#t-del1-new-here-main-refused) | defect | 3468 | Given the repo's main checkout, when goal.py new --here runs there, then it refuses with one line naming the worktree command. | PASS 2026-11-14 |
| [issue-117-github-touches](Tests#t-issue-117-github-touches) | defect | [#117](https://github.com/jcl2018/agent-workflow-template/issues/117) closed (2026-11-11) | Given a goal touching github:wiki that deletes a file a repo script writes, when it opens its pull request, then the surface is listed and the script is warned about (issue: Goals can't name GitHub-side changes, and nothing warns when a script regenerates what a goal deletes). | not run |
| [depth-marker-rows-4557](Tests#t-depth-marker-rows-4557) | defect | #4557 | Given the review-depth marker rows (depth-on-board, depth-in-pr-body, depth-reference) that printed PASS and still exited non-zero on CI, when test-review-depth.sh runs as a whole, then its last line is ALL PASS (issue 4557). | not run |
| [pr-body-no-checks](Tests#t-pr-body-no-checks) | defect | [PR 62](https://github.com/jcl2018/agent-workflow-template/pull/62) merged (2026-11-09) | Given a pull request, when its body is written, then it says nothing about checks and lists each step's result. | PASS 2026-11-12 |
| [issue-38-verdicts](Tests#t-issue-38-verdicts) | defect | [#38](https://github.com/jcl2018/agent-workflow-template/issues/38) closed (2026-11-11) | Given a step reply with VERDICT lines, when the goal opens its pull request, then each verdict is listed under its step (issue: Record the Codex judge and idea-run results). | not run |
| [pr-body-by-file](Tests#t-pr-body-by-file) | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | Given a lane that lists hundreds of rows, when goal.py opens the pull request, then the body goes in a file, not on the command line, which Windows caps. | PASS 2026-11-13 |
| [stop-takes-tree](Tests#t-stop-takes-tree) | defect | [#1396](https://github.com/jcl2018/agent-workflow-template/issues/1396) closed (2026-11-12) | Given a step or child stopped for a timeout or a mend, when it is stopped on any platform, then its whole process tree goes with it. | PASS 2026-11-12 |
| [held-time-3878](Tests#t-held-time-3878) | defect | [#3878](https://github.com/jcl2018/agent-workflow-template/issues/3878) closed (2026-11-15) | Given a goal held 772 minutes and active 20 minutes, when a new step starts at a 300 minute budget, then it is not refused (#3878). | PASS 2026-11-14 |
| [pr-body-no-home-3841](Tests#t-pr-body-no-home-3841) | defect | [#3841](https://github.com/jcl2018/agent-workflow-template/issues/3841) closed (2026-11-14) | Given lane records that name a Unix or Windows home folder, when goal.py pr builds the lane part of the pull request body, then no home folder or user name is in it (issue 3841). | PASS 2026-11-14 |
| [prd-no-dunder-import-3800](Tests#t-prd-no-dunder-import-3800) | defect | [#3800](https://github.com/jcl2018/agent-workflow-template/issues/3800) closed (2026-11-15) | Given the scripts under skills/*/scripts (prd.py and render.py relock and render through importlib), when the package Safety rule scans them, then none holds __import__ (issue 3800). | PASS 2026-11-16 |
