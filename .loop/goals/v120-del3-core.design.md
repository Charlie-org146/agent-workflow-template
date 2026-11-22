# Design: v120-del3-core (DEL-3.1 to DEL-3.5, revised DEL-3)

## Problem

Today the operation layer asks the owner about many choices that are not on any fixed list. Full auto (MON-11, `auto.py`) answers only
when a standing record exists and refuses by a built-in set of safety regexes (`auto.CLASSES`) plus kind, ETA and always-ask rules; the
owner's typed words are a per-machine file (`<git common dir>/loop/owner-words.tsv`), so an answer typed in one operation session is
retyped or relayed through top in another; "relayed from top" records count as the owner's words except for safety classes
(`layers.relay`); decisions made for the owner are lines in `auto.log` and a check-in section, with a revert command per line but no board
list. The source text is `.loop/goals/v120-del3-text.source.md` (verbatim from the owner's v1.2.0 page, goal A's reviewed text); this goal
builds DEL-3.1 to DEL-3.5. DEL-3.6 to DEL-3.10 are goal C (v120-del3-rules).

## Facts read

- `auto.py` is 20,377 bytes; it holds `CLASSES` (five regexes: destructive, money, security, private data, steward merge, about 1.4 KB),
  `why_not` (kind, ETA, always-ask, no recommendation, classes, risky_paths), the decision pass, the `auto.log` line format and the owner-words
  helpers (`add_owner_words`, `owner_rows`). `layers.relay(source, text)` (20,439) accepts `--from top` except safety classes and refuses `peer`.
  `sessions.py owner-words` (18,977) is the one writer; a worker never writes. `checkin.py:138-150` prints the decided lines with a revert command.
- Near-cap files (never newly over 19,000, none over 20,480, no trimming of comments or docstrings: GRD-20): auto 20,377, layers 20,439,
  operate 20,466, sessions 18,977, checkin 18,996, board_lines 18,955. The package holds 100 of 100 files (`dev/package.py` MAX_FILES), so a
  new script under `skills/` needs grd21-cap-lift-2 (MAX_FILES 200, branch `loop/grd21-cap-lift-2`, not on main).
- Owner-words ids are per machine (`o308` here is `o765` on the Mac); machines already share small JSON blobs as git refs on origin
  (`refs/loop/handover/<slug>`, `refs/loop/snapshot/<machine>`, machines.py).
- `sections.confidence()` counts regression rows keyed by a requirement id; rows keyed `DEL-3.n` never count (bug #5790); goal A's plan says
  this goal adds ONE known row keyed DEL-3 with an open issue so DEL-3's score is honest until DEL-3.1 to DEL-3.10 are enforced.

## Approach (chosen): one new script, the rest forwarders and moves

A. `skills/workflow-monitoring/scripts/decide.py` (new, under 19,000 bytes) holds the five classes, the list file reader and seal check, the
   decision record, the undo, the tool-bug filer and the owner-words sync. `auto.py` gives up `CLASSES` to it (the owner-words readers stay in auto.py; net
   smaller), `layers.relay`, `sessions.owner-words`, `checkin.py` and the board call it through short forwarders. Cost: one new file (needs
   the cap lift), about 10 small edits, 5 toys, 6 rows.
B. Squeeze it all into the existing files: rejected, they have 0 to 130 bytes free and GRD-20 forbids trimming to fit.

## Chosen: A, stacked on goal A's head, merged after grd21-cap-lift-2.
