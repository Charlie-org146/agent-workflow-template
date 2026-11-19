#!/usr/bin/env python3
# windows: ok
"""Break one rule of the gap-wave1-small goal in the current checkout, so `regression.py red ID --break "python3 dev/toy/break-gap-wave1.py NAME"`
can show its row fails without it. usage: break-gap-wave1.py NAME"""
import sys

LANES = "skills/workflow-regression/scripts/lanes_cli.py"
BOARD = "skills/workflow-monitoring/scripts/board_status.py"
SETTINGS = "skills/workflow-setup/scripts/settings.py"
DEFECTS = "skills/workflow-health/scripts/defects.py"
COPY = "skills/workflow-docs/scripts/prdcopy.py"
AUTO = "skills/workflow-health/scripts/automation.py"
RUNS = "skills/workflow-regression/scripts/runs.py"
REG = "skills/workflow-regression/scripts/regression.py"
TOKEN = 'bool(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))'
BREAKS = {
    "floor-lanes-4": (LANES, '.get("min_free_memory_gb", 3)', '.get("min_free_memory_gb", 4)'),
    "floor-fallback-4": (LANES, "        need = 3", "        need = 4"),
    "floor-board-35": (BOARD, 'float(cfg.get("min_free_memory_gb", 3))', 'float(cfg.get("min_free_memory_gb", 3.5))'),
    "floor-table-4": (SETTINGS, '("min_free_memory_gb", REPO, 3,', '("min_free_memory_gb", REPO, 4,'),
    "ms-unchecked": (SETTINGS, "if source and not re.fullmatch(", "if False and not re.fullmatch("),
    "ms-unknown": (SETTINGS, '    ("milestones_source", REPO, "",', '    ("milestones_source_off", REPO, "",'),
    "ms-flagged": (DEFECTS, '{"regression_runs", "milestones_source"}', '{"regression_runs"}'),
    "img-any-file": (COPY, "(?:png|jpe?g|gif|svg|webp)", "(?:" + chr(92) + "w+)"),
    "token-digest": (AUTO, "live = args.live", "live = " + TOKEN + " or args.live"),
    "token-owed": (RUNS, "live = args.live", "live = args.live or " + TOKEN),
    "token-red": (REG, "runs.owed_clear(root, args.id, args.live)", "runs.owed_clear(root, args.id, args.live or " + TOKEN + ")"),
}

path, old, new = BREAKS[sys.argv[1]]
with open(path, encoding="utf-8", newline="") as handle:
    text = handle.read()
if text.count(old) != 1:
    sys.exit("cannot break %s: %r found %d times in %s" % (sys.argv[1], old, text.count(old), path))
with open(path, "w", encoding="utf-8", newline="") as handle:
    handle.write(text.replace(old, new))
