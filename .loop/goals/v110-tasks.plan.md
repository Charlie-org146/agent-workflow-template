# Plan: v110-tasks, tasks in DEL-23's format and the task list on the check-in and the board

## Implementation plan 

Goal file `.loop/goals/v110-tasks.md` (five frozen done lines). Scheduling is out. No new file under `skills/`. Scripts are measured in bytes (health.py size_rows, 20,480, CRLF normalised) but stricter caps are enforced by existing rows: test-hands-off.py:275 caps graph.py at 19,000 (13 bytes of room) and checkin.py at 19,495 (499 bytes; test-release-gate.py:335 holds the same); board.py and board_page.py keep 19,000 (test-board.sh:256). The usable room is therefore: board_lines.py about 1,525 and live_board.py about 1,538 (no stricter cap found for either: to be re-verified by grep before the build), checkin.py at most 499, graph.py none. Behavior-preserving trims of existing code in board_lines.py and live_board.py are allowed to make room, only if every existing toy that reads them still passes; nothing else is trimmed. Every touched script is re-measured after each edit.

### 1. Briefs (done line 1)
`.loop/tasks/<slug>.md`, one per task, read by line:
```
# <task name>
- Feature: <ID>
- Release: <vX.Y.Z, or "patch (v1.1.x)", or "none">
- Goals: <live goal slugs, comma separated; empty if none yet>
- Needs: <task slugs; optional>
- Replaced by: <task slug; optional>
- Source: <frozen page and its sha256 prefix and the owner word, or the issue / goal file>
## Purpose
<quoted>
## Done when
- <quoted lines, or "(none in the source)">
```
Eleven briefs: v110-text, v110-tasks, migrate-features-2, v110-impl, fix-5727-smoke-env-2, grd21-cap-lift, v120-text, v120-del3, v120-del22, v120-set1, service-repo-migration. Text is quoted only from what the sources hold (B7): v110-text: "written into the docs exactly as on this page, with your review marks"; v110-tasks: "the board shows the task list by name with each task's goals and progress" and the v1.1.0 release-level done-when; migrate-features-2: "already built and tested; finished under its frozen done lines"; v110-impl: "Every test case passes, and no existing test turns red"; the v120 tasks: each feature's Expected change and its Test lines from the v1.2.0 page (marked not frozen: the page is a draft, o715 is the owner word named in the brief). fix-5727: the bug line from the page plus the issue body read once with `gh issue view` and quoted; grd21-cap-lift: "the file limit raised to 200 (o718, o719)" and the owner's words; where no text exists the Done when holds "(none in the source)". The parked migration quotes the service repo as "the service repo" (the same swap doc27-28-text-5 made, o711); its release is "none". Patches say "patch (v1.1.x)". Goals names the `-2` goal where both a goal and its `-2` have records (fix-5727-smoke-env-2, migrate-features-2, v120-del3-2 only if its record is the live one; the choice is checked against the run records and written down in Source). `Goals` and `Replaced by` are the only two lines that change after the freeze (a goal is added when it starts; a replacement is named when a new task supersedes this one); every other line is frozen by the owner's word. Every quoted line is verified verbatim against the stripped text of its source page by a one-off check run at build time (not shipped); a line that does not match is not written. The four v120 briefs record in Source: the v1.2.0 page (draft of 2026-11-21 09:42, sha256 prefix f44f0d5c73783626) and the owner word o715, exactly as the page says; they are not called frozen. The parked migration is shown as queued with release none (its Purpose says it is parked); briefs name only live goals (never a retired one). Where both a goal and its `-2` have records, the brief names the one whose record is not retired and newest, and Source says so. `Needs`: v120-del22 and v120-set1 need v120-del3 ("DEL-3 is built first"); no other Needs (the v1.2.0 to v1.1.0 order is release-level, not a start order; the cut order is not a start order).

