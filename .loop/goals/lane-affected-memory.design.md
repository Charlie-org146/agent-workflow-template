# Design: lane-affected-memory

## Problem

`lanes_cli.py affected` builds one `cache` dict for the whole run, and `lanes.read()` (lanes.py:203) stores the text of every file it opens in `cache["text"]`, up to 400,000 characters each. On a large repo like thermis, the closures reach thousands of files, so the process holds every file's text until it exits: 430 to 820 MB per process (#4151), of which the text cache is 135 of 182 MB in the measured run. The text is only needed briefly. Everything later steps reuse is already memoized as small derived results (`scan`, `header`, `narrow.scan`, closures).

## Who reads the text

- `lanes.scan`, `narrow.header` and `narrow.scan` each read a file once and cache what they derive (the paths it names, its header, its imports).
- `lanes.closure` (lanes.py:275) reads each shell file in a closure again to test `ROOT_RUN` and a bare `cd`.
- `narrow.narrow` keeps the shell texts of one call in a local `shell` list and re-reads them for the sourced-binding pass (narrow.py:253) and the problem lines (narrow.py:275).
- `lanes.names_any` (lanes.py:336) reads every file in a row's closure, for every row and every deleted or unmapped path. That is the costliest reread.
- `tiers.unsafe` (tiers.py:122) uses the keys of `cache["text"]` as the list of files the plan read, to refuse saving a plan that read an ignored file or a file outside the repo through a symlink. That list has to survive the change.
- `narrow.suggest` reads the table into a throwaway cache and isn't affected.

## Approaches

**A. Cap the text cache: an LRU bounded by size (about 32 MB), plus a set of the names read.**
Cost: small, about 20 lines in `read()`. Risk: `names_any` walks every closure file once per row, so on thermis it would evict files and read them back from disk over and over. Memory is bounded, but time can grow and isn't bounded. The cap is also a tuning number that a bigger repo can outgrow.

**B. Keep no text for the whole run. Keep a set of the names read, plus the small facts each reread needs.**
`read()` returns the text and records only the name, in `cache["read"]`. A caller that used to reread a file memoizes the fact it needs, per file:
- `closure`: `("shellfacts", rel)` → (`ROOT_RUN` hit, bare `cd` present).
- `names_any`: `("names", rel, path)` → bool. The test is the same: path, basename or import stem in the text.
- `narrow.narrow`: its local `shell` list stays, because it lives for one call and holds only shell files. Its two rereads go through `read()` and come back from disk.

Cost: about 30 to 40 lines across lanes.py, narrow.py and tiers.py. Risk: missing a caller that relies on the text being cached. That would only make it slower, never wrong, because `read()` is a pure function of the file. Memory then scales with the derived facts, not with file sizes.

## Chosen: B

B bounds memory by design, not by a tuned number, and it avoids A's thrashing in `names_any`. The output can't change, because every memoized fact comes from the same text by the same regex. Before writing any code, the build measures peak memory and the share of each `cache` key (with `tracemalloc` and a per-key size) on thermis and on the toy, and confirms the text cache is the biggest one. If it isn't, the build keeps B and adds the next-largest key to the plan.

`tiers.unsafe` switches from `cache.get("text", ())` to `cache.get("read", ())`. `read()` stays the only place that opens files, and it still applies the 400,000-character cap and `errors="replace"`, so each file's text is exactly what it was before.

lanes.py is at 393 lines. If the script size check would fail, the per-file memo helpers move into narrow.py or a new small `lanefacts.py` rather than growing lanes.py.

## What each done line needs

1. **Under about 200 MB on thermis, found by measuring first.** A measurement before the change gives peak RSS and the per-key breakdown, which should show text at about 135 of 182 MB. After the change, `affected` over thermis's usual change set runs under about 200 MB peak RSS. Peak RSS comes from `resource.getrusage` on POSIX, or the peak working set (`GetProcessMemoryInfo` through ctypes) on Windows. The before and after numbers go into the pull request. thermis is on this PC (all repos live here since 2026-11-13), so this is measured locally, not left as an off-machine to-do.
2. **Toy memory bound plus the same answer.** A new `dev/toy/test-lane-affected-memory.sh` (or `.py`) builds a git repo of many large files: for example 400 files of 300 KB that one row's closure reaches, plus a deleted path so `names_any` runs. It runs `affected` before the change (the old `lanes.py` taken from the merge-base into a temp folder) and after it. It checks that the output is identical byte for byte and that the new peak is under the bound, while the old peak, for the red proof, is over it. Rows go into `.loop/regression.tsv` with `regression.py add`, and `regression.py red` proves they can fail.
3. **Optional memory wait: left out, and said so.** budget-enforce's REG-7 sub-bullet ("A lane about to run rows waits while free memory is below `min_free_memory_gb` …") is on `loop/budget-enforce` only, not merged into this branch's base. It also covers a lane about to run rows, not the `affected` call. So the condition "only if REG-7's new sub-bullet already covers it" fails: no wait is added, and the pull request says why.

## Open questions

- What exact path set the thermis measurement uses. Recommended: the change set of thermis's most recent goal lane, from its record or `git diff --name-only` of its last merge, so the number reflects a real lane.
- Whether the bound for the toy's peak RSS should be 200 MB or a figure scaled to the toy. Recommended: a toy bound of 100 MB, picked so the old code fails it clearly (its text cache alone is about 120 MB) and the new code passes it with room to spare.
