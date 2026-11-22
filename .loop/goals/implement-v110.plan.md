# Plan: implement-v110

## Implementation plan

Goal implement-v110 (v1.1.0 task 4): enforce DOC-27, DEL-19's goal format, DEL-23 and the revised DOC-28, with every
test case passing. Design: `.loop/goals/implement-v110.design.md`; measured bytes: `.loop/goals/implement-v110.bytes.md`
(committed with this plan); done lines frozen in `.loop/goals/implement-v110.md`. Depth: full. This is the plan as amended by
the review round recorded at its end.

### Preconditions, checked by the build's first command (and by the operation session before dispatch)
1. `dev/package.py` on the merge base has `MAX_FILES = 200` (the file-limit lift, o718), because `brief.py` is file 101.
2. The pages on the base carry DEL-23 and the revised DEL-19 and DOC-28 text with the owner's review marks (the text
   goal). This goal never writes Reviewed text or a mark.
If either is false the build stops and reports; it does not start work that a later merge would break.

### Rules for the whole build
- Exactly one new file, `skills/workflow-release/scripts/brief.py` (o718, o719). Everything else goes in existing
  scripts. No script reaches 20,480 bytes; none newly crosses 19,000 (`dev/toy/test-pods.sh`).
- Bytes come only from docstring and comment text (the byte table lists each host's docstring and comment bytes:
  goal.py 725+56, release.py 429+92, checkin.py 424+224, review.py 1,471+172, merge.py 1,423+255, proctree.py
  3,501+584 per copy, live_board.py 2,472+619, graph.py 3,113+2,030, watch.py 646+171, batch.py 1,467+144, and so on).
  Never code, never a test. Each trimmed file keeps a one-line purpose docstring; longer explanation moves to the
  skill's `references/`. A hook is one call, `brief.gate(...)` or `brief.lines(...)`, loaded by path, at most 100 bytes.
- The byte table is re-measured at build start and again before the PR; the toy asserts upper bounds (each script
  under 20,480 and none newly over 19,000), not equality, so a later edit by another goal is a rebase task for the
  coordinator, not a trim hunt for this lane.
- Net regression rows rise by at most four, one per feature (o736); new cases fold into existing scripts.
- Pages in the old shape keep passing: every DOC-27 rule applies only to a feature in the new form.

### Steps (in this commit order, so the first half can merge on its own if the operation session splits the goal)

**Half 1: DOC-27 and DEL-19.**

1. **DOC-27 in `sections.py`** (room 7,425; done lines 2 and 6). Add `features(root, text)` and one call from
   `sections.run`, reached by `docs.py check` through `render.front`; `docs.py` itself gains only the `--strict` flag
   (below). It runs only on a feature in the new form (a requirement line whose sub-bullets include `### Problem`).
   Rules, each a named finding with page and rule: section order Problem, Requirements (Functional then
   Non-functional), Non-goals, Success metrics, Reference, Revisions, Tests last, and no other section; at most five
   requirements; each requirement has one `Success metric N.N.` and a `Test cases` list with at least one case (exact
   matches); the Success metrics table lines index the inline metrics exactly; Reference lines tagged adopted,
   adapted, own or reference; the Milestone line links this repo's milestone (`pageformat.owner_repo`).
2. **The old-form section check must not fire on a new-form page.** `render.py:96` (the fixed old-form section list and
   Tests-last check) is gated on the absence of `### Problem`; an end-to-end `docs.py check` case on a new-form page
   proves the whole check passes, not just `sections.features`.
3. **Reported, not failed (done line 6).** A missing metric, test or reference, a feature marked "to split" and the
   page-rebuild items are `NOTE` findings that name what to add. `docs.py check --strict` turns every NOTE into a
   failure (about 60 bytes in `docs.py`), and the check prints how many features are in the new and the old form.
   Promotion: a new-form feature that carries a Reviewed mark is held to the failing form; the rest stay NOTE.
4. **Reviewed from the owner's typed record only (DOC-27.5), checked twice.** `deployments.owner_words` is not changed.
   - (a) At mark time, `criteria.py` (25 spare bytes; bytes from its 1,605 docstring bytes) reads the local ledger
     (`<git common dir>/loop/owner-words.tsv`) and refuses a new-form Reviewed mark unless one record exists whose ID
     list is exactly that one ID and whose source is the owner (a delegated or relayed record is refused for a new-form
     mark); on success it appends one line to the **committed** file `.loop/reviews.tsv`: `ID<TAB>record id<TAB>date`.
     Only the ID, the record id and the date are written, never the owner's words.
   - (b) In CI, `docs.py check` (through `sections.features`) requires every new-form Reviewed mark to have a line in
     `.loop/reviews.tsv` naming exactly that ID and one record id, so the mark is enforced where merges happen with
     nothing private in the repo. A mark with no line fails, naming the ID and the fix (run the mark command on the
     machine that holds the ledger). Marks already on main before this goal have no line: the build seeds a line for a
     mark only where the local ledger holds a record naming exactly that ID with the owner as source, and lists every
     mark it could not seed to the operation session; until a mark has a line it is a `NOTE` naming the missing line,
     and any mark dated after the day this rule lands must have one. The rule never writes a mark and never reads or
     prints the owner's words.
   - The committed file is the repo's own data, listed in the doc-spec registry and in `.loop/docs.tsv`'s mapping so the
     template's own check reads it; adopted repos get it from setup like any other `.loop` file.
