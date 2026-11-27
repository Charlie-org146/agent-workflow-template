#!/usr/bin/env python3
"""The board's cards (BOARD-1, 2, 3): one card per release, task and goal, and the three views over them.

Pure data in, text out: no model call, no network, no write. `cards(...)` builds them, `group_by(...)` groups them.
"""


def setting(cfg, key, default):
    raise NotImplementedError


def cards(items, runs, task_rows, batches, at, root=None, max_age=120):
    raise NotImplementedError


def group_by(found, view):
    raise NotImplementedError
