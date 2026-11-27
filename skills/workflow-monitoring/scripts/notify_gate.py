#!/usr/bin/env python3
"""What notify.py checks before a mail goes out (BOARD-5, BOARD-8): the private-name scan and the check-in gate."""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DELIVERY = os.path.join(HERE, "..", "..", "workflow-delivery", "scripts")


def outgoing_refusal(units):
    """What the private-name scan refuses in the text about to go out: its places, never the word ("" when clean). {place: text}.
    No list, a broken list or a scan past its limit refuses too (it fails closed); a list that holds only comments passes."""
    sys.path.insert(1, DELIVERY)
    private = importlib.import_module("private")  # another skill's script: no static import, so the package scan sees none
    found = private.scan(".", "", texts=units)
    if found["state"] in ("none", "broken"):
        return "the private-name scan could not run: " + str(found.get("note", found["state"]))
    return "; ".join(found["hits"]) if found["state"] == "hit" else ""


def checkin_gate(state, lines, now, every):
    """send, same or early for a check-in carrying these CHANGE lines. Reads state, writes nothing: same = nothing changed since the
    last check-in sent; early = a change closer than `every` minutes to it; send otherwise (a first one included)."""
    last = state.get("checkin") or {}
    key = "|".join(sorted(lines))
    if last and last.get("lines") == key:
        return "same"
    if last and now - last.get("at", 0) < every * 60:
        return "early"
    return "send"


def checkin_sent(state, lines, now):
    state["checkin"] = {"lines": "|".join(sorted(lines)), "at": now}



def checkin_lines(text, needs):
    """What a check-in says, without its clock: its headline and its Needs you items."""
    first = next((x.strip() for x in str(text or "").splitlines() if x.strip()), "")
    return ([first] if first else []) + needs(text)


def checkin_event(state, text, needs, root, live):
    """[the check-in as one more event] when it is due, else []. The first check-in seen only becomes the baseline (nothing sent);
    live is False for a start review's own run."""
    import datetime
    import json
    import board_cards
    lines = checkin_lines(text, needs)
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    if not lines:
        return []
    if "checkin" not in state:
        checkin_sent(state, lines, now)
        return []
    try:
        with open(os.path.join(root, ".loop", "config.json"), encoding="utf-8") as handle:
            cfg = json.load(handle)
    except (OSError, ValueError):
        cfg = {}
    if live and checkin_gate(state, lines, now, board_cards.setting(cfg, "checkin_every", 10, 5, 10)) == "send":
        return [("checkin:%d" % now, "check-in", "", "check-in: " + "; ".join(lines)[:600])]
    return []


def mark(state, text, needs, sent, key):
    """A check-in mail went out: remember what it said and when (it is not a per-event key)."""
    import datetime
    checkin_sent(state, checkin_lines(text, needs), datetime.datetime.now(datetime.timezone.utc).timestamp())
    sent.pop(key, None)
