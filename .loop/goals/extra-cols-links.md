# checkin.py reads a docs.tsv with extra columns, and DOC-19 lets an allowed origin's link pass when a ) or backtick follows it

- Slug: extra-cols-links
- Touches: not declared
- ETA: 295 active minutes (estimate 235m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. checkin.py and every other reader of .loop/docs.tsv (mend.py feature_of first) take the first two columns of a row and ignore any extra ones, such as a Notion sync column; a test row runs checkin.py against a repo whose docs.tsv has three-column rows, and it exits 0
2. DOC-19's outside-link match (prdcopy.py AWAY and the check that reads it) ends a URL before a trailing ), backtick, quote or sentence punctuation, so a link to an origin listed in public_origins or scripts/public-origins.json passes when written as [text](https://host/path) or inside backticks; a test row covers both forms, and an unlisted origin is still reported
3. Nothing else changes: no wiki page wording changes, no spec text changes, and the net test-row count grows by at most 2

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
