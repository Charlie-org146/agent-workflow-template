# Plan: v110-lvl-relevel (Test levels G1: level words, risk tags, one re-levelling, L0)

Frozen done lines: `.loop/goals/v110-lvl-relevel.md` (6 lines). This plan builds to them and changes none.
Design source: the owner-approved Test levels page (record o980, landing o985). G1 builds LVL-1.1's level words and
their refusal, LVL-1.3's tagging, LVL-1.5's re-levelling and the L0 limit. Running rows by level belongs to later goals.
Rulings built in: done line 3's rows are the table's rows when G1 builds, every one kept (o1005); a side record file,
no new table column (no done line names one); a new module is allowed under the 20,480-byte packaged-script limit;
the plan is rewritten with a new red team (o1032), planned now (o1036). This text replaces the earlier plan whole.

Files: skills/workflow-regression/scripts/levels.py, skills/workflow-regression/scripts/levels_read.py (only if needed), skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/completion.py, skills/workflow-regression/scripts/lanes.py, skills/workflow-delivery/scripts/sizing.py, skills/workflow-delivery/scripts/cover.py, skills/workflow-regression/SKILL.md, .loop/regression.tsv, .loop/regression-relevel.tsv, .loop/regression-risk.tsv, .loop/regression-relevel-input.tsv, dev/toy/lvl_fixture.py, dev/toy/test-lvl-table.py, dev/toy/test-lvl-relevel.py, dev/toy/test-lvl-sizing.py, skills/loop-files.md, listing.json, docs/wiki/Tests.md
Lines: 1100
Gates: reading the regression table (new refusals), the one re-levelling, reading the size table
Classes: none

**Added to the frozen touches by operation:** `.loop/regression-relevel.tsv`, `.loop/regression-risk.tsv` and
`.loop/regression-relevel-input.tsv` (the record and its two inputs), `skills/loop-files.md` (the file formats and
refusal codes), `listing.json` (the new commands must be listed), `docs/wiki/Tests.md` (re-rendered when rows are
added).

## 1. Data files
- `.loop/regression.tsv` keeps its eight columns. G1 adds rows only; it edits no existing row.
- **Record**, `.loop/regression-relevel.tsv`: one line per table row, in table order, tab-separated:
  `id, old, level, risk, covers, seconds, cmdhash, reason`.
  `old` is the table's level word at the re-levelling; `level` is `L0`, `L1` or `L2`; `risk` is `security`, `private`
  or `none`; `covers` is a comma list of row ids (covered rows only); `seconds` and `cmdhash` (sha1 of the row's
  command) are filled for L0 rows; `reason` is one or more of `default`, `time:<seconds>`, `risk:<tag>`,
  `covers`, `excepted:<owner record>`. A reason never holds a link or a repository name.
  Example: `eta-freeze  land  L1  none            default`.
- **Risk data**, `.loop/regression-risk.tsv`, read on every table read: `kind, key, tag, why`.
  `kind` is `requirement` (a Principle 6 requirement id, including the ids it absorbs), `row` (a hand-tagged row
  id) or `label` (an issue label that means security or private). Section 8 lists them. A repository with no
  Principle 6 requirement says so with one line, `requirement`, `-`, `none` and why.
- **Re-levelling input**, `.loop/regression-relevel-input.tsv`, read only by `relevel`: the `covers` list of each
  covered row (section 7), and for a defect row whose link is a bare number, `own <number>` (an issue of this
  repository). It never holds another repository's name or address.

## 2. When the new rules apply
A table is **levelled** when the record file exists, or the table holds the row `lvl-armed`. A levelled table without
the record file is refused. A table with neither (fixtures, a repository that never re-levelled) reads exactly as
before. The pull request text states this boundary.

## 3. What reading a levelled table refuses
All failing rows are listed at once (the first 20 and a count), on stderr, exit 2. Each line names the code, the
row, the file and line, the value, the fix and who makes it.
| Code | Refused |
|---|---|
| `LEVELS_NO_RECORD` | a levelled table with no record file |
| `LEVELS_NO_ENTRY` | a row with no record entry (names the row and L0, L1, L2) |
| `LEVELS_BAD_LEVEL` | a level that is blank or not L0, L1 or L2 (names the row and the three levels) |
| `LEVELS_NO_RISK` | a row that guards a Principle 6 requirement (its goal names a listed requirement, or the row is listed) whose risk is blank or `none` |
| `LEVELS_RISK_L0` | a security or private row at L0 |
| `LEVELS_ORPHAN` | an entry whose row is not in the table |
| `LEVELS_DUPLICATE` | an id twice in the table or in the record |
| `LEVELS_L0_OVER` | L0 seconds adding to more than 45 (names the total) |
| `LEVELS_L0_TIME` | an L0 entry with no positive seconds, or a `cmdhash` that no longer matches the command |
| `LEVELS_BAD_COVERS` | a covered row whose list is empty, names itself, an unknown id or another covered row, or loops |
| `LEVELS_BAD_RISK_DATA` | risk data missing, empty or unreadable while the table is levelled |
| `LEVELS_BAD_FILE` | a malformed line (column count, non-number seconds, conflict markers) |
An unexpected failure prints one redacted line and says nothing was written. One bad entry stops every command that
reads the table; the repair commands of section 5 still run.

