# dev/package.py passes on main: listing.json names every command, and a row keeps a new command from shipping unlisted.

- Slug: listing-commands
- Touches: listing.json, dev/toy, .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. listing.json commands names apply, forward and wiki-only, and python3 dev/package.py builds the ZIP with no Disclosure failure.
2. A row runs a toy that fails when any add_parser command is missing from listing.commands, seen red.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
