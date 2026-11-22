# auto-approve-off: design

Status: APPROVED (condensed; the owner decided the value, o806, and the cause is a single config key).

## Problem
`.loop/config.json` has `"auto_approve": true`, so `goal.py record` approves whatever a flow step leaves for the owner and logs it auto-approved. The owner said "Turn it off" (o806).

## Decision
1. Set `"auto_approve": false` in `.loop/config.json` (the only code-path input; `goal.py:280` reads `cfg.get("auto_approve") is True`). `auto_merge` stays as it is: the owner named only auto_approve.
2. Re-render what names the repo's value: the generated rows `.loop/START.md` (entry.py write) and `docs/wiki/How-to-use-Setup.md` (settings rows: `overridden: true` becomes `default`), then restamp the pages the render touches.
3. Rewrite the one hand-written sentence that says this repo runs with no gates, `docs/wiki/How-to-use-Delivery.md:48`: it must say `auto_merge` is on, `auto_approve` is off, and what a step leaves for the owner now waits.
4. Toy: in `dev/toy/test-goal.sh`, next to the "No gates" block (which already holds the negative control, auto_approve true: `AUTO-APPROVED`), add a case that reads this repo's committed config, asserts auto_approve is false there, and shows a PENDING reply holds (`WAITING`, status running, nothing logged auto-approved). Fold it into the existing `auto-approved` row (one more PASS line); no new row.

## Checked: no test reads the repo's value
`test-goal.sh`, `test-review-depth.sh` and `test-delivery-prd.sh` set their own config. `test-defect.sh:255` quotes the generic line in `skills/workflow-delivery/references/commands.md`, not this repo's config. `test-settings.sh` lists keys only. To be proved by the lane, not assumed: any row that renders the settings or START page from the repo config.

## Out of scope
`auto_merge`, `plan_ahead` (an owner's `approve ahead` answer still lets the plan step take the recommended answer; that is the owner's own word), the hold wording, any script change.

## Open
None for the owner.
