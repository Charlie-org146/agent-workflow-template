#!/usr/bin/env python3
# windows: ok
# reads: dev/package.py
"""The static scan of the shipped skills files: frontmatter and inventory, the scripts' imports and the safety scan (secrets,
obfuscated or encoded text, instructions aimed at the agent, dangerous commands and private name prefixes). It runs on every pull
request and in the merge group, so a Markdown-only change to a skills file is scanned too.

This is only an entry point: the rules live in dev/package.py, which stays as the fixture builder for the update, adopt and sync
toys and as the home of these rules until the follow-up update-package-path moves them. No package is built; `--static` is the
only mode. usage: skills-scan.py [--root DIR]  (prints "PASS: N files, the static rules hold", or each rule that failed)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import package  # noqa: E402

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--static"] + sys.argv[1:]
    sys.exit(package.main())