5. **DEL-19 goal format** (done line 3).
   - `proctree.TEMPLATE` gains `Task:` and `Release:` lines. The template is formatted by `goal.cmd_new`, `watch.py`
     (its own copy) and `batch.cmd_queue` with a fixed key set: all callers and all three `proctree.py` copies change
     together, and a toy asserts the three copies are byte-identical.
   - `goal.py new` takes `--task` (bytes from `goal.py`'s docstrings, 725). `--task` is required: every existing
     goal-creating test caller is found with grep and updated in the same commit (the byte-identical goal text is
     unchanged; no test is loosened), and the task joins the frozen record.
   - `fit.frozen_fields` refuses a freeze whose named task or requirement is not Reviewed (read from the committed
     `.loop/reviews.tsv` and the pages) and, in the same place, a freeze with no task, a done line that is not Given/when/then (its own small regex) or
     a missing part, printing what, fix and a code.
   - `role.requirement_gate` (called by `cmd_pr`) refuses the PR when the flow's review step is skipped.
   - `HEAD_MOVED` and the `done_sha` refusal already exist: they get rows only.
   - A steps block generated from `flow.STEPS` (loaded by path) sits in `sections.py` beside "What this is". The two
     generated blocks have different sources and each goes stale on its own: the steps block when `flow.STEPS`
     changes, "What this is" when the DEL-19 text changes; neither takes precedence and each gives the existing `STALE`
     finding when regenerated output differs.

**Half 2: DEL-23 and DOC-28 in `brief.py`** (done lines 4, 5 and 7).

6. **Commands (the first-run path).** `brief.py freeze task NAME`, `brief.py freeze release VERSION`, `brief.py tasks`,
   `brief.py check`, `brief.py gate <merge|bump|cut> ...`. A task brief lives at `.loop/tasks/<slug>.md`, a release brief
   at `docs/release-brief-<version>.md`; slugs are validated (letters, digits, hyphen) and a frozen brief is never
   overwritten. `references/commands.md` of `workflow-release` shows one copy-paste task brief and one release brief and
   a toy runs both examples. `docs/release-brief-*.md` and `.loop/tasks/` are registered in the doc-spec registry and
   `.loop/docs.tsv`, and the setup and update notes name them as the repo's own data, so adopted repos keep their own
   briefs and the template's check reads them. `SKILL.md` stays within its line cap (144 of 150) by moving detail into `references/`.
7. **Freeze and re-freeze.** `freeze` needs the owner's typed record naming exactly that ID. Without it the refusal is one question with the
   recommended record text ("Freeze <ID>? Recommended: type `<exact words>`"), the lane stops with status `waiting`
   and never retries or types the words itself; an unattended lane therefore waits for the owner's one decision per
   brief, as DEL-3 allows and stores the content hash; a
   changed word makes `check` fail with the fix line "a change is a new task that replaces this one: `brief.py freeze task
   NEW --replaces NAME`" (a new typed record and a new freeze; the old brief becomes `replaced`).
8. **Tasks** (DEL-23). `tasks()` is the one list (name, state queued/running/waiting/done/replaced, goals, ETA) from
   the briefs and the goals' run records; a new brief shows on the next read, and the board's existing refresh sets how
   fast. `can_start`: refuses with no frozen brief or a named dependency not done; independent tasks run side by side.
   `can_finish`: every goal merged and every done-when line met.
9. **Releases** (DOC-28). The release brief lists tasks in order and is frozen the same way. Gates: a major or minor
   with no frozen brief is refused; a cut with a named task not done is refused; a feature task merges only once a
   frozen brief names it, a bug-fix task any time; a major with a non-empty `.loop/regression-known.tsv` is refused
   with no waiver (o714), listing the rows and saying clearing a row is the only path; the tag notes list every task, and the tag notes and the brief's result text pass `private.scan` (and the home and
   email check) before the tag is made, a hit refusing the cut with the line named;
   after the cut the brief records each task's merged goals. The cut's side effects run in a fixed order (write the
   brief's result record as pending, tag, notes, mark the record complete); a refusal states what was done so far and
   the reconcile command, and the brief write is idempotent so a retry is safe.
10. **Refusals share one helper** in `brief.py`: it prints what (operation and values, never ledger text), fix (the exact
    command or what the human must provide) and a stable code (BRF-001 and up, listed in `references/commands.md`) on
    stderr, exits non-zero, and every refusal test reads those strings.
11. **Cost bounds, measured.** Each gate reads at most two small files and one record file: a toy asserts the merge,
    bump and cut gates finish under one second each on the toy repo, the task list under one second, and the board's
    task block adds nothing over 10 seconds to the board; the "within a minute" claim is tested with a timestamped add
    (the brief written, the list read, the elapsed time under the board's refresh) and states the refresh it relies on.
11b. **Hooks** (one call each, loaded by path; the gates fail closed, the board renderers show a NOTE when `brief.py`
    cannot load): `merge.py` (feature-task merge gate), `review.py` `gate_refusals` (known-red rule), `release.py`
    `bump` and `cmd_cut`, `checkin.py` and `live_board.py` (tasks by name with their goals under them). Behaviour
    changes carried into the PR body (file, old, new): `fit.frozen_fields` and `goal.py new` (task required), `role.
    requirement_gate` (skipped review refuses the PR), the merge, bump, cut and known-red refusals, the DOC-27 findings.

**Both halves.**

12. **Package and gate** (done line 7). `dev/toy/test-release-gate.py` check 7 ("no file is added") becomes "the shipped
    package stays within MAX_FILES", with a control where one file over fails (o719); this follows the owner's o719
    and is not a loosening: the new assertion cites o719 in its text. `brief.py` is added to that file's size guard
    list (line 333). New DOC-28 cases do not go in the known-red `rel-major-refused` row.
13. **Tests** (done lines 1 and 8). Four rows, one per feature (DOC-27, DEL-19, DEL-23, DOC-28), each running one script
    that holds all of that feature's cases (folded into `test-docs-sections.sh`, `test-goal.sh`,
    `test-release-gate.py` and a new section of an existing script for DEL-23); every case has a fixture that breaks
    only its rule and is proven red with `regression.py red ID --break`; each script prints the failing case ID on red;
    assertion strings are read by the rows (the REG-4 unread rule). Tests tables come from `criteria.py render`
    (`criteria.py` has 25 spare bytes: the render change is confirmed to fit before the four-row shape is committed;
    if it does not, the row text is shortened, never the render skipped). No existing test turns red.
14. **Guards.** Cite GRD-20's own wording: its limit is the fail line and its rule is that a script is never reformatted
    only to fit; trims here shorten docstring and comment text and keep a one-line purpose in each file, with the
    detail moved to the skill's `references/` (where the command reference checks read it), and the byte table lists
    each trim; no code is reformatted. A toy asserts each host's byte bounds; the `test-pods.sh` size section, the package check, the full
    affected-row lane and a scan of committed text for private names pass. The expected headroom of `brief.py` goes
    into the byte table so the next goal knows whether it can grow (scheduling is a non-goal and will need a file).

### Non-goals
Scheduling of tasks; the page rebuild; writing any Reviewed text or mark; changing a guard or hook of the loop.

## Review record

Run: three native phases (CEO, DX, Eng) through the planning tool's driver, no outside voice (`--no-outside`;
coverage native_only); the Eng reviewer was sent back once to check every claim against the repo files. Findings: CEO 11,
DX 10, Eng 12. All plan-changing findings are applied in the steps above: preconditions (cap lift and the DEL-23 text on
the base), the byte table committed with the plan and re-measured with upper bounds, trims from docstrings and
comments only, `--task` required with every caller updated, the `render.py:96` gate for new-form pages, `owner_words`
untouched with the exact-ID rule in a new helper, the TEMPLATE callers changed together, the exact NOTE text for an
unverifiable mark, `--strict` and the promotion rule, the shared refusal helper with codes and no ledger text, named
commands and a re-freeze path, an idempotent cut order, fail-closed hooks, new cases outside the known-red row,
failing case IDs, and the behaviour-change list for the PR body. The driver's own approval item stays pending: the
plan gate is `notify.py plan-review`.

Considered and rejected: splitting this goal into two (DOC-27 with DEL-19; DEL-23 with DOC-28). The goal is frozen with
the owner's approved done lines; the commit order above still keeps the first half separable.
Round 1 gate: eight breaks; this revision applies the six plan fixes (Reviewed named task, measured bounds, GRD-20
wording, the tag-note scan, the registry and setup note, the one-question refusal) and the two-step Reviewed check for
the first break.

<!-- autoplan-accepted:ceo -->
- Preconditions; byte table with re-measure; docstring-only trims; one-call hooks; behaviour-change list.
<!-- /autoplan-accepted:ceo -->
<!-- autoplan-accepted:dx -->
- Shared refusal helper with codes; named commands and examples; re-freeze path; NOTE text; strict flag; cut order.
<!-- /autoplan-accepted:dx -->
<!-- autoplan-accepted:eng -->
- render.py gate; owner_words untouched; TEMPLATE callers together; known-red row avoided; fail-closed hooks.
<!-- /autoplan-accepted:eng -->
