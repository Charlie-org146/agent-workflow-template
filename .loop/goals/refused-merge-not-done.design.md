# Design: refused-merge-not-done (#4004)

## Problem

`merge.py` refuses through `autorelease.fail()` (stale wiki pages, a private name, a missing requirement, a gh merge
error). `fail()` records `release_error` and a log line but keeps the run record at `status: done`. The board reads the
goal as finished while its pull request is open, and `goal.py resume` refuses it (RESUME_STATUS: only a failed or
stopped goal resumes); a worker cannot repair its own goal (WORKER_SELF_REPAIR).

## Approaches

1. `fail()` sets `status: failed` while the pull request is not merged. `merge.py` then also accepts a failed goal that
   holds a `release_error` and a pull request, so the Fix lines the refusals already print ("then run merge.py") keep
   working without a resume. A successful merge puts the status back to done. Cost: a helper in autorelease.py and a
   shorter condition in merge.py. Risk: the watcher mends a failed goal, which is the intended behaviour.
2. Change `resume` to accept a done goal with a `release_error`. Cost: guards.py grows. Risk: the board still shows the
   goal as finished, which is the bug.

## Chosen

Approach 1. It fixes the record where it is written, so the board, resume and the Fix lines all agree.

- A refusal before the merge (release is not `merged`) leaves `status: failed`, step unchanged. After the merge
  (release `merged`) a failure stays `done`, because the pull request is in.
- `merge.py` accepts `done`, or `failed` with a `release_error` and a pull request (`autorelease.mergeable`).
- A merge sets `release: merged` and `status: done` (`autorelease.mark_merged`).
- merge.py has 62 bytes free under the 20480 cap, so the logic lives in autorelease.py and merge.py gets shorter.

## Each done line

1. Toy: run merge.py on a goal whose pages are stale (refused); read the record: status is `failed`, `release_error`
   set.
2. Same toy: `goal.py resume` as the operation brings it back to a running goal that resumes at pr.
3. Same toy: with the fault fixed, merge.py merges the failed goal; status ends `done`.

## Open questions

None for the owner. DOC requirements are not touched; if a reviewed requirement needs wording it goes to DECISIONS.md.
