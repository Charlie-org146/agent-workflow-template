# package-green design

Problem: #3800 (dev/package.py must pass on main) was fixed by windows-safe (v0.28.71); #2874 (setup should say up front that un-reviewing a locked requirement needs the owner's own sentence) is open.

Approach A: one NOTE line in setup.py's first output plus a SKILL.md "After it runs" item, proved by a toy. Approach B: a new reference file, which would break the 98-file cap. Chosen: A. setup.py is at 20,460 bytes, so the line is kept short; scripts-c will trim it later. The Documentation page already states the rule (DOC-2, reviewed), so no reviewed text changes.

Done lines: 1 is met by dev/package.py passing now (98 files, PASS), kept proven by the existing package-gate-head row; 2 by row setup-owner-words-up-front, seen red.

VERDICT: self: approve
