# Turn auto_approve off in the template repo's committed config, as the owner said (o806), so no step leaves an owner item auto-approved (patch)

- Slug: auto-approve-off
- Touches: .loop/config.json, dev/toy, .loop/regression.tsv, docs
- ETA: 295 active minutes (estimate 233m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given .loop/config.json, then auto_approve is false (owner o806), settings.py show reports it false, and the generated settings rows and docs that name the repo's value agree.
2. Given a step reply with a PENDING owner item, when goal.py record runs in this repo, then the step holds for the owner and nothing is logged auto-approved; a toy shows it, with a negative control where auto_approve is true.
3. Given the package, then every script stays under 20,480 bytes and none newly crosses 19,000, the package stays within MAX_FILES, no test is loosened, no existing row turns red, and committed text never names the service repo.

## Verify by hand

1. Run `python3 skills/workflow-setup/scripts/settings.py show`. Expect: the line `auto_approve | false | repo | .loop/config.json`.
2. Run `git show HEAD:.loop/config.json` and look for `auto_approve`. Expect: `"auto_approve": false` and `"auto_merge": true`.
3. In a scratch repo with this config, record a step reply that ends with `PENDING: approve the design`, `DEPTH: full`, `STEP: pending` (goal.py record). Expect: a line starting `WAITING` with the ask, the run record's status `waiting`, and no `AUTO-APPROVED` line.
4. Open `docs/wiki/How-to-use-Delivery.md` and `listing.json`. Expect: neither says this repo runs with no gates or that owner items are approved automatically; both say `auto_merge` is on and `auto_approve` is off.
5. Run `bash dev/toy/test-goal.sh 2>&1 | grep -F "PASS: a real PENDING item among none lines still waits"`. Expect: one PASS line.
