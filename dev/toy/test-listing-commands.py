#!/usr/bin/env python3
# windows: ok
# reads: listing.json dev/package.py
"""Every add_parser command in the shipped scripts is named in listing.json's commands (the package Disclosure rule),
checked here without building the package so every platform runs it; dropping one name must fail. The same rule for hosts: every
host the shipped README links is in listing.network (the README-links entry holds the reference links, never fetched by any
script), and a README host that is not listed fails."""
import contextlib
import io
import json
import os
import sys
import tempfile

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
FIVE = ["eslint.org", "rework.withgoogle.com", "www.agensi.io", "www.atlassian.com", "www.gitguardian.com"]


def hosts(data, tree=root, names=("README.md",)):
    package.failures.clear()
    with contextlib.redirect_stdout(io.StringIO()):
        package.check_disclosure(tree, list(names), data)
    return [t.split()[1] for r, t in package.failures if t.startswith("host ")]


bare = dict(listing, network=[n for n in listing["network"] if not n.startswith("README.md links only")])
unlisted = hosts(listing)
print(("PASS: " if not unlisted else "FAIL: ") + "every host the README links is in listing.network" + ("" if not unlisted else " " + str(unlisted)))
five = sorted(set(FIVE) & set(hosts(bare)))
print(("PASS: " if five == FIVE else "FAIL: ") + "negative control: without the README-links entry the five reference hosts fail (%s)" % ", ".join(five))
with tempfile.TemporaryDirectory() as tree:
    with open(os.path.join(tree, "README.md"), "w", encoding="utf-8") as handle:
        handle.write("# T\nSee [a](https://not-listed.example.org/x) and [b](https://eslint.org/docs/rules/max-lines).\n")
    odd = hosts(listing, tree)
print(("PASS: " if odd == ["not-listed.example.org"] else "FAIL: ") + "negative control: a README host that is not listed still fails, a listed one passes (%s)" % odd)
sys.exit(0 if not missing and dropped and not unlisted and five == FIVE and odd == ["not-listed.example.org"] else 1)
