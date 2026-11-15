# Design: guard-fixes

Problem: (#4287) `auto.py` `why_not()` has no rule for a PENDING line that asks for the owner's words, so under full_auto a question such as "add the DOC-17 sub-bullet" was AUTO-APPROVED; only the owner can answer it. (#4048) `min_free_memory_gb` is already in the settings registry (settings.py:62, shipped default 4) but this repo's `.loop/config.json` carries the key twice (lines 48 and 78, both 3.5).

Approach A for #4287: add an `OWNER_WORDS` regex in auto.py and a `why_not` rule that returns "it asks for owner words" (waits, logged once). Cost: one regex and three lines; auto.py is 11.9 KB. Risk: a pattern too wide would hold routine questions.
Approach B: require workers to label such questions kind `owner`. Rejected: the failure is a worker that did not, and auto.py must not trust the label alone.
Chosen: A. The pattern covers owner words / owner-words record, criteria_max, un-review/re-review, a reviewed page or requirement, and a requirement id with "sub-bullet". It is checked on the ask and the recommended answer, before the owner-answered rule, after the kind rule.

Done line 1: the rule, a new toy `dev/toy/test-auto-owner-words.py` (routine kind, recommended answer, still waits; a plain routine question still answers), a regression row proven red by removing the rule in a HEAD copy.
Done line 2: delete the second duplicate key from config.json (keep one, 3.5); the registry already lists it; add a check to the same toy that the config has the key once. The registry's shipped default stays 4 (test-budget-enforce pins it).
Out of scope: reply_hook.py size (scripts-a, PR #4279), requirement text (none changes), the shipped default.
Open questions: none.
