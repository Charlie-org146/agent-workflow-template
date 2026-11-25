# The package checker never prints a matched credential or private-name text (urgent security repair, owner o1082)

- Slug: v110-pkg-secret-print
- Touches: dev/package.py, dev/toy, .loop/regression.tsv, dev/toy/test-package-no-echo.py
- ETA: 345 active minutes (estimate 273m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a shipped file holding a credential-shaped string or a private-prefix match, when dev/package.py checks safety (full or --static), then it refuses naming the file, the line number and the kind of match, and prints no part of the matched text; a toy shows the output holds none of the matched characters, seen red on today's code.
2. Given that check failing inside the pull-request workflow, when the run ends, then its log holds no part of the matched text.
3. Given the pull-request workflow runs of the last 90 days, when their logs are searched for the package checker's Safety lines, then the goal's record lists each run that printed a match by run id and kind only, never the text, so the owner can decide on rotation.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
