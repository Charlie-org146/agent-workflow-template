# Plan: v110-cbs-asz

Design: `.loop/designs/v110-cbs-asz.md` (idea step, recorded). Requirement text: CBS-1 and ASZ-1 in the file reviewed-features-2026-11-23-reworded-DRAFT.md.

## URGENT, outside this plan

None.

## Implementation plan

Done lines (frozen, from the goal file): (1) every CBS-1 and ASZ-1 test case runs as a real regression test linked to its requirement and passes, and each fails on a fixture that breaks only its rule; (2) at freeze a plan is sized small, medium or large by the owner's lines, the reason is recorded, the checks come from the CBS-1 table, and a goal touching a safety class is always large; (3) at build record a goal is re-sized up and the added checks run before its PR, and a size never goes down; (4) every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

Touches (frozen): skills/workflow-delivery, skills/workflow-monitoring, .loop/config.json, dev/toy, .loop/regression.tsv. Nothing outside these is edited; where a requirement reaches outside them (the release list, the settings reader's refusal) the plan says which touched file carries it.

### Size of this goal (computed by its own rule, recorded here as the first use)
Files: skills/workflow-delivery/scripts/sizing.py (new), skills/workflow-delivery/scripts/guards.py, skills/workflow-delivery/scripts/role.py, skills/workflow-monitoring/scripts/sizeline.py (new), skills/workflow-monitoring/scripts/board_tasks.py, skills/workflow-release/scripts/cutcheck.py (new), skills/workflow-release/SKILL.md, .loop/config.json, dev/toy/test-sizing.sh (new), .loop/regression.tsv
Lines: about 600
Gates: the planning gate, the build gate, the ship gate
Large: it touches three skills and 10 files with gates. New files, exactly four: sizing.py, sizeline.py, cutcheck.py and dev/toy/test-sizing.sh; the owner allows the new files past the file limit (record o918). Its checks are the full set; it is the first goal to run the new rule and gets no lighter form.

### 1. New module `skills/workflow-delivery/scripts/sizing.py` (new file, under 15,000 bytes; every existing delivery script is within a few hundred bytes of the cap, so each hook is one call)
- `size_of(plan_text, changed, config, safety)` is a pure function. Inputs: the plan's `Files:` list (each entry one file path; a directory, a glob or a missing list counts as large with that reason), its `Lines:` estimate (a missing estimate counts as large), its `Gates:` line (a gate is a named merge or build gate; none listed means none), and `safety`, the safety classes judged on the plan text and on every changed path against the repo's risky-path list, using the monitoring skill's class table read from there, never copied. It returns `(size, reason)`. Small: 3 files or fewer, 150 lines or fewer, no gate and no safety class. Medium: 10 files or fewer and no safety class. Large: everything else, and always large when `safety` is non-empty. The reason names each number and the line it crossed.
- `read_table(base)` reads `.loop/config.json` from `origin/<base>`, then the base branch, the way the review-depth setting is read, so a worker's own branch cannot lighten the table it is judged by. A missing table takes the shipped defaults; a row that drops or lightens a fixed check (build gate, full test run before merge, two leak readers before any push, every safety class) is refused with a message naming the row and the check. It is called by `size`, by `resize` and by the record check, and each refuses on a bad row.
- `size(slug)`: reads the plan file, writes the stored `sized` (`size`, `reason`, `checks` with each check's named form and pass count, the plan sha, `added`, `owner`). It runs in the plan step after the plan file is written and before any review phase of that step, so the plan's own reviews run at the size's forms. The plan record re-checks the plan's sha; a changed sha re-runs it. On every re-run the stored checks are a ratchet: the union of the old and new checks, each at the stronger form, so a large plan edited down to small keeps the large checks (negative controls: a plan edit, a table change). Every write of `sized` stores `grow(old, new)` for the size and the checks ratchet together. A test edits a large plan down and re-records, and the stored size must stay large.
- `resize(state)`: diffs against the base for files and lines and stores `grow(old, new)`; when the size rose, the checks the new size adds go to `added`. A failed diff read keeps the stored size and logs the failure (a size never goes down).
- `grow(old, new)` returns the larger of two sizes (small < medium < large).
- `check(state, step, text)` owns two refusals, both no-try: a ship record while any check in `sized.added` has no evidence line, and a reply whose `CHECK:` lines are missing, unknown, of another form or of a different pass count than the stored form. The record check calls it before its budget-stop early return, so a step stopped at its budget still has to carry the lines (negative control: a budget-stopped reply without them is refused). A form's pass count is validated against the shipped defaults, so a form cannot be redefined under the same name. Each form in `forms` lists its required phases or marker strings; `check` also refuses a `CHECK:` line on a reply whose step is `skipped` or `pending`, or that lacks those phases. The existing full-review marker check stays and runs as well.
- `override(state, size, record)` needs a record id from the owner-words record (the one `plan-accept` already takes), stores the id with the old and new size and applies `grow`. A request for a smaller size, or for any size under a safety-class goal, is refused. After an override the same ship gate runs the added checks.
- `skipped(states)` prints one list across goals of every check skipped or run light, with its named form, for the pull request body.
- `rule(step, state)` returns the one prompt line that tells a step which forms to run. For the plan step with no `sized` field it returns: when the plan file is written and before any review phase, run `python3 skills/workflow-delivery/scripts/sizing.py size SLUG`, then run each check in the form it prints. It appends nothing for goals frozen before this rule. The plan record refuses (no try used) a goal that has no `sized` field.

### 2. Table and defaults: `.loop/config.json` key `checks_by_size`
- Rows `small`, `medium`, `large`, each listing its checks with a named form; `forms` defines each form once, with its pass count and a one-line `covers` text (CBS-1.3): for example plan review `one-round`, `full`; red team `one-pass-no-rerun`, `full`; review `normal`, `full`.
- Defaults: small runs the fixed list plus one-round plan review, one-pass red team and normal review; medium runs the fixed list plus full plan review, one-pass red team and normal review; large runs every check in its full form. The defaults are written once, in the config, and `sizing.py` reads them from there; a toy case compares the shipped config to the sizer's reading so the two cannot drift.
- Strength order of the forms is their pass count (a form with more passes is stronger), and each form's required phases or marker strings are written once, in `forms`.
- Only the owner's words change the table: a table change on a worker branch is not read (it is read from the base).

### 3. Hooks (no trims anywhere: a hook goes in a new or roomy file, and a file with no room is not touched)
Rule from the operation (TD1424): no docstring or comment is trimmed to make room. goal.py, flow.py, lane.py, fit.py, operate.py, board_lines.py and release.py are not edited at all.
- A freeze-time size already exists (DEL-5: a small/large flag stored with the goal, used only to pick the review depth). It is left exactly as it is; the new size is the separate stored field `sized`, so the review-depth rule and every test of it keep their meaning.
- Prompt rule: `skills/workflow-delivery/scripts/role.py` (the module that already holds the step's depth text) gains one call, `sizing.rule(step, state)`, so the stored forms reach the prompt of the plan step and of each later step. The plan step's rule line makes the agent run `sizing.py size SLUG` once the plan file exists and before any review phase; `size` is never called at step start.
- Record check: `skills/workflow-delivery/scripts/guards.py`, in its existing record-time check, gains one call to `sizing.check` placed before the budget-stop early return. It owns: the plan record refusing a goal with no `sized` field, the ship record refusing while any check in `sized.added` has no evidence line, and the `CHECK:` line validation. It also returns the stamp text the record already appends to the step line, which carries the list of skipped or light checks; the pull request body already renders each step's line, so CBS-1.4's list reaches the PR body with no edit to the PR body code.
- Re-size: `sizing.resize(state)` runs at the first step start after the build (review), at qa and at ship through the step-start stamp in `guards.py`, and once more at the PR step: the function `guards.waiting_gate`, which `cmd_pr` already calls with the goal's state, gains one call, `sizing.at_pr(g, state)`, which resizes the final diff (uncommitted changes included) after the base merge, then calls `sizing.check(state, 'ship', '')`, so checks added at PR time are refused until their evidence is recorded. It refuses unless a resize of the final diff succeeded. (`goal.py step build` is not a hook: the build has no diff yet, and goal.py is not edited.)
- The stored forms take precedence over the review-depth wording for a goal that has `sized`; goals without it keep today's wording.
- Board: `skills/workflow-monitoring/scripts/board_tasks.py` (a small file with room) gains one call into `sizeline.py` that returns the goal's size line: size, reason, checks, and the owner's record id when an owner line changed it.
- Owner size line: the new script `skills/workflow-monitoring/scripts/sizeline.py` is its own command (`sizeline.py set SLUG SIZE --owner-record ID`, and `sizeline.py show SLUG`); it calls `sizing.override`, refuses without a record id, and operate.py is not edited.
- CBS-1.4 cut check: the new script `skills/workflow-release/scripts/cutcheck.py` prints one list across goals of every check skipped or run light, and with `--require-full CHECK` runs that check in its full form first and exits non-zero if it fails. The release skill's `SKILL.md` gains one line saying to run `cutcheck.py` before the cut. `release.py` is not edited, so the cut test is a procedure (run cutcheck, then cut), not a refusal inside the cut; the plan states this plainly. The operation session adds `skills/workflow-release/scripts/cutcheck.py` and `skills/workflow-release/SKILL.md` to this goal's touches before the build (owner record o918 allows the new files).
- CBS-1.2 through the settings reader is out of reach (the reader is outside the touches): the refusal is met through `read_table` and its three callers, which is what the test calls.
- Byte budget: no existing file is trimmed. guards.py (475 bytes of room) takes two call lines and role.py (145 bytes) one; each addition is measured and the file stays under 20,480 bytes. board_tasks.py has ample room. sizing.py, sizeline.py and cutcheck.py are each under 15,000 bytes. `size-check.py` and the existing size rows are the proof.
- Build gate for this goal: it does not open until the operation session has added the two release paths to the touches.

### 4. Tests and rows (dev/toy, .loop/regression.tsv)
(Additional cases beyond the seven requirement tests: a table row on a worker branch is not read; a directory, a glob and a missing estimate each size large with a reason; a size never drops on resume or re-record; an owner line asking for a smaller size is refused; a reply with a missing, unknown or different form line is refused; the shipped defaults equal the config.)
One toy script `dev/toy/test-sizing.sh` (under 20,480 bytes) with one case per requirement test, each run on fixtures in a temp HOME with a toy repo and no network:
- CBS-1.1: a small goal's record shows exactly the table's small checks, each in its named form.
- CBS-1.2: a table row that skips the full test run for small is refused when the table is read.
- CBS-1.3: a medium goal's red team runs light; the record names the form and shows one pass.
- CBS-1.4: three goals skip a check; `cutcheck.py` lists all three, and `cutcheck.py --require-full CHECK` runs that check in its full form first and exits non-zero when it fails.
- ASZ-1.1: a goal touching 2 files and no gate is sized small with its reason, and its checks start with no question.
- ASZ-1.2: a small goal whose diff passes the medium line is re-sized and the medium checks run before the PR; a safety-class goal is large; a size never goes down.
- ASZ-1.3: the owner's line sizes a goal up; the board shows the new size with the words; a line without words is refused.
- Negative controls: each case also has a fixture that breaks only its rule and must fail the case.
Rows in `.loop/regression.tsv`: one row per case, linked to the requirement, each added with `regression.py add` and seen red with `regression.py red --break`.

### 5. Docs
The wiki pages `Checks-by-size` and `Autonomous-sizing` are written by the owner-approved text step (v110-tsk12-14-text); this goal links to them and does not write them.

### Verification
Every toy case green, every row seen red then green, `size-check.py` passes (every script under 20,480 bytes, sizing.py under 15,000), no existing test changed, `docs.py check` clean, and the committed text is scanned for the service repo name.

### NOT in scope
Making any check faster or cheaper (SKP-1, CHP-1); the Checks-by-size and Autonomous-sizing pages (v110-tsk12-14-text); setting the table's values beyond the shipped defaults (only the owner's words do); the planning tool's guard.

### What already exists
The monitoring skill's safety-class table, the settings reader and `_help` pattern for config keys, the owner-record pattern of `plan-accept`, the board's line renderers, `regression.py add` and `red --break`, `dev/toy/size-check.py`.

## Review record

(filled by the plan review)