**A covered row's level** is the highest level among its covers (at least L1 when the row is tagged; every cover of
a tagged covered row is tagged too). Reads use the computed value; every write by the tool records it again. A covered
row never runs: it carries no seconds or command hash, and the L0 total and time rules skip it.

**A covered row with no proving row** is excused only by a fixed entry in the new module, tied to the row's id, goal
and command (TD2022, by ID). The entry names the owner record, records the row at L1, and prints
`EXCEPTED <id>: covered with no row list, by <record>` each time it applies. One such entry is
`done-pkg-secret-print-3`; section 9 says what holds for `done-gap-wave1-small-4`.

## 4. Which readers enforce it
The central reader (`regression.read_rows`) enforces sections 2 and 3: every `regression.py` command reads through
it (the pull-request check's shards run through them), and so do the runner and the local cover. The other readers
that parse the table themselves, including the scheduled run's embedded selection by the old words, are not
changed by G1 and do not refuse (section 11 names who takes them).

## 5. Writing and repairing
- The table and the record are one update under the table's one write lock: read again, build both, check both, then
  write the record first and the table second. No reader sees half of it, including one that reads while the write is under way. An interrupted write is completed by running
  the same command again, and the refusal that follows says so.
- Drafting a row (`sync --write`) writes its row and its entry in that same update.
- Repair and list commands read without refusing, check only what they change, and list what is still wrong.
- Nothing silently drops or lowers a tag: an orphan's message offers a rename when a likely new id exists, and
  removal only for a row that is gone; identical duplicate entries are dropped, other duplicates ask for a choice;
  lowering `security` or `private` needs an owner record; a Principle 6 row is never set to `none`.
- No merge attribute is added: a merge conflict in the record shows as a conflict.

## 6. Commands
All new parsers and handlers live in the new module and register through one call; each is listed in `listing.json`
with what it writes, and `SKILL.md` shows one example each.
- `relevel [--dry-run] [--input FILE] [--risk-for ROW=TAG --owner-record ID]...` (the last pair may repeat).
- `level ID [--test-level L] [--risk R] [--covers A,B] [--remove] [--rename NEW] [--retime]`.
- `levels` (lists levels and problems), `levels --check` (offline; it reads no issue and writes nothing; exit 0 with
  "valid" when every entry is valid, or "not levelled" for a table that is not; exit 2 listing what is missing or
  wrong, each marked as a missing entry to fill or a stored entry to repair) and `levels --fill` (adds missing entries
  of non-defect rows offline, from the same rules). `relevel --dry-run` previews a full fill, defect labels included.
- `add` gains `--test-level`, `--risk` and `--covers`. Every documented `add` command keeps working: a new row that
  is not a defect gets L1 and the derived risk, and the command prints what it chose. Adding or relinking a defect
  reads its labels or refuses. `add --level` keeps its meaning (the old words, which still select what runs); its
  help says so, it is checked as before, and the record's `old` word is the word at the row's first entry and does
  not follow later edits. On a table that is not levelled, `add` writes no record and behaves as before.
- One L0 rule (section 7) applies to `relevel`, `add`, `level` and `level --retime`.
- **Changing a row's command** moves it from L0 to L1. L0 again needs a new measurement of that command
  (`level ID --retime` runs it and records seconds and `cmdhash`). A script that slows down while its command stays
  the same is not detected.
- A change to goal, category or link derives the risk again and never lowers it silently.

## 7. The re-levelling
Run once by the build, on the table as it is then, with its command, output and counts committed in the build
record; every row gets an entry, none is dropped, reordered or edited. Running it again fills only missing entries.
That run is the proof of done line 3 on the real table; it depends on that day's table, times and issue labels and is
not repeated by a check.
- `land` becomes L1 by default. A row is **eligible for L0** when its measured time is above zero and under 5
  seconds, its command and the scripts it names (followed three deep, by a word list in the module) use no network
  and no toy repository, and it is not tagged. Eligible rows are taken fastest first (ties by id) while the total
  stays at 45 seconds or less. The output gives the count excluded by each rule, why each otherwise eligible row was
  excluded (the matched word or rule), and the L0 ids.
- `nightly` becomes L1 when its measured time fits the pull-request check's per-row time limit (the setting the
  check uses) or the row has a limits-file entry; otherwise L2.