### 2. The list (done lines 2, 3)
Parser in `board_lines.py` (`task_rows(root)`: reads briefs; an unreadable brief gives a one-line note, a brief missing a part is flagged incomplete). State in `board_lines.py` `tasks(rows, runs, at, root, gone=())` (graph.py is untouched: 13 bytes of room under its cap) (root is passed explicitly to `left_time`, which otherwise defaults to the working directory and could read another repo's goal files; a toy runs it with the working directory outside the fixture), pure; it uses graph.merged and a lazy import of board_status for left_time (board_lines already lazy-imports live_board the same way). `runs` is what the caller already holds (live_board.load and gather drop retired records, so a goal with no record is "not started"; briefs never name retired goals). A goal is finished when `graph.merged(run)` or its slug is in `gone` (the board passes the PR-merged set it already computes in live_board.render; the check-in passes the merged slugs its own gather() already resolved from the same states, so both surfaces agree and no extra GitHub lookup is made; verified at build). A named goal with no run record, no goal file under `.loop/goals/` and no queue entry is flagged "unknown goal: check the Goals line of <brief>"; a goal whose run is retired (live_board.run_files lists it) is flagged "retired: name its replacement on the Goals line". A record with status queued (written by watch.freeze before work starts) counts as not started. Any other record (running, waiting, failed, stopped, held, done-but-unmerged) is in flight. Precedence, one table, no recursion: replaced > done > running > waiting > queued. Pass 1 gives each task its goal state (replaced if `Replaced by`; done if at least one goal and all finished; running if any goal in flight; otherwise not started). Pass 2 turns a not-started task into waiting when any `Needs` is unmet, judged on the Needs task's pass-1 state (done means its goals are finished, whatever it waits on itself); a task whose goals already run stays running. Needs are resolved first through `Replaced by` (at most five hops; a longer chain or a replacement naming no brief is a named problem, "bad replacement"), then `board_lines.cycled` runs over those effective edges; unmet means: not done, no brief, bad replacement or cycle; the reason is shown: "waiting: needs <name>", "no brief" or "cycle". A goal named by two tasks is counted in both and flagged. ETA, stated: the time left of the slowest in-flight goal (goals run side by side) through `board_page.span`; "?" if an in-flight goal has no estimate; "awaiting merge" if every in-flight goal has status done (left_time returns 0 for those); "-" if nothing is in flight. Unstarted goals add nothing.

### 3. Shown (done line 4)
Scope of repos: the Tasks section covers the repo the check-in or board runs in; followed repos are not flattened in (their own check-ins show theirs); stated on the how-to page. Briefs are ordinary committed files merged by a goal (operation's checkout cannot edit the repo); the check-in reads the checkout it runs in, so a brief appears once its goal's branch is merged there.
`live_board.task_lines(rows)` (live_board already holds plain, fit, FLOW and current): one line per task by name: `<name>: <state>, <k> of <n> goals finished, <ETA>`, then an indented line per goal: `<slug> <label>`, label being: "finished" if merged; "awaiting merge" if status done but unmerged; "not started" if no record or status queued; otherwise `lb.FLOW[lb.current(run)]` (the source the All sessions table uses; board_log.current alone returns idea for a queued record and release for a done one). Every name and note passes `re.sub(r"[\x00-\x1f\x7f|]", " ", s)` then a length cut (lb.plain alone does not strip control characters or pipes). No `|` rows; none of the words merged, total, hist, closed, milestone, tokens, done lines, longest, Roadmap, Needs you, level N in the board text (test-live-board line 72). Prints nothing when `.loop/tasks` is absent or empty. Check-in: a `Tasks` section of bullet lines right after the All sessions table (lb.fit already wraps the check-in). Board: the same lines between Queued goals and Dependencies, wrapped by the board's own fit at 60 columns. Done line 4 requires both surfaces: if the board reader cannot fit, the goal halts and reports line 4 as unmet to operation; "check-in only" is delivered only on operation's word. Before the build is accepted a throwaway prototype of the parser and tasks() is measured; if bytes run short use the compact form, which keeps every goal's name: `<name>: <state>, <k> of <n> goals finished (<slug> <step>, <slug> <step>), <ETA>` on one line; drop order after that: the goal-in-two-tasks flag, then the cycle label; anything that would remove a done-line element (name, state, goals, ETA, progress) is not a drop, it is an unmet goal reported to operation.

### 4. Size and package (done line 5)
Budget: parser and state in board_lines.py about 1,500 of 1,525 (very tight: the first prototype measures it, and the drop order applies); the renderer and its board call in live_board.py about 1,000 of 1,538; the check-in call site at most 300 of 499 in checkin.py. If the check-in or board reader cannot fit after the drop order and the allowed trims, the goal halts and reports to operation (done line 4 unmet), never delivers a reduced version without operation's word. Measured after each edit; trimmed, not moved to a new file. No `.loop/tasks` content names the service repo; the package scan (obfuscation patterns) and private-name scan stay green; docs: docs.tsv maps the monitoring scripts to the Monitoring, Operation and Check-in-and-board pages, so after the build `docs.py audit` names every page that needs its line or stamp and each is fixed by the repo's own route (never `restamp-own` with --help); the generated Tests tables are re-rendered after the rows are added; README only if the render changes it; no Delivery how-to line; the CHK-1 line is untouched. Room measured 1493 + 1525 + 1484 + 1538 = 6040 bytes; budget about 3 KB. Only rows are added to `.loop/regression.tsv`; every assert of the new toy is read by a row (size-check --unread).

### 5. Tests
New toy `dev/toy/test-tasks.py` (hermetic temp dirs; fake run records; never the real `.git/loop`; never the held toys) and added rows, each seen red before the code: two tasks with no Needs both running; Needs shows waiting then not waiting once the named task is done; a goal with no record and a goal with status queued are both not started; a waiting or failed run counts in flight (running); no record is queued; an unknown Needs is flagged; Replaced by shows replaced; each of the eleven briefs has every part, a Source, and no service repo name; reversed order and a three-task Needs chain resolve in one run; a Needs naming a replaced task follows the replacement; a goal named by two tasks is flagged; a name with a pipe, a control character or 500 characters prints as one clean bounded line; an unreadable brief gives one note and the rest still print; graph imported alone works; `no existing row changes` and `no new file under skills/` are checked in the lane by a diff against origin/main showing only added rows and no new skills path; the real `checkin.py` and `live_board.py` output over a fixture with briefs contains each task name and goal, and the same check-in text passes `reply_hook.py check`; output with no briefs is byte-identical to before.

### 6. Order and gates
Merge up to main (with v110-text) before the first lane; rerun what a conflict touches. After the build, a post-build review by an independent reviewer, reply recorded verbatim; the held toys are dev/toy/test-machine-log.py and dev/toy/test-platform-limits.py and are never run. Lanes: one fresh detached clone each, up to three while free memory is at least 40% and swap at most 2.5 GB, operation.id hashed before and after, copy only on a pass at exactly HEAD. Then `goal.py pr`; the merge is operation's.

### 7b. Lane and test-harness requirements (from the eng review)
The regression dependency mapper lists the two held toys' rows (platform-sends-counted, machine-status-live-workers) as depending on all four scripts, and `goal.py pr` runs the land lane (`regression.py run land --reuse --tier goal`); a detached clone does not exclude them. Operation must supply an exclusion that survives the PR lane before the first lane or the PR step, otherwise those rows would run the held toys; the worker does not run them and stops at that point to ask. New rows are proven red on a committed HEAD of the toy with a deliberate negative control per row (the tooling treats any non-zero exit except 77 as red, so a startup crash must be told apart by its message); every planned assertion prints a `PASS: <words>` line and each row greps its own PASS lines (size-check --unread reads only that shape); the end-to-end fixture follows the existing check-in toys' isolation (environment set before imports, fixed machine, health and PR states, no network) and the no-briefs baseline is captured from origin/main output on the same fixture, not from two runs of the new code; the forbidden-word rule applies to generated labels only, and a task named with a forbidden substring is a test case that must pass.

### 8. Obligations carried into the build (from the CEO and DX reviews)
O1-O8 (never raise; clean text; goal in two tasks; replacement then cycle; precedence and root; both surfaces; verbatim quotes; docs) and DX1-DX6, DX8-DX10 as recorded in the Review record; DX7 (reply hook requiring the task names) is deferred.


## Accepted amendments

Each is part of the plan above and is built and tested as written.

### Scope and strategy

- O1 never raise into the check-in or board; incomplete or unreadable brief named, not hidden; toy rows.
- O2 brief text cleaned (control characters, pipe, length) and no private name; toy row with the repo's private-name scan.
- O3 a goal named by two tasks is counted in both and flagged; toy row.
- O4 Needs resolved through Replaced by, then cycle check on effective edges; toy rows for a cycle, a replacement cycle, reversed order and a three-task chain.
- O5 state precedence replaced > done > running > waiting > queued; status queued is not started; ETA metric as stated; root passed explicitly; toy rows including cwd outside the fixture.
- O6 both surfaces are required; if the board reader cannot fit the goal halts and reports line 4 unmet to operation; compact form keeps goal names.
- O7 every quoted line verified verbatim against its source page at build time; the v1.2.0 briefs are not called frozen.
- O8 docs: every page docs audit names is updated; Tests tables re-rendered.

### Developer experience

- DX1 every problem line names the fix; an unexpected parser error prints "tasks unavailable: <error class>" and never stops the rest; toy rows.
- DX2 the how-to page documents where briefs live and how they reach the checkout (merged files), the layout, the two lines that may change after the freeze (Goals, Replaced by), the states, the ETA words, the repo scope.
- DX3 the page carries one complete example brief; no template file.
- DX4 keys case-insensitive, spaces trimmed, unknown lines ignored.
- DX5 no .loop/tasks: byte-identical output.
- DX6 a toy row shows a brief appears in the same render; no telemetry.
- DX8 an unknown or retired goal reference is flagged by name with the line to check; toy rows.
- DX9 the Tasks section covers this repo only; stated on the page.
- DX10 goal labels: finished, awaiting merge, not started, else the flow step; toy rows.

### Engineering

- E1 three functions only (task_rows, tasks, task_lines); callers only call and print.
- E2 both surfaces get the same finished set; one fixture renders both and the task lines are compared.
- E3 every planned assertion prints a PASS line read by a regression row; rows land level, only added; proven red on a committed HEAD with a negative control each.
- E4 the real check-in and board outputs are tested end to end under an isolated fixture; reply_hook check on the check-in text; forbidden words on generated board labels only.
- E5 a hostile brief and a deleted run record are tested; a task named with a forbidden substring passes.
- E6 bytes measured after each edit against the enforced caps (graph.py 19,000; checkin.py 19,495) and 20,480; a prototype measurement comes before the build is accepted; if it does not fit the goal halts and reports.
- E7 the held toys are never run; operation supplies the lane exclusion before the first lane (7b).

Deferred (a taste call, listed in the PR notes): the reply hook requiring task names (DX7). Open for operation: the exclusion of the two held toys' rows from the PR lane (section 7b).
