# Plan: plan-red-team-v20

Checked against the code: `layers.py` has `collect`, `board`, `publish_board`, `read`, `write`, `main`; it imports `machines`
(`me`, `shared`, `sh`, `read_json`) and `graph`; `operate.py` calls `layers.publish_board` in the top pass, so the nudge
needs no `operate.py` change; `dev/toy/test-three-level.py` imports `layers` and already builds two-machine STATUS data;
`.loop/regression.tsv` row `no-done-line-refused` (goal DEL-1) exists and the table is at its 1300-row cap.

## Build steps

1. `layers.py`: add `REDTEAM = "redteam"` folder constants and four helpers: `reviewer_input(common, now)` (board + one
   compact STATUS line per machine with age + the instruction block), `parse_reply(text)` (lines `A:`, `I:`, `R:`; exit with a
   refusal unless exactly one `R:`), `record(common, text, now)` (writes `<common>/loop/redteam/<UTC stamp>.json` with
   timestamp, the three lists and each item's route; returns the routing lines), `due(common, now, eta)` (DUE or ok).
2. `main`: add `redteam input|record|due` (record reads FILE or `-`; due takes `--eta ISO`). `publish_board` appends the due
   line when a pass is due. Keep layers.py under 19,000 bytes; update its docstring usage block.
3. `dev/toy/test-three-level.py`: add checks (below). `.loop/regression.tsv`: chain the new greps onto row
   `no-done-line-refused` (rows stay 1300). Re-render Tests tables with the docs command.
4. `docs/wiki/Delivery.md`: one Unreviewed bullet under DEL-1 (wording sent to the owner first). Run workflow-docs check.
5. Fill `## Verify by hand` in the goal file.

## Tests (each seen failing before, passing after)

- input holds both machines' STATUS and the board, and asks for three lists. record writes a timestamped JSON with the three
  lists. A wrapper on `open` and `subprocess.run` proves the only writes are under `<common>/loop/redteam/`, repo file hashes
  are unchanged, and no merge, push, gh or send call happens. Negative control: two `R:` lines refused, nothing recorded.
- due: DUE with no record; ok at 59 minutes; DUE at 61; DUE with an ETA 30 minutes out and no pass since; board line appears
  from publish_board only when due. Routes: `A:` to ops-findings, `I:` and `R:` to a proposed TOP-DECISION.
- `regression.py red` on the chained row proves the new checks fail on main's layers.py.

## What could break

- layers.py size (cap 19,000): trim prose, no extra file. The board text gains a trailing line only when due; existing board
  order tests read sections by index and are unaffected. The chained row now needs three-level to pass: it already runs fast.

## Out of scope

Starting the reviewer session, sending to top, filing issues (the machine session and `ops-findings-v20` do these), any
change to `operate.py`, new requirement IDs, other pages.

