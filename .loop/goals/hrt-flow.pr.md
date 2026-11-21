# hrt-flow investigation record

Issues: #5652 #5654 #5678 #5667 #5677 #5681.

Incomplete: environment blocked. All six toys were run sequentially, once each, on this branch in the sandbox. No toy, fixture, product script, regression row, known list or setting was changed. No assertion was weakened, replaced, skipped or deleted; no changed assertion or new negative control exists to assess. No product bug was established. No branch publication or PR was attempted.

The first toy additionally reported this exact sandbox refusal:

```text
PermissionError: [Errno 1] Operation not permitted: 'ps'
```

Every toy reported this exact cleanup refusal:

```text
SKIP: REAP: cannot list processes (ps failed ([Errno 1] Operation not permitted: 'ps')); leftover processes were not checked here
```

These are environment effects. Each affected toy action was left without edits or a retry; no alternate process-list method or sandbox workaround was used. Several scripts continued internally after their suppressed subprocess failures before the outer command returned. Exit 1 was retained because assertions had already failed; the cleanup helper reports its process-list failure as 77 internally. The original outside-sandbox measurements supplied by the owner differ from these sandbox observations.

| Toy | Before in sandbox (exit, assertion FAIL count) | After | Disposition |
|---|---|---|---|
| `dev/toy/test-budget.sh` | 1, 8 | Not rerun | Unchanged; environment blocked |
| `dev/toy/test-delivery-prd.sh` | 1, 28 | Not rerun | Unchanged; environment blocked |
| `dev/toy/test-tokens.sh` | 1, 4 | Not rerun | Unchanged; environment blocked |
| `dev/toy/test-milestones.sh` | 1, 2 | Not rerun | Unchanged; environment blocked |
| `dev/toy/test-status-graph.sh` | 1, 1 | Not rerun | Unchanged; environment blocked |
| `dev/toy/test-wiki.sh` | 1, 8 | Not rerun | Unchanged; environment blocked |

## Evidence and every observed assertion failure

### test-budget.sh

The toy expects its slow review command to run headlessly. The observed output instead repeatedly says `IN SESSION review`; recording then reports `NOT_RUN_BY_FLOW`. `flow.py:in_session` requires a fresh reply before writing the `.ran` marker; `goal.py:cmd_record` requires that marker. Commits `a93736c64` (session steps), `5702ab78d` (flow-run guards), and `8238a12c4` (new goals bind an app session) establish intended behavior. Independently, the regression timeout path in `lanes.py:descendants` calls `ps` and was denied. No stale assertion was adapted after this environment blocker.

Observed assertion FAIL lines (verbatim):

```text
FAIL: rows run in order until the budget, then the rest are left and listed
FAIL: a left row is not a failure
FAIL: the next lane on the same content reuses the left rows and runs none
FAIL: the lane passes, says what it left, and the goal's run file names the step, the limit and the rows
FAIL: a review stopped at its limit records done with what it left, never a failed try
FAIL: the goal's run file names the step and what it left
FAIL: the step instructions carry the step budget in minutes
FAIL: the report lists each budget hit with what it left
```

### test-delivery-prd.sh

The `step()` fixture assumes that two flow calls execute a headless fake skill and produce a reply. Session execution instead asks for a reply, leaving downstream depth, resume, budget and PR checks without the expected completed flow. `goal.py:cmd_record`, `flow.py:in_session`, and `fit.py:bind_here` implement this behavior (commits `5702ab78d`, `a93736c64`, `8238a12c4`). The setting failure needs separate investigation: no `bud1.extra.json` was produced. Cleanup could not inspect processes. This run does not establish that every failure has the same cause, or prove a product bug.

Observed assertion FAIL lines (verbatim):

```text
FAIL: a small goal's condensed review is recorded under condensed
FAIL: a large goal's condensed review is refused with no try under condensed
FAIL: set refuses a depth after the plan is recorded, pointing to --again
FAIL: the owner's per-goal override beats the size
FAIL: under review_depth full a small goal is full, and the owner's override still wins
FAIL: under review_depth full a small goal with no override is held to full
FAIL: a condensed goal still runs the full land lane in qa
FAIL: a review killed mid-step counts exactly one failed try
FAIL: the killed goal keeps its recorded idea and plan
FAIL: goal.py show names review as where it resumes
FAIL: rerunning a recorded step is refused with no try and names the resume step
FAIL: the resumed review runs and records, and the goal moves on to qa
FAIL: with idea and plan recorded and no commit since, the goal resumes at build
FAIL: --again reruns a step on purpose: it clears that step and every later one, keeping tries and tokens
FAIL: a session worker killed mid-step keeps its record, is asked again, and a reply with no STEP line uses no try
FAIL: the owner raises one goal's budget with set
FAIL: goal.py pr refuses to push a private name, with no try, naming the place, never the text
FAIL: a name added then removed in a later commit still refuses
FAIL: a private name only in a commit message refuses
FAIL: a private file name is masked, and a '++ ' line and text past column 4096 are scanned
FAIL: a goal that only removes a leaked name is not refused
FAIL: a private name only in the pull request body refuses
FAIL: a broken list refuses every push, naming the file and line, never the pattern
FAIL: with no list the pull request says nothing was checked, naming the list unexpanded
FAIL: a step's VERDICT lines are kept on the run record and listed in the pull request (#38)
FAIL: the pull request names the decided review depth and the budget (#38)
FAIL: a deleted file a repo script writes back is warned about in the pull request (#117)
FAIL: goal.py pr refuses a goal that changed a Reviewed requirement no done line states, pushing nothing
```

