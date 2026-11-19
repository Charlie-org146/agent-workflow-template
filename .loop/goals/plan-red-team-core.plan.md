# Plan: plan-red-team-core

Checked against the code: `layers.py` already holds `redteam input|record|due` (cherry-picked); `mailbox.py` (8.9 KB) has `main`,
imports `machines`, and is the file `mailbox.py finding` (ops-findings) is routed to; `guards.py` is imported by `goal.py` and
holds the gates (`waiting_gate`); `goal.py` `cmd_step` is where `goal.py step SLUG build` starts a build; `state_dir()` is
`<git common dir>/loop/runs` and `owner-words.tsv` sits one level up, in `<git common dir>/loop`.

## Build steps

1. `mailbox.py`: add `plan_input(root, slug)` (done lines, design, plan, the principles from docs/wiki/Principles.md, the request),
   `plan_parse(text, count)` (lines `A:`, `R:`, `B<n>:`, `C:`; refuse a `B` with no number or a number outside the principles),
   `plan_record(common, root, slug, text, now)` (write `<common>/loop/redteam/plan-<slug>-<stamp>.json`: time, plan sha1, four
   lists), `plan_accept(common, slug, n, record)` (write `plan-<slug>.accept.json`; refuse an id owner-words.tsv does not hold);
   wire `plan-review`, `plan-record`, `plan-accept` in `main`; keep it under 19,000 bytes.
2. `guards.py`: add `plan_gate(g, state)`: newest `plan-<slug>-*.json` whose plan sha equals the plan file's sha; every break
   needs an owner-words.tsv record in the accept file, else refuse (`REFUSED (no try used)`, exit 2, with the fix). `goal.py`
   `cmd_step` calls it when the step is `build`. Trim prose in both files so each ends no larger than it started.
3. `layers.py`: the routes print the ops-findings command; trim the hourly code if needed to stay under 19,000.
4. Tests in `dev/toy/test-three-level.py` (record and parse, read-only proof, negative controls) and a gate test that runs
   `goal.py step` in a toy repo; chain the new checks onto existing rows (rows stay 1300) and prove each red once.
5. Fill `## Verify by hand`; render Tests; the HLT-2 bullets wait for the owner (not written before approval).

## What could break

- goal.py, guards.py: already over 19,000 bytes; any growth fails the size rule, so the trim must land first.
- A goal with no review, or whose plan changed, must still build: the gate only blocks a recorded break on an unchanged plan.

## Out of scope

Starting the reviewer session, sending to top, filing issues (the machine session and `mailbox.py finding` do these), new IDs,
a new file.

