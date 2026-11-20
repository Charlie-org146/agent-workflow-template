# Generated links never depend on a checkout's git origin (TD407/TD408/TD410, operation-top under owner delegation; owner words about 05:25 'apply some of the small changes today'). Since #5455's commit 901133f3e (generated links: the organization origin), render.template_line falls back to TEMPLATE_REPO = jcl2018/agent-workflow-template (skills/workflow-docs/scripts/render.py:220) when .loop/config.json has no template_repo and the checkout has no origin; so the toys that copy the repo with git init (deploy-not-locked, deploy-section-optional, issues 5476 and 5477) print STALE README line and never DOCS OK, and a checkout whose origin still names jcl2018 renders the Tests page Run links wrong (the PC's #5480). The change: add "template_repo": "Charlie-org146/agent-workflow-template" to .loop/config.json; check that How-to-use-Automation's links render the same from a copy with no origin (render.repo_of's fallback) and feed the same key there if they do not. Small fix: one config line, at most one small script change, no new row unless one is needed for the How-to check. Target: pushed within 15 minutes

- Slug: template-repo-config
- Touches: .loop/config.json, skills/workflow-docs/scripts/render.py
- ETA: 460 active minutes (estimate 368m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a copy of the repo made with git init and no origin, when docs.py check runs, then it prints DOCS OK and no STALE README line, and the rows deploy-not-locked and deploy-section-optional pass (they fail on main today)
2. Given the same copy, then How-to-use-Automation and the Tests page render the same links as in a checkout whose origin is the organization URL, and a checkout whose origin is the old jcl2018 URL renders them the same too
3. Given this goal's diff, then only .loop/config.json's template_repo, at most one small change in render.py or the How-to renderer, any regenerated pages and the goal's record files change, every script stays under 20,480 bytes, and the PR's CI shows both deploy rows passing

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Copy the repo with `git archive HEAD | tar -x -C /tmp/copy`, run `git init` there and `python3 skills/workflow-docs/scripts/docs.py check`.
   Expect: DOCS OK: 16 pages, with no STALE line, and the same with a copy whose origin is the old jcl2018 URL.
2. In that copy run `python3 skills/workflow-docs/scripts/criteria.py render` and `git status --short`.
   Expect: nothing changed, so How-to-use-Automation and Tests render the same links with no origin as with the organization origin.