### test-tokens.sh

The captured output is `IN SESSION idea`, so the fake JSON-emitting agent never supplies the tested output, tokens or raw reply. `flow.py:in_session` deliberately prints instructions until it receives a fresh reply. This follows the session path introduced in `a93736c64` and automatic binding in `8238a12c4`. The live-board assertion also failed; its cause is not established by this run. Cleanup was blocked; no execution-mode or assertion changes were made.

Observed assertion FAIL lines (verbatim):

```text
FAIL: the step prints the agent's own STEP and PENDING lines
FAIL: tokens are input + output + cache-creation, never cache reads
FAIL: the reply file holds the result text, the raw JSON is kept beside it
FAIL: the live board leaves tokens off
```

### test-milestones.sh

The first assertion conflates milestone prompts with any occurrence of `milestone` in generated files. Captured setup output has no milestone prompt; `settings.py` now includes the optional `milestones_source` setting, introduced by `55e0d2d25`. Setup's prerequisite checklist was introduced by `88a3a9263`. The PR fixture also fails to finish its flow: `flow-done.sh` polls flow but does not supply session replies, and `goal.py:cmd_pr` requires every flow step. Session/guard history is `a93736c64`, `5702ab78d`, `8238a12c4`. Cleanup was blocked; assertions and fixtures remain unchanged.

Observed assertion FAIL lines (verbatim):

```text
FAIL: setup mentions a milestone: PREREQUISITES:
FAIL: pr: REFUSED: the flow hasn't finished: idea, plan, review, qa, ship. Fix: run flow.py calc-goal idea.
```

### test-status-graph.sh

The failing label assertion follows two flow calls with no session reply, then an unsuccessful record whose output the toy redirects. `goal.py:cmd_record` requires `.ran`, whereas `flow.py:in_session` writes it only after a fresh STEP reply. Successful recording still explicitly assigns `state["step"] = role.after(step)`; this evidence does not prove a label-advance product bug. Session/guard behavior is documented in commits `a93736c64`, `5702ab78d`, `8238a12c4`. Cleanup was blocked; no assertion was changed.

Observed assertion FAIL lines (verbatim):

```text
FAIL: recording moves the label on, so the finished step is never shown as current
```

### test-wiki.sh

The fixture failed to reach a PR for both w and x. The captured run includes a `ps` PermissionError, then downstream refusals because no finished PR exists. `goal.py:cmd_pr` requires completed flow; `flow-done.sh` does not supply session replies; `wiki.py:cmd_prepare` and the release commands exercise later stages that require a usable PR/branch fixture. Relevant history is `a93736c64`, `5702ab78d`, `8238a12c4`. The blocker prevents separating all fixture drift from any additional wiki defect. No product bug is asserted and no toy/fixture was changed.

Observed assertion FAIL lines (verbatim):

```text
FAIL: goal did not reach a pull request
FAIL: merge stale
FAIL: not committed or pushed
FAIL: merge publish
FAIL: page not on wiki
FAIL: goal x did not reach a pull request
FAIL: merge unmapped
FAIL: notes not published
```

## Required checks

- `python3 skills/workflow-docs/scripts/docs.py check`: exit 0, `DOCS OK: 16 pages`.
- `python3 skills/workflow-docs/scripts/criteria.py render --check`: exit 0, `TABLES OK`.
- `python3 dev/package.py --static`: exit 0, `PASS: 100 files, the static rules hold`.
- `python3 skills/workflow-delivery/scripts/private.py hook staged`: exit 0, no output, on the investigation record.

The goal remains incomplete: outside-sandbox green runs are unavailable and intended fixes have not been implemented. Scope, documentation checks, and the staged private-name check passed for this record. This record is evidence of a blocked investigation, not a completed repair.
