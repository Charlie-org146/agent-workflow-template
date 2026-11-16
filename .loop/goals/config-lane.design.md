# Design: config-lane

## Problem
In `lanes.plan` a changed path is checked with `touches(root, command, path, cache)`: a row is stale when `path` is in its
reach. Nearly every row reaches `.loop/config.json` (the scripts read it), so any edit to it, even removing one duplicate
`min_free_memory_gb` key (guard-fixes, #4320), marks 891 of 906 rows affected and the pr lane becomes the full suite (#4321).

## Approaches
1. **Key-aware branch in `plan` (chosen).** For `path == ".loop/config.json"`, compare the file at the row's recorded
   commit with the working copy as a multiset of `(key path, value)` pairs, read with `object_pairs_hook` so a duplicate key
   counts (json.load would hide the one thing guard-fixes did). The changed key names are the last component of every
   pair in the symmetric difference. A row is then stale only when `names_any(root, command, keys, cache)` is true: its
   command, or a file it reaches, names a changed key (that helper and `narrow.names` already exist, for deleted files).
   Cost: about 25 lines in `lanes.py`'s caller or `narrow.py`, no new file. Risk: a script that reads keys by a computed
   name (`cfg[name]`) is not seen, so the check fails wide: a key whose name appears in no file the row reaches still
   reruns every row that reads config as a whole (a bare `json.load(...)` iterated or passed on), see below.
2. **Declare keys per row (a `# reads: .loop/config.json:key` header).** Exact, but 906 rows to annotate and authors
   forget. Rejected: cost and drift.

## Chosen, and fail-wide rule
Approach 1. If either side fails to parse, or the diff is empty but the file's bytes changed (comments, whitespace) the
row is stale only when it names no key at all? No: an unparseable file is stale for every row that reaches it (today's
behaviour); a parse-equal reformat touches no row. A key counts as read when its name appears quoted in the row's command
or a reached file (`narrow.names` on the key name). A reached script that loads the whole config and passes it on is
caught because the loader scripts name the keys they use; one that iterates all keys is a known blind spot (open question).

## Each done line
1. The `min_free_memory_gb` toy: copy `.loop/config.json` with a duplicate key at a recorded commit, remove one, plan
   the rows: only rows naming `min_free_memory_gb` are stale, the rest reused. Proven red by breaking the branch (revert
   to `touches`), then 891-style: every row stale.
2. Toy cases: added key, removed key, changed value, a script reading the key, a script not reading it, an unparseable
   config (all rows stale), a reformat-only change (none stale); each seen red.
3. Size: `lanes.py` (20,732) and `narrow.py` (20,131) are over 19,000 on main today; scripts-c is trimming them. Build
   after scripts-c's release is on origin/main, put the code in the trimmed `narrow.py`, no new file (package at 98).

## Open questions
- A row that iterates all config keys without naming them (none found yet): the toy for it asks `grep` for `.items()` over
  a loaded config; if any exists, `names_any` is not enough and those scripts get a `# reads:` declaration.
