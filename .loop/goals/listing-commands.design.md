# Design: listing-commands

Problem: merge-unblock and ff-stash-fix added operate.py commands apply, forward and wiki-only without naming them in listing.json, so package.py's Disclosure rule refuses and no ZIP builds.

Approaches:
1. Add the three names to listing.json and rely on the existing package-passes row (skipped on Windows). Cheap, but a Windows lane never sees the miss.
2. Add the names and a small toy that runs package.check_disclosure directly on every platform, with a negative control, behind a row. Small cost, no new risk.

Chosen: 2. The listing holds names only, so no per-command descriptions are added.

Done lines: line 1 is the three names (package.py then builds); line 2 is the toy plus row, seen red.

Open questions: none.
