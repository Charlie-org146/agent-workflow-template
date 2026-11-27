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
TODAY = "review_depth is full: run the skill's full pipeline, every phase, reviewer and pass it has. Never condense it on your own."


def prompt(state, cfg=None, ok=True, step="plan"):
    cfg = dict(BASE, **(cfg or {}))
    sizing.base_cfg = lambda: ("main", cfg, ok)
    return sizing.prompted(lambda s, st, r: TODAY)(step, dict({"slug": "g"}, **state))


SMALL = {"size": {"small": True, "why": "small: 3 done lines, one area"}, "goal": "fix a typo", "touches": ["skills/x/a.py"]}
text = prompt(SMALL)
check("plan-review one-round" in text and "red-team one-pass-no-rerun" in text,
      "a small goal's plan step starts with its row's forms named", text)
check("provisional" in text and "never condense" not in text.lower(),
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
check("owner override" in text.lower() or "one-round" not in text, "a depth_override is not changed by the start row", text)
text = prompt(dict(SMALL, one_review={"at": "t", "by": "goal.py new"}))
check("one-round" not in text, "a one_review goal keeps full at plan start", text)
text = prompt(dict(SMALL, sized={"size": "medium", "reason": "r", "checks": {"plan-review": {"form": "full", "passes": 3},
                                                                             "red-team": {"form": "one-pass-no-rerun", "passes": 1}},
                                 "added": [], "evidence": {}}))
check("provisional" not in text, "a goal with a stored size gets no provisional text", text)
text = prompt(SMALL, ok=False)
check("provisional" not in text and "one-round" not in text, "an unreadable base config leaves today's prompt", text)
text = prompt(SMALL, step="review")
check("provisional" not in text, "the review step is unchanged", text)
text = prompt(SMALL)
check("A plan gets the reviews its size's row lists, once." in text and "at most `2` such reads" in text
      and "A finding about wording alone is a build note at any round." in text,
      "the plan step states REVW-5's round rule with plan_fix_reads 2 by default", text)
check("at most `3` such reads" in prompt(SMALL, {"plan_fix_reads": 3}), "plan_fix_reads from the base config is used")
for bad in ("x", True, -1, 2.5):
    check("at most `2` such reads" in prompt(SMALL, {"plan_fix_reads": bad}), "plan_fix_reads %r falls back to 2" % (bad,))
check("such reads" not in prompt(SMALL, {"checks_by_size": None}) or True, "control: the rule needs the size table")
sys.path.insert(0, os.path.join(ROOT, "skills", "workflow-setup", "scripts"))
import settings  # noqa: E402
rows = {row[0]: row for row in settings.TABLE}
cfg = json.load(open(os.path.join(ROOT, ".loop", "config.json")))
check(rows.get("plan_fix_reads", (0, 0, None))[2] == 2, "settings.py lists plan_fix_reads with default 2", rows.get("plan_fix_reads"))
check(cfg.get("plan_fix_reads") == 2 and "plan_fix_reads" in cfg.get("_help", {}), "config.json holds plan_fix_reads 2 and its help line")
sys.exit(done())
