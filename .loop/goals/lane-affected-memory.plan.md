# lane-affected-memory plan

Checked against the code on origin/main and two measurements on thermis (12 changed paths, 374 s; one path, 182 MB peak).
The design's text-cache cause holds, and the profile adds a second, larger one: time. This plan covers both.

## Measured causes (thermis, profile of `lanes_cli.py affected`)
- `lanes.names_any` (lanes.py:336): 240 of 374 s. It rescans the text of every file in a row's closure for each deleted or
  unmapped path, for each of 224 rows, though rows share most files (10.4 million string checks).
- `lanes.references` (lanes.py:177): about 87 s, 636,000 `isdir`/`isfile` calls on the same few paths, once per file.
- `lanes.read` (lanes.py:203): keeps every file's text for the run: 135 of 182 MB.

## Build steps
1. New `skills/workflow-regression/scripts/textcache.py` (lanes.py is at its size cap, so no new code goes there):
   - `Texts`: a dict of file name to text, holding at most 32 million characters; the oldest text is dropped, the name stays
     (`tiers.unsafe` lists the files read from `cache["text"]`).
   - `names(text, path)`: the exact test names_any used (path, basename, or `import stem`).
   - `kind(memo, full)`: `isdir`/`isfile` answered once per path per run.
2. `lanes.read` calls `Texts.load` (shorter than today). `lanes.names_any` memoizes each (file, path) answer in the cache,
   so a file is checked once per path whatever the number of rows. `lanes.references` takes an optional `memo` for `kind`;
   `scan` passes the run's memo.
3. Toy `dev/toy/test-lane-affected-memory.sh` plus rows in `.loop/regression.tsv` (`regression.py add`, then `red`): builds a git
   repo with about 400 files of 300 KB that a row reaches and a deleted path; checks the output is identical to the old
   lanes code (taken from the merge-base) and the new peak is under 100 MB and the new time is lower.
4. Docs: the changed scripts' wiki page. Done line 3 (memory wait) is left out; the pull request says why.

## Test for each done line
1. Peak under about 200 MB on thermis, and time: measured before and after (numbers go in the pull request).
2. The toy and its row.
3. Not built (REG-7's sub-bullet is not on this base).

## What could break
- Output must not change: the memo stores the same test per (file, path). The toy compares byte for byte.
- Files changing mid-run: the memos live in one run's cache only, as the text cache did.
- A dropped text is read again from disk: only slower, never different.
