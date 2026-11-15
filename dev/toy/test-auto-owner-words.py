#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-monitoring/scripts/auto.py skills/workflow-setup/scripts/settings.py .loop/config.json
"""MON-11 (#4287, #4048): full auto never answers a question that asks for the owner's words; the config holds each key once.

Calls auto.why_not and the settings table directly. No model, no network."""
import json
import os
import sys

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for skill in ("monitoring", "setup"):
    sys.path.insert(0, os.path.join(root, "skills", "workflow-" + skill, "scripts"))
os.environ.pop("LOOP_ROLE", None)
import auto  # noqa: E402
import settings  # noqa: E402

bad = []


def check(ok, text):
    print(("PASS: " if ok else "FAIL: ") + text)
    if not ok:
        bad.append(text)


def verdict(ask, kind="routine"):
    return auto.why_not({"kind": kind, "recommend": "yes", "words": ["yes", "no"], "ask": ask}, {})


for ask in ("Add the DOC-17 sub-bullet to Delivery as drafted?",
            "Raise criteria_max from 26 to 28?",
            "Un-review the Setup page so its wording can change?",
            "Is a reviewed requirement changed here without owner words?"):
    check(verdict(ask) == "it asks for owner words", "a routine question that asks for owner words waits: " + ask[:40])
check(verdict("Which name should the toy use?") == "", "a plain routine question is still answered")
check(verdict("Use the step-2 wording for the log line?") == "", "a lower-case word before a number is not a requirement id")


def once(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate key: " + ", ".join(sorted({k for k in keys if keys.count(k) > 1})))
    return dict(pairs)


with open(os.path.join(root, ".loop", "config.json")) as handle:
    live = json.load(handle, object_pairs_hook=once)
check(live.get("min_free_memory_gb") == 3.5, "this repo's config holds min_free_memory_gb once, at 3.5")
check("min_free_memory_gb" in {row[0] for row in settings.TABLE}, "the settings table registers min_free_memory_gb")
sys.exit(1 if bad else 0)
