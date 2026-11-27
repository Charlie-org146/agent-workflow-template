#!/usr/bin/env python3
"""What the owner is shown about goals under DLF-1.3, and the functions moved here to make room. Imported by the
monitoring scripts; it has no command of its own. Standard library only."""
import datetime
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_status as bs  # noqa: E402


def eta_new(root, slug, done, touches, budget, cfg=None):
    """{minutes, estimate, basis}: the model's high end plus the margin (30 minutes at least), else the time budget."""
    import auto  # here, not above: auto.py calls into this script
    names = glob.glob(os.path.join(auto.loop_dir(root), "runs", "*.json"))
    runs = [r for r in map(bs.read_json, names) if isinstance(r, dict) and r.get("slug")]
    try:
        found = bs.estimate_full({"slug": slug, "status": "queued", "done": done, "touches": touches}, runs,
                                 datetime.datetime.now(datetime.timezone.utc), root)
    except Exception:
        found = None
    if not found or not found[2]:
        return {"minutes": budget or 240, "estimate": 0, "basis": "no estimate yet, so the time budget"}
    high, margin = int(found[2] // 60), auto.eta_margin(cfg)
    return {"minutes": max(auto.ETA_FLOOR, -(-int(high * margin) // 5) * 5), "estimate": high,
            "basis": "estimate %dm plus a %d%% margin%s" % (high, round((margin - 1) * 100), ", rough" if found[3] else "")}
