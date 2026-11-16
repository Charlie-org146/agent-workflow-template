# Design: queue-hygiene

Problem: (#4343) a merged goal can keep its pr-queue ticket and beat, so the next goal waits behind it (budget-fair held scripts-b 25 minutes); and dev/toy/test-merge-main-own.py's last case fails on main.

Approach A: only make pool.pr_order treat a merged goal as free. Approach B (chosen): also have merge.py remove the ticket and beat right after the PR merges, so the release step's wait never holds the queue, and let pr_order drop a goal whose run says release merged/cut and remove the beat with the ticket (it left the beat behind).
Toy case 2: since #4208 wiki.pending audits the goal's head tree, which only prints main's stale page as a FINDING when the head holds main's commit (goal.py pr merges main first); the toy's goal branch never merged main, so the toy is fixed by merging origin/main into it, which is what the real flow does.
Done lines: both covered, each with a row seen red. pool.py and merge.py were over 19,000 bytes, so the change is net-negative in bytes there (docstrings shortened). No new file. Out of scope: the queue's other rules.
