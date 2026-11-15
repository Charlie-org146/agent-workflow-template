# Plan: listing-commands

Steps:
1. listing.json (commands): add apply, forward, wiki-only (operate.py add_parser, confirmed at operate.py:343-347).
2. dev/toy/test-listing-commands.py: runs package.check_disclosure over the shipped .py and SKILL.md files and fails if listing.commands lacks a name; a negative control drops "apply" and must be caught.
3. Row listing-names-every-command (land) runs the toy; seen red by removing "apply".

Tests: done line 1 is dev/package.py passing (99 files); done line 2 is the row, seen red.
Could break: package cap of 99 files (shipped files only; the toy is under dev/, not shipped).
Out of scope: per-command descriptions (the listing holds names only), other Disclosure rules.
