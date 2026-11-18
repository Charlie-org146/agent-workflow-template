# Delivery, Release, Setup and Machines carry the v2 rewrite text through the revision tooling, each requirement on the page it belongs to (owner o35, o37, o38, o39, o44, o46)

- Slug: regroup-delivery
- Touches: not declared
- ETA: 290 active minutes (estimate 232m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the Delivery, Release, Setup and Machines pages, when this goal merges, then every requirement in those four sections of prd-rewrite-to-10.md (Delivery 10, Release 13, Setup 17, Machines 6) has that text on its page as a new revision through the revision tooling from prd-revisions, with REL-9 to REL-13 and MCH-4 to MCH-6 added and every requirement that moves between pages retired on its old page as moved to its new ID; no requirement outside these four features changes.
2. Given a moved or renumbered requirement, when the docs and health checks run, then every test row, issue link and How-to item that cited its old ID points at the new ID, the old ID still resolves through its moved-to marker, and Home lists the four pages with their milestones (Release none) and Topic as before.
3. Given the merged pages, when wiki.py prepare and the regression lane run, then the Tests tables re-render with zero regression rows added net, each new rule has a row seen failing and passing, wiki.py prepare is clean and entry.py check prints ENTRY OK.
4. Given the shipped package, when this goal merges, then no shipped file is added, no script crosses a size line it was under on main, and no page other than these four, Home and the Tests page changes.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: it prints no LINK, HOWTO, FORMAT or TESTS line (the one CAP Setup line waits on the owner's cap decision).
2. Open docs/wiki/Release.md and read REL-9 to REL-13, then its Revisions section.
   Expect: each is a title with sub-bullets, and REL-1 to REL-8 show an r2 row above their r1 row.
3. Open docs/wiki/Delivery.md and search for DEL-5.
   Expect: it appears only under Retired as "moved to REL-9"; DEL-10 and DEL-11 read "moved to MCH-5".
4. Open docs/wiki/Machines.md.
   Expect: MCH-1 and live MCH-2 and MCH-3 stand, with MCH-4 to MCH-8 added.

