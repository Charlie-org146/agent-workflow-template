#!/usr/bin/env python3
# reads: skills/workflow-delivery/scripts/sizing.py skills/workflow-delivery/scripts/fit.py skills/workflow-delivery/references/commands.md skills/workflow-setup/scripts/settings.py .loop/config.json dev/toy/lvl_fixture.py
"""v110-plan-by-size: at its start the plan step is told the forms its size's row lists (full, shorter refused, for a large
goal or one touching a safety class), and states REVW-5's round rule with plan_fix_reads."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
from lvl_fixture import DELIVERY, ROOT, check, done  # noqa: E402

sys.path.insert(0, DELIVERY)
import sizing  # noqa: E402

RUNS = tempfile.mkdtemp()
sizing.runs = lambda: RUNS
BASE = {"review_depth": "full", "risky_paths": [r"^\.github/"],
        "checks_by_size": {s: sizing.DEFAULTS[s] for s in ("small", "medium", "large")}}
TODAY = "today's depth text"  # has no 'never condense': only the start row or the stored size can add it


def prompt(state, cfg=None, ok=True, step="plan"):
    cfg = dict(BASE, **(cfg or {}))
    sizing.base_cfg = lambda: ("main", cfg, ok)
    return sizing.prompted(lambda s, st, r: TODAY)(step, dict({"slug": "g"}, **state))


SMALL = {"size": {"small": True, "why": "small: 3 done lines, one area"}, "goal": "fix a typo", "touches": ["skills/x/a.py"]}
text = prompt(SMALL)
check("plan-review one-round" in text and "red-team one-pass-no-rerun" in text,
      "a small goal's plan step starts with its row's forms named", text)
check("provisional" in text and "never condense" not in text.lower() and TODAY not in text,
      "the start text says the row is provisional and has no 'never condense'", text)
text = prompt(dict(SMALL, size={"small": False, "why": "large: 5 done lines"}))
check("never condense" in text.lower() and "one-round" not in text,
      "a large goal's plan step is told full, a condensed reply refused", text)
text = prompt({"goal": "x", "touches": ["a/b.py"]})
check("never condense" in text.lower(), "a goal with no frozen size is treated as large", text)
text = prompt(dict(SMALL, touches=[".github/workflows/x.yml"]))
check("never condense" in text.lower(), "a small goal touching a risky path is told full", text)
text = prompt(dict(SMALL, goal="rotate the password and token handling"))
check("never condense" in text.lower(), "a small goal whose words name a safety class is told full", text)
text = prompt(dict(SMALL, depth_override={"depth": "condensed", "why": "owner o1096"}))
check(text.startswith(TODAY) and "provisional" not in text and "never condense" not in text.lower(),
      "a depth_override is not changed by the start row", text)
text = prompt(dict(SMALL, one_review={"at": "t", "by": "goal.py new"}))
check(text.startswith(TODAY) and "one-round" not in text and "provisional" not in text,
      "a one_review goal is left to today's depth at plan start", text)
text = prompt(dict(SMALL, sized={"size": "medium", "reason": "r", "checks": {"plan-review": {"form": "full", "passes": 3},
                                                                             "red-team": {"form": "one-pass-no-rerun", "passes": 1}},
                                 "added": [], "evidence": {}}))
check("provisional" not in text and "never condense" in text.lower(),
      "a goal with a stored size gets its stored depth and no provisional text", text)
text = prompt(SMALL, ok=False)
check(text == TODAY, "an unreadable base config leaves today's prompt", text)
text = prompt(SMALL, step="review")
check("provisional" not in text and "such reads" not in text, "the review step is unchanged", text)
text = prompt(SMALL)
check("A plan gets the reviews its size's row lists, once." in text and "at most `2` such reads" in text
      and "A finding about wording alone is a build note at any round." in text,
      "the plan step states REVW-5's round rule with plan_fix_reads 2 by default", text)
check("at most `3` such reads" in prompt(SMALL, {"plan_fix_reads": 3}), "plan_fix_reads from the base config is used")
for bad in ("x", True, -1, 2.5):
    check("at most `2` such reads" in prompt(SMALL, {"plan_fix_reads": bad}), "plan_fix_reads %r falls back to 2" % (bad,))
# red team pass 1 (v110-plan-by-size): inputs that must stay full
for name, odd in (("a dot-slash path", {"touches": ["./.github/workflows/x.yml"]}), ("a backslash path", {"touches": [".github\\x"]}),
                  ("an upper-case path", {"touches": [".GITHUB/workflows/x.yml"]}), ("a dotdot path", {"touches": ["x/../.github/y"]}),
                  ("touches as a string", {"touches": ".github/workflows/x.yml"}),
                  ("small as the text false", {"size": {"small": "false"}}), ("small as 1", {"size": {"small": 1}}),
                  ("a list for goal", {"goal": ["a"]}), ("a None touch", {"touches": [None]}),
                  ("a bogus depth_override", {"touches": [".github/x"], "depth_override": {"depth": "x"}})):
    text = prompt(dict(SMALL, **odd))
    check("never condense" in text.lower() and "one-round" not in text, "%s is held to full at plan start" % name, text)
# red team pass 2 (v110-plan-by-size): more inputs that must stay full
for name, odd, cfg in (("a directory path with a slash", {"touches": [".github/"]}, None), ("a path leaving the repo", {"touches": ["../.github/x"]}, None),
                       ("a path with leading blanks", {"touches": [" .github/x"]}, None), ("touches as a dict", {"touches": {"a": 1}}, None),
                       ("touches as None", {"touches": None}, None), ("empty touches", {"touches": []}, None),
                       ("a GitHub surface", {"touches": ["github:wiki"]}, None),
                       ("a pattern for the dot-slash spelling", {"touches": ["./skills/x/a.py"]}, {"risky_paths": [r"^\./skills/"]})):
    text = prompt(dict(SMALL, **odd), cfg)
    check("never condense" in text.lower() and "one-round" not in text, "%s is held to full at plan start" % name, text)
check("one-round" in prompt(dict(SMALL, touches=["skills/x/a.py", "skills/x/b.py"])), "control: two files in one area stay small")
sys.path.insert(0, os.path.join(ROOT, "skills", "workflow-setup", "scripts"))
import settings  # noqa: E402
rows = {row[0]: row for row in settings.TABLE}
cfg = json.load(open(os.path.join(ROOT, ".loop", "config.json")))
check(rows.get("plan_fix_reads", (0, 0, None))[2] == 2, "settings.py lists plan_fix_reads with default 2", rows.get("plan_fix_reads"))
check(cfg.get("plan_fix_reads") == 2 and "plan_fix_reads" in cfg.get("_help", {}), "config.json holds plan_fix_reads 2 and its help line")
sys.exit(done())
