# gap-cheap-fixes design

Problem: three README gaps found by readme-conformance's audit are cheap to close (TOP-DECISION 128, owner records o236 and o243): five `gh` calls still put a long body on the command line, which Windows caps (MCH-1.7); `goal_lane_minutes` is a second lane limit beside the lane budget (REG-7.1); and health's `criteria_max` default (6) disagrees with the documented default (10).

Approaches:
1. Write a temp body file at each call site. Cost: about 150 bytes a site; milestones.py and prdcopy.py sit at 18.9 KB, so it cannot fit under 19,000.
2. Pass the body on stdin with `--body-file -` and `input=text` (gh reads `-` as stdin; `prd.out` already forwards `**kw` to subprocess). Cost: +16 bytes a site. For goal_lane_minutes: delete the LANE-line note and health's goal-lane warning and retire the setting, so `test_budget_minutes` is the only lane limit. For criteria_max: make rules.py default to 10.

Chosen: 2, the only shape that keeps every touched script under 19,000 bytes.

What each done line needs:
1. merge.py, milestones.py and prdcopy.py use `--body-file -`; row pr-body-by-file covers all four scripts with an in-row negative control, seen red with the old `--body` back.
2. lane.py and health's milestone.py stop reading goal_lane_minutes; the setting leaves settings.py, settings.md, survey.py, config.json and the commands.md lines; rows lane-over-minutes and health-timing now assert the opposite.
3. rules.py defaults to 10; row cap-default-10 also checks health's requirements-per-page rule with a 10-page and an 11-page fixture.
4. No requirement text, no new shipped file, net rows 0, scripts under 19,000 bytes (merge.py 18982, milestones.py 18996, prdcopy.py 18929).

Open questions: the toy rows cannot be seen red on Windows (their toys exit 77), so three rows need a Mac proof.
