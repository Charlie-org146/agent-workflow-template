# Health checks every principle, closing gap cluster G08 (HLT-2.17, HLT-2.18, HLT-2.19; issue #5239), the (v2.0 planned) principle-check bullets of HLT-2 on the v2.0 path (owner o355 gap scope, o234; TOP-DECISION 143; PC o242).

- Slug: health-principles
- Touches: not declared
- ETA: 275 active minutes (estimate 219m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. health check prints a red PRINCIPLE line for any of the six principles with no Reviewed requirement under it or no rule under it that can fail, and a Reviewed requirement that names no principle fails Requirements; each new rule has a negative control run against a deliberately broken copy
2. Health reads the six principles from the README list, the health commands reference shows the same six (no 'eight principles' left anywhere), and a README principle sentence that differs from that list by a word fails health with the line named
3. health review prints, per principle, the requirements enforcing it, their tests, and the principles with none or weak enforcement
4. Every changed row is proven seen-red, no script grows past 19,000 bytes and judge.py stays at or under 18,999 (more code goes to a script with room, never a new file), and net regression rows are 0 or fewer

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 skills/workflow-health/scripts/health.py check`.
   Expect: six PRINCIPLE lines, principle 6 UNREAD, the others green, and `PASS controls principle-map control: fires on its fixture`.
2. Run `python3 skills/workflow-health/scripts/health.py review`.
   Expect: after the findings, a PRINCIPLES block with one line per principle listing its Reviewed requirements and test counts, WEAK on any with no test.
3. Remove one requirement row from docs/wiki/Principles.md (a scratch copy) and run health check.
   Expect: a FAIL principle-map row naming that Reviewed requirement as under no principle.

