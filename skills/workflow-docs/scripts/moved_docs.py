"""Helpers moved out of docs.py to keep it under 19,000 bytes."""
import json
import os
import sys


def config(root):
    try:
        with open(os.path.join(root, ".loop", "config.json")) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        sys.exit("REFUSED: no readable .loop/config.json. Fix: run workflow-setup and merge its branch.")
