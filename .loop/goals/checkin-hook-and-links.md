# README and Home link the organization repository, and the check-in hook's section list follows CHK-1 (TD422, approved by operation-top under owner delegation DOC-2, o486). (a) README.md and docs/wiki/Home.md hold about 70 links to github.com/jcl2018/agent-workflow-template while the repository is github.com/Charlie-org146/agent-workflow-template; the links are fixed at their source (the renderer or the config value it reads, template_repo now set), so a render writes the organization URL and nothing is fixed by hand. (b) reply_hook.py SECTIONS still lists the old section names: the worker DRAFTS the new order from the approved CHK-1 text and the board order and sends it to operation-mac; it is NOT built in this goal until operation-top answers

- Slug: checkin-hook-and-links
- Touches: skills/workflow-docs/scripts, README.md, docs/wiki/Home.md
- ETA: 425 active minutes (estimate 338m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a fresh render of README.md and docs/wiki/Home.md, then no link names github.com/jcl2018/agent-workflow-template, every repository link names github.com/Charlie-org146/agent-workflow-template, the change sits in the renderer or its config (not hand-edited links), and docs.py check passes with no STALE line
2. Given reply_hook.py, then its SECTIONS is unchanged in this goal, and the pull request carries the drafted new order with the CHK-1 text it follows, for operation-top's answer
3. Given this goal's diff, then only the renderer or config line, the regenerated README and Home, and the goal's record files change, every script stays under 20,480 bytes, and the private-name scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `grep -c "jcl2018" README.md docs/wiki/Home.md`.
   Expect: 0 for each file; every repository link names the organization repository.
2. Run `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: DOCS OK with no STALE line, and `git diff skills/workflow-monitoring/scripts/reply_hook.py` is empty.
