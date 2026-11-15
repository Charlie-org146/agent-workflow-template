# Health sweep (2026-11-15)

Run on the owner's Windows PC against origin/main `b3e89e73`. Tracking issue: [#4365](https://github.com/jcl2018/agent-workflow-template/issues/4365), whose one summary comment holds the grouped findings. Nothing was fixed, mailed or posted as a digest, and the `Regression:` issues were left alone.

## Closed

Closed: 104

Each issue was closed with a comment naming the finding that `health.py preview` lists as no longer found. They were closed by hand because `health.py file` crashes on its close path (`KeyError: 'label'` in `file.py args_of`).

| Group | Closed |
|---|---|
| size | 58 |
| consistency | 20 |
| performance | 13 |
| docs | 5 |
| adoption | 4 |
| traceability | 2 |
| requirements | 2 |

Left open on purpose: #3822 (a Mac-only rule, skipped on this PC).

## Still open

Open health issues: 113, of which 12 sit outside a Backlog milestone and count for v1.0.0.

| Group | Open |
|---|---|
| size | 56 |
| performance | 35 |
| adoption | 11 |
| requirements | 5 |
| traceability | 2 |
| hygiene | 2 |
| freshness | 1 |
| docs | 1 |

Outside a Backlog milestone: #4223 (monitoring SKILL.md at 151 lines), #3803, #3804, #4142, #4143 and #143 (requirements without rows), #3879 and #4025 (fixed defects without a defect test), #347 and #3903 (Documentation stale from windows-safe's `a26bf376`), #3810 (nightly last ran 2026-11-11), #3822 (Mac task).

## Expected with scripts-b and scripts-c

The size WARN starts at 90% of the 20,480 byte cap (18,432 bytes). scripts-b (PR #4278, docs and release) and scripts-c (health and regression) aim at 19,000 bytes, which is still above that line, so they close no size issue unless a script ends below 18,432. Up to 24 close if they do: docs 9, release 4, health 7, regression 4. Expected at the 19,000 target: 0.

## Defect found, not fixed here

`health.py file` crashes at its first close or reopen action: `args_of` in `file.py` builds all four argument lists eagerly and the "open" one reads `act["label"]`, which a close or reopen action lacks.
