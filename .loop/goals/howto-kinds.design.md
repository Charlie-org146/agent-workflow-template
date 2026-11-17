# howto-kinds design

Problem: How-to-use pages list what a feature delivers in no fixed form, the README still holds How-to-use tables, and nothing checks that a feature page's commands are on its page (#4677, owner o78).

Approaches:
1. Port the adopted repo's rules into docs check: a What's delivered table whose rows each name a Kind, one block per row with that Kind's fields, a coverage check for commands, and a links-only README (DOC-5 reworded, Home links the page). Additive and testable.
2. Leave the README tables and add the Kind rules only. Rejected: the owner asked for links only.

Chosen: 1. DOC-4 and DOC-5 are reworded under owner record o87 and left Unreviewed; the Kind rules are sub-bullets of DOC-19 (the Documentation page is at criteria_max).

Each done line: 1 needs the toy checks and negative controls; 2 the listed-commands check; 3 all nine pages typed, docs check clean, and the Documentation page stating the rules with test rows, the wording left to the owner.

Open questions: DOC-18's third sub-bullet (Reviewed) still says the README keeps a few things to say; it needs the owner's record to reword.
