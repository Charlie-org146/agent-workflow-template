#!/usr/bin/env python3
"""One set of level words, L0, L1 and L2 (goal v110-lvl-retire-old-words-2): what the goal_levels setting means, on a levelled table and
on one that is not. An old word is read, never silently: a levelled table prints one line; another value is refused there."""
import sys

OLD = {"land": "L1", "nightly": "L2"}  # the old words, translated on a levelled table: the level that selects at least the same rows (TD2334)
LEVELS = ("L0", "L1", "L2")
PLAIN = {"L0": "land", "L1": "nightly", "L2": "nightly"}  # a table that is not levelled runs the level as its old word


def goal_target(value, levelled):
    """The target a goal lane plans from for the goal_levels value `value` (None when unset): L0, L1 or L2 on a levelled table,
    land or nightly on one that is not. Prints the old-word line or the warning; a bad value on a levelled table is refused."""
    if value is None:
        return "land"  # not set: the setting's default, run as it always was
    if levelled:
        if value in OLD:
            print('SETTINGS (GOAL_LEVELS_OLD): goal_levels "%s" in .loop/config.json is read as %s. Fix: set "goal_levels": "%s" and commit it.' % (value, OLD[value], OLD[value]))
            return OLD[value]
        if value in LEVELS:
            return value
        print('REFUSED (GOAL_LEVELS_BAD): goal_levels is %s in .loop/config.json; the values are L0, L1 and L2. Fix: set one there and commit it. Nothing was run.' % repr(str(value))[:42], file=sys.stderr)
        sys.exit(2)
    if value in PLAIN:
        return PLAIN[value]
    if value not in ("land", "nightly"):
        print('SETTINGS (GOAL_LEVELS_BAD): goal_levels is %s in .loop/config.json and runs as land. Fix: set "land" or "nightly", or L0 or L1.' % repr(str(value))[:42])
        return "land"
    return value