- `covered` takes the highest level of its covers. A row without a measured time starts at L1.
- A `draft` row (none today) keeps its old word in the record; the separate draft state belongs to a later goal.
- **Defect evidence:** labels of every linked issue are read once, at the build, with a per-call and an overall time
  limit, one retry and one read per address; a missing tool, sign-in, access, not-found, rate-limit, timeout and
  unreadable answer are told apart; nothing partial is written; path segments `.` and `..` are refused; no raw
  tool output or address is printed or written to any file. Access is checked before the build starts. A defect row
  that cannot be read is listed, all at once, and takes `--risk-for` with an owner record. No test uses the network.
- The record's reason names the time, the risk or the default. No committed file names another repository.

## 8. Risk data (Principle 6)
Requirement rules: DEL-9 (and the ids it absorbs) means `private`; GRD-4, GRD-5 and GRD-6 (and the ids they absorb)
mean `security`; `private` wins when both apply, including between a requirement tag and a defect label. One
function derives a row's tag for every command. A label whose name holds "security" means `security`; one holding
"private" or "privacy" means `private`; the labels found are written into the risk data. The list is pinned in the risk data, not read from the wiki on each
read; one check compares it with the Principles page, so a change to the page alone is caught only when that check
runs. Defect rows take their tag from the pinned label list.

Hand-tagged rows (they guard a Principle 6 requirement without naming it):
- `private`: scan-fail-closed, defect-5727-smoke-private-list, grd10-install-hooks, wiki-front-tree,
  wiki-front-private-scan, wiki-front-hardening, dlf-scan-every-path, pkg-no-echo-1, pkg-no-echo-2, machine-done-4,
  machine-done-11, machine-task-layout, ls-nothing-in-repo, set2-layers-show, tasks-briefs-real,
  roadmap-finished-not-queued, codex-run-ends-done, dlf-only-safety-waits, setup-refusal-writes-120,
  machine-hook-state, package-passes-3800, notify-new-events, eta-preflight-asked, dlf-lines-not-waits,
  dlf-setting-off-waits, set1-docs-format, ls-log-bounded, task-first, dlf-cut-refuses-open,
  dlf-mutation-controls, wiki-front-tracked, release-static-rules, make-room-3-package, make-room-b-3-package,
  pods-size, adoption-golden.
- `security`: owner-record-applies, delegated-record-accepted, rel-owner-only, perms-docs-check,
  worker-push-guard-refuse, gap-token-needs-live, preview-writes-nothing, no-token-would, known-no-block,
  st-setup-readonly, st-public-zero, defect-5609-one-merge-path, guards-rule-start, guards-resume,
  guards-worker-role, unattended-loop-recreate, mon13-two-layers, pods-independent, codex-fallback-start,
  machine-done-9, machine-done-10, merge-guard-base-head, merge-reach-fail-closed, st-pass, aut-regression-off,
  sync-not-connected, milestone-sync-no-source.
A listed id no longer in the table at the build is removed from the list and named in the build record.

## 9. Covered rows
| Covered row | covers |
|---|---|
| done-hard-eta-1 | eta-freeze, eta-checkin-table, eta-header-margin-setting |
| done-hard-eta-2 | eta-freeze, eta-budget-raise |
| done-hard-eta-3 | eta-health-missing, eta-health-rules |
| done-home-stale-1, done-home-stale-2 | home-stale-clears |
| done-held-time-charge-1 | held-charge-pauses |
| done-held-time-charge-2 | held-charge-idle |
| done-judge-stable-keys-1, done-judge-stable-keys-2 | judge-key-savings |
| done-apply-rerender-1, done-docs-v2-6 | apply-rerender-tables, apply-rerender-blocks |
| done-apply-rerender-2 | apply-rerender-blocks |
| done-toys-no-leak-1 | toys-no-leak-lane-pool, home-sandbox-4859 |
| done-toys-no-leak-2 | home-guard-catches-leak, toys-no-leak-schedule |
| done-homeguard-skills-main-1, done-homeguard-skills-main-2 | toys-no-leak-schedule |
| done-docs-v2-1, done-docs-v2-2 | doc19-diagram-passes, docs-v2-repo-passes |
| done-docs-v2-3 | doc19-diagram-passes, doc19-kind-row, doc18-howto-missing |
| done-docs-v2-4 | doc18-howto-missing, docs-v2-repo-passes |
| done-docs-v2-5 | doc18-howto-missing |
| done-agent-routing-1 | agent-routing |
| done-pkg-secret-print-3 | none: excused by ID (section 3) |
| done-gap-wave1-small-4 | none: see the sentence below |
`apply-rerender-blocks` is on the known-red list; a row it covers is not counted as proven while it is red. The record
states which rows prove a covered row; it does not state that they prove every word of its line, and the pull request
says so.

