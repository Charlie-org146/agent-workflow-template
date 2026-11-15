# Plan: queue-hygiene

Checked: pool.pr_order drops a ticket when age>limit, the run is not LIVE or not at checks/pr, but unlinks only the ticket (the .beat stays); merge.py main() writes the merged state and prints MERGED, then autorelease.finish; wiki.pending runs `docs.py check --own` in the head tree.
Build: 1. pool.pr_order also drops a run whose release is merged or cut, and unlinks ticket and beat. 2. merge.py leave_queue(path, slug) called right after MERGED. 3. Docstrings shortened so pool.py (-11 bytes) and merge.py (-7) end smaller. 4. test-pr-order.py: two cases (merged goal free with beat removed; merge.leave_queue removes both). 5. test-merge-main-own.py: merge origin/main into loop/g before the audit. 6. Rows queue-merged-free-4343, merge-leaves-queue-4343 (MON-15) and merge-main-own-finding-4343 (DEL-5), each seen red; render; docs check.
Could break: a goal still at pr whose run says release merged (never). Out of scope: other queue rules. No owner decisions.
