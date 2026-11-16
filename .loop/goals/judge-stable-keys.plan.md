# judge-stable-keys plan

Checked against the code: `file.saves`, `file.plan`, `judge.as_rows`, `judge.ASK`, `issues.key_of`/`evidence_of`/`legacy`, `report.py` calling `as_rows` all exist as read.

## Build steps
1. issues.py: `about(where)` and `first_cite(evidence)`.
2. judge.py: `as_rows` keys a review subject by feature and first citation and sets `about`; `twin(item, issues)` finds an older-key issue by rule and subject; the SAVES prompt asks for the file or row first.
3. file.py: `saves_rows(found)` keys by `about`; `plan` takes the twin when no issue holds the key; an owner-closed twin stays closed.
4. Toy `dev/toy/test-judge-stable-keys.py` (12 checks) and rows judge-key-savings, judge-key-review, judge-key-old, each seen red; done lines covered.
5. Health and Tests tables re-rendered; commands reference and DECISIONS.

## Tests per done line
1. savings and review rounds update #7 and #9, with controls for another file and another first citation.
2. an old-key issue (#4326-shaped and a review one) is matched and updated, not closed; owner-closed stays; another subject files.

## What could break
Existing keys: an issue under the new key is found directly; one under an old key is found through its body. Scripts stay under 20 KB (file 19.2k, judge 19.4k, issues 19.3k).

## Out of scope
Closing or rewriting any existing issue, a similarity match, a new judge answer format.
