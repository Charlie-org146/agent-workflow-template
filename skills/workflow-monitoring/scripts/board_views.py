#!/usr/bin/env python3
"""The board's three views, written for each followed repo into its own folder (BOARD-1, 2, 3, 5, 7).

`publish(...)` builds one repo's cards, scans what it is about to write with the private-name scan, and writes `cards.json` and
`views.txt` under that repo's git common dir only when their content changed. A refusal skips the write and names the place
(never the word). No model call, no network.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_cards  # noqa: E402
import notify_gate  # noqa: E402

VIEWS = (("release", "By release"), ("task", "By task"), ("goal", "By goal"))


def views_text(found):
    """The three views as text: each group, then its cards with their state, stale mark, ETA owner, task and machine."""
    out = []
    for view, title in VIEWS:
        out.append(title)
        for group, members in sorted(board_cards.group_by(found, view).items()):
            out.append("  %s" % group)
            for c in members:
                out.append("    %s %s: %s%s, ETA of %s%s%s" % (c["kind"], c["name"], c["state"], " (stale)" * bool(c["stale"]), c["eta_of"],
                                                            ", task " + c["task"] if c["kind"] == "goal" else "", ", on " + c["machine"] if c["machine"] else ""))
        out.append("")
    return "\n".join(out)


def publish(name, path, base, rows, deps, at, setting_of, write):
    """Write one repo's cards and views into its own board folder; returns a refusal line or ''."""
    found = board_cards.card_list(rows, deps, at, [(name, path, base)], setting_of)
    cards = json.dumps(found, indent=2, sort_keys=True) + "\n"
    views = views_text([c for c in found if c.get("kind") != "error"])
    said = notify_gate.outgoing_refusal({"cards": cards, "views": views}, strict=False)
    if said:
        return "BOARD_REFUSED %s: the private-name scan refused %s; nothing was written" % (name, said)
    folder = os.path.join(base, "loop")
    os.makedirs(folder, exist_ok=True)
    write(os.path.join(folder, "cards.json"), cards)
    write(os.path.join(folder, "views.txt"), views)
    return ""
