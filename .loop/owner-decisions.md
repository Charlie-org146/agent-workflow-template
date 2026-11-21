# What waits for the owner (DEL-3.1)

This one file says what waits for the owner. Nothing else waits. Every session reads it; full auto answers everything not named here on the recommended path
and records the options, the reason and how to undo it. Only the owner's own words change this file: a change needs an owner-words record naming it.
Item 1 is the safety classes, which the tools keep as patterns in code; items 2 to 5 are matched by the `kind:` a worker reports or by the `match:` pattern.
A question is on the list when its kind or its words match. A line starting `always-ask:` names a goal (or `*`) the owner wants asked about, with the owner record it came from.

1. The safety classes: deleting what can't be restored, money, security and sandbox settings, private data, steward merges.
2. What my features promise: writing or changing a principle, a feature or its limits, marking a feature Reviewed, and loosening a test.
   kind: promise
   match: what (?:a|my|the) features? promises?|(?:write|writing|change|changing) (?:a|the) principle|loosen\w* (?:a|the) test
3. Freezing a release's brief.
   kind: brief
   match: freez\w+ .{0,30}brief
4. Shipping a major release, or merging a major template update into another repo.
   kind: major
   match: \bmajor (?:release|template update)
5. Posting anything to a project outside my own repos.
   kind: external
   match: \bpost\w* .*(?:outside|another) (?:my )?(?:own )?(?:repos?|project)
