# Plan: guard-fixes

Checked against the code: `skills/workflow-monitoring/scripts/auto.py` (11.9 KB) holds RISKY, `why_not(waiting, cfg, answered)` (kind rule, recommended-answer rule, risky words, risky paths, owner-answered rule); `skills/workflow-setup/scripts/settings.py:62` already registers min_free_memory_gb (shipped default 4, pinned by dev/toy/test-budget-enforce.py); `.loop/config.json` has the key at line 48 and line 78 (both 3.5); `dev/toy/test-monitoring-prd.sh` (24 KB) drives `auto.py pass` and stays untouched.

Build steps:
1. auto.py: add `OWNER_WORDS = re.compile(...)` matching: owner words, owner-words, criteria_max, un-review / unreview / re-review, "reviewed page", "reviewed requirement", and a requirement id (two to five capitals, dash, number) near "sub-bullet" or "wording". In `why_not`, after the kind and recommend rules and before the risky-word rule, return "it asks for owner words" when it matches the ask or the recommended answer. File stays well under 19,000 bytes.
2. config.json: delete the second min_free_memory_gb line (78); keep the one at 48.
3. New toy `dev/toy/test-auto-owner-words.py` (header `# windows: ok`, `# reads:` auto.py and config.json): calls auto.why_not for routine questions that ask for owner words (a DOC-17 sub-bullet, a criteria_max raise, an un-review of a page) and expects a "owner words" reason each; a plain routine question ("Which name?") still returns ""; config.json parsed with a duplicate-key hook holds min_free_memory_gb exactly once at 3.5; the settings table lists it.
4. Regression rows `auto-owner-words-wait` (GRD-... tie: the row ties to MON-11, the requirement that owns full auto) and `config-memory-key-once`, both `land`; commit, then `regression.py red` each with a break (delete the rule in the HEAD copy; re-add the second key) so both are seen failing.
5. Re-render (settings reference unchanged, criteria render, entry write, docs check). No reviewed requirement text changes; if MON-11 needs wording, stop and send the exact sub-bullet to operation.

Tests per done line: line 1 = toy case plus row `auto-owner-words-wait` seen red; line 2 = toy check plus row `config-memory-key-once` seen red.
Could break: a routine question that merely mentions "reviewed" must still answer (only "reviewed page/requirement" matches); test-monitoring-prd.sh cases keep passing (run it).
Out of scope: reply_hook.py size (scripts-a, PR #4279), the shipped default of min_free_memory_gb, any requirement text.
No owner decisions left.
