#!/usr/bin/env python3
# windows: ok
# reads: listing.json dev/package.py
"""Every add_parser command in the shipped scripts is named in listing.json's commands (the package Disclosure rule),
checked here without building the package so every platform runs it; dropping one name must fail."""
import contextlib
import io
import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(here, "..", ".."))
sys.path.insert(0, os.path.join(root, "dev"))
import package  # noqa: E402

listing = json.load(open(os.path.join(root, "listing.json"), encoding="utf-8"))
files = [f for f in package.walk(root) if f.endswith(".py") or f.endswith("SKILL.md")]


def disclosed(data):
    package.failures.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        package.check_disclosure(root, files, data)
    return [t for r, t in package.failures if "listing.commands" in t]


missing = disclosed(listing)
print(("PASS: " if not missing else "FAIL: ") + "every command is in listing.commands" + ("" if not missing else " " + str(missing)))
cut = dict(listing, commands=[c for c in listing["commands"] if c != "apply"])
dropped = disclosed(cut)
print(("PASS: " if dropped else "FAIL: ") + "a command left out of listing.commands is caught")
sys.exit(0 if not missing and dropped else 1)
