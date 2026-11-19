# dev/package.py passes on main: the package fits its file cap and listing, so the package, adopt and sync rows pass again

- Slug: known-red-package
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. dev/package.py passes on main: the package holds 98 files or fewer (from 103), rules.py and report.py are within their size cap, and listing.json lists the 7 machines.py subcommands it now misses
2. Rows package-passes, package-passes-3800, package-headroom-held, package-rows-tracked, trim-package-98, plan-sizes, pods-size, adopt-set-3, adopt-set-4, adopt-set-5, sync-check-preview and sync-board-lag pass and leave .loop/regression-known.tsv; sync-check-preview and sync-board-lag print why when package.py refuses instead of exiting silently
3. No shipped behaviour changes beyond folding files and trimming size; nothing else changes; net test rows grow by at most 0

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
