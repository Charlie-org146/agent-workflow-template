# prd-principles: the README holds only the eight principles and how the features enforce them, a Principles page shows each with its diagram, and health gives one verdict per principle (DOC-23, HLT-2; owner o35, o37, o39, o43)

- Slug: prd-principles
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the template repo, when the docs check runs, then the README holds only its title, the eight principles each with its one-sentence statement, its diagram and the requirement IDs that enforce it, and one link to the wiki Home; the check fails a README with any other section or a principle sentence that differs by a word from the list health uses (DOC-23).
2. Given the wiki, when it is published, then a Principles page shows the same eight sentences, each with its diagram as an SVG file under docs/wiki and the requirement IDs that enforce it; every cited ID either resolves to a requirement on a page or is listed as planned with the regroup goal that adds it.
3. Given a health check, when it runs, then after the twelve groups the report prints one verdict for each principle from the groups under it (1 Traceability; 2 Requirements, Tests, Controls; 3 Consistency, Docs; 4 Freshness, Hygiene; 5 Performance, Size; 6 Security and privacy; 7 Adoption), red when any of its groups fails; principle 8 prints UNREAD until its Attention group exists, and UNREAD is never green; the twelve groups and their names are unchanged.
4. Given the pages, when this goal merges, then DOC-23 is added and HLT-2, DOC-15 and DOC-18 carry the draft text from prd-rewrite-to-10.md as new revisions through the revision tooling from prd-revisions, with no other Reviewed requirement changed; the README content that moves out (How to use, Commands, Getting started, About this repo, File reference, Settings, Automation) is on Home or the How-to-use pages, nothing lost; each new rule has a regression row seen failing and passing, with zero rows added net.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