**done-gap-wave1-small-4:** it is excused by ID like `done-pkg-secret-print-3` (section 3), naming o988, the record
that removed the rules it states.

## 10. Rollout and merges
- Once G1 is on main, a branch that adds rows carries their record entries.
- A pull request that went green before G1 merged can still add a row with no entry; reading the table then refuses
  on main. The repair is `levels --fill` in a pull request from operation, and the message says so. A defect row
  needs its labels read. Hand tags come from the risk data by id, so a fill keeps them.
- The build merges main after each merge it needs and fills the entries of rows added since. The conflict repair that
  already mends the table does not touch the record; a fill follows it.

## 11. Size table (done line 5)
The default size table and the repository's settings file are not changed. A second default, used when a size row has
no `levels` key, gives small and medium `L0, L1` and large `L0, L1, L2`. A `levels` key is read from a copy of the
size row and is not treated as a check. It must be a list drawn from L0, L1, L2 that holds L0 and L1; otherwise the
read refuses once with `SIZING_BAD_LEVELS`, naming the size and the missing level. A size named `levels` is refused.
The release cut's own read of the table is unchanged and still reports its read-failure code beside the reason. The
sizing script imports no regression module.

**Left to later goals, and named in the pull request** (G2: running rows by level and the cover; G3: the scheduled
run; G4: retiring the old words): the record file instead of the page's column, with two sets of level words until G4;
the old words in the `goal_levels` setting, the pull-request level map and the runbook labels (G4); the draft state
column (G4); "a covered row is green when all its covers are" (G2); anything that uses a size's levels, including the
large goal's one L2 run (G2); the scheduled run's selection (G3); the other readers that parse the table (G2 to G4).

## 12. Stale results and the local cover
The new module is added to the runner's list of files whose change makes cached results and plans invalid. The local
cover never skips a row recorded at L0: L0 always runs locally.

## 13. Modules and size
New module `levels.py`; a second new module `levels_read.py` (the re-levelling and the evidence reading) only if the
first would reach the 20,480-byte limit. Each runs on its own and imports only the standard library or its own
folder. Every packaged script stays under it. `regression.py` is nearly full: the
`split` function moves whole to `completion.py` with an import back; the build measures every touched script before
and after, and if the hooks do not fit it moves another whole function and names it. No text is trimmed to make
room. `lanes.merged` is not changed and `narrow.py` is not touched.

## 14. Checks
Each new row's check is seen red first, as its own assertion, on the code before the change; checks run only in
isolated clones with their own `.git` and HOME (TD1965). Fixtures name no other repository.
| Row | Proves |
|---|---|
| `lvl-armed` | this repository's table and record are valid (`levels --check`) |
| `lvl-table-refused` | done lines 1 and 2 and every refusal of section 3, including a missing entry and a missing record; repairs that run on a refused table; no tag lowered without a record; an interrupted write completed by running again; a read during a write; a table that is not levelled reading as before; a change to the new module making cached results invalid; an L0 row never skipped by the local cover; the commands of section 6 |
| `lvl-relevel-record` | done lines 3 and 4: every row of the input kept, each with one level and its old word and reason; the L0 limit with the total named; the L0 eligibility rules one by one; covered levels; defect evidence failures without any network; nothing partial written; no link or repository name in any written file |
| `lvl-sizing-levels` | done line 5; the existing sizing check passes unedited |
| package line | done line 6: package gate after every code commit, scripts under the limit, no test loosened, no row red, no committed text naming the service repository |
Each new row names this goal's done line in its goal cell (`v110-lvl-relevel:N`), has its own record entry (L1) and
its first red date; each new toy declares what it reads, and `lvl-armed` is chosen by a change to the table, the
record, the risk data or the Principles page. The record run on the real table (done line 3) is
done once in the build and committed with its command, output and counts; the check on fixtures stays reproducible.

## 15. Docs
`SKILL.md` (command map and examples), `skills/loop-files.md` (record, risk data, input, every code), and the
re-rendered test page. No reviewed requirement text is edited.

## 16. Verify by hand (for the goal file at the pull request)
Commands run from `skills/workflow-regression/scripts/` as `python3 regression.py <command>`.
1. In a disposable copy with no record and a stand-in for the issue reader: `relevel`, then clear one entry's level
   and one Principle 6 tag and run `sync` (without `--write` it only reads and lists). Expect both rows refused by
   name.
2. In the real repository: `levels --check`. Expect "valid"; the record has as many lines as the table has rows.
3. In a disposable clone: drop L1 from one size in the settings on its base branch, then run
   `python3 skills/workflow-delivery/scripts/sizing.py size <slug>` with that goal's plan file and record present.
   Expect a `SIZING_BAD_LEVELS` refusal naming the size and L1.

## 17. Time
ETA 425 active minutes, time budget 240.
