# Design: lanes-closure-slashes

## Problem
On Windows, lanes.closure can return deps with backslashes (.loop\config.json) while touches() compares a path against them with forward slashes, so a goal touching .loop/config.json misses the rows that read it. narrow.config_hit already normalises its own copy (#4457).

## Approaches
1. Normalise at each caller (touches, config_hit, others). Cost: every reader repeats the fix; risk: the next reader forgets.
2. Normalise once where the deps leave closure, and make touches() read its path the same way. Cost: about 10 lines in lanes.py; risk: a cached tuple now holds a new set, which no caller mutates.

## Chosen
Approach 2: closure() wraps the old body (now raw_closure) and returns every dep with forward slashes; touches() replaces backslashes in its path. config_hit's own normalisation stays and is harmless.

## Done line needs
- Line 1: a toy feeds both slash forms to closure and touches and gets the same result.
- Line 2: the same toy on a POSIX list reads as before; rows lane-closure-slashes and lane-closure-posix-same are seen red.

## Open questions
None for the owner. lanes.py grows to about 19.7 KB, under the 20,480 limit.
