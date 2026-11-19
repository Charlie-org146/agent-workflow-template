# dev/package.py passes on main with the package at 100 files and the v2.0 headroom target 100 (TOP-DECISION 47, cap o70), so the package, adopt and sync rows pass again; replaces known-red-package, carrying its commits

- Slug: known-red-package-100
- Touches: not declared
- ETA: 290 active minutes (estimate 231m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. dev/package.py passes on main: the package holds 100 files or fewer (from 103), the package-headroom target is 100 for v2.0 (TOP-DECISION 47; the hard cap of 100 is unchanged), rules.py and report.py are within their size cap, and listing.json lists the 7 machines.py subcommands it missed; no function is scattered into an unrelated script
2. Rows package-passes, package-passes-3800, package-headroom-held, package-rows-tracked, trim-package-98, plan-sizes, pods-size, adopt-set-3, adopt-set-4, adopt-set-5, sync-check-preview and sync-board-lag pass and leave .loop/regression-known.tsv; MCH-5 is revised path-only (mailbox.py reply to machines.py reply) with its How-to and commands.md matching; a v2.1 issue is filed to restructure board_model.py and lean.py and bring the headroom back to 98
3. No shipped behaviour changes beyond folding files, trimming size and the AST-identical reindent; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
