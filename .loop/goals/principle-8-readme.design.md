# principle-8-readme: design

## Problem
The template README, wiki Home and Principles page show seven principles. The owner (record o482, 2026-11-19 20:53 PT, TD242) approved an eighth, "Honest, verified and on time", with one new bullet on each of six existing requirements (CHK-1, DEL-17, OPS-1, HLT-2, HLT-4, OPS-2) and REG-9 listed unchanged. No new requirement ID and no new feature.

## Approaches
1. Edit the three pages by hand. Cheap, but Part 2 repeats HLT-2 three times and the docs check would not hold the eighth principle in place.
2. Make the one principle list (`commands.md`, "The principles") the single source: add row 8, then write section 8 on the three pages from the owner-approved draft by a throwaway script, and revise the six requirements through `criteria.py revise` with the owner record. Chosen: `pageformat.py` already reads the list, so the README check, the Principles page check and health's PRINCIPLE lines pick up the new row with no script change, and the negative controls live in the existing toy tests.

## Choices
- Section 8 sentence, diagram, seven-row table and Follows cells are the approved draft's text, byte for byte. The Follows verdict for all six new rows is "adapted, v2.0 planned" (none of these tools can run inside a chat-session loop); REG-9 keeps its own Follows, version and flow from its existing row, with the summary "Unchanged; it already serves this principle".
- The six bullets land as `(v2.0 planned)` sub-bullets exactly as approved, each through `criteria.py revise <ID> --owner-record o482`, which leaves them Unreviewed until the owner re-reviews. HLT-2's one extra change is its principle count: "seven" becomes "eight", and "principles 6 and 7 print UNREAD until their Attention and References groups exist" becomes "6, 7 and 8 ... Attention, References and Honesty groups".
- Principle 8 maps to the health group `honesty`, which does not exist yet, so health prints `PRINCIPLE 8 ... UNREAD (honesty)` exactly as it does for principles 6 and 7.
- The diagram is `docs/wiki/principle-10-honest-verified-and-on-time.svg` (docs, not part of the shipped package); the overview diagram's "six principles" becomes "eight".
- DOC-19's "stands alone" check rejects links outside the repo, so the five new Follows origins (blogs.eclipse.org, github.com/in-toto/attestation, research.google, standards.ieee.org, www.joelonsoftware.com) go in `public_origins`; START.md is regenerated because the config changed.
- No script changes: `pageformat.py` (18,994 bytes) and every other script are untouched.

## Open questions
- None for the owner. The one gap the draft names (OPS-2's "keeps working while capped" half has no reference of its own) is the draft's own note; the approved bullet is used as written.
