"""The workflow writer, moved whole out of actions.py (owner o994): it checks the settings and writes regression.yml."""
import json
import os
import re
import sys


def write(root, default, render):
    try:
        with open(os.path.join(root, ".loop", "config.json")) as handle:
            cfg = json.load(handle)
    except (OSError, ValueError):
        cfg = {}
    cfg = cfg if isinstance(cfg, dict) else {}
    cron, levels = cfg.get("regression_cron") or default, cfg.get("ci_levels") or "nightly"
    if levels not in ("land", "nightly"):
        sys.exit("REFUSED: ci_levels is %r, not land or nightly. Fix: edit .loop/config.json." % (levels,))
    if cron != "off" and not (isinstance(cron, str) and re.fullmatch(r"[0-9A-Za-z*/,\- ]+", cron) and len(cron.split()) == 5):
        sys.exit("REFUSED: regression_cron is not five cron fields or off. Fix: edit .loop/config.json.")
    path = os.path.join(root, ".github", "workflows", "regression.yml")
    if os.path.exists(path):
        with open(path) as handle:
            if not handle.read().startswith("# Written by workflow-regression"):
                sys.exit("REFUSED: %s exists, and this tool didn't write it. Fix: merge by hand." % path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(render(cron, levels))
    print("WROTE " + path)
    return 0
