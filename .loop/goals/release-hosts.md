# The release package's network disclosure stays true after the approved README added reference links (TD425, TD428; operation-top under owner delegation DOC-2, o486). Release run 44761417118 failed with 'Disclosure: host eslint.org / rework.withgoogle.com / www.agensi.io / www.atlassian.com / www.gitguardian.com is not in listing.network' beside 'Size: 105 files'. These are reference links in shipped text, not hosts the package contacts. THIS GOAL IS A DRAFT FIRST: the worker reads dev/package.py's disclosure rule and the shipped files, and sends operation-mac a fix that keeps both true (the disclosure lists only hosts the package contacts, and the check is not loosened), for example keeping the references where the package does not ship them, or a separate declared reference-links section if the rule already allows one; if no such fix exists it says so and it goes to the owner. It also drafts adding the release rule checks (Size, Disclosure) to the PR check. Nothing is built until operation-top answers; while swap is 95% or more only text drafts run

- Slug: release-hosts
- Touches: dev/package.py, listing.json
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the draft, then it names each of the five hosts, the file and line that carries it into the package, and a fix that keeps listing.network limited to hosts the package contacts without loosening the disclosure check, or it states that no such fix exists
2. Given the draft, then it describes how the PR check would run the release rule checks (Size, Disclosure) on the merged ref, with the files it would touch and their byte headroom
3. Given this goal before operation-top answers, then no file in the repository is changed except the goal's own record files

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/package.py`.
   Expect: no Disclosure line; only `FAIL Size: 105 files, at most 100 allowed` remains.
2. Run `python3 dev/toy/test-listing-commands.py`.
   Expect: PASS for the README hosts, and PASS for both negative controls (the five fail without the README-links entry, an unlisted README host still fails).
