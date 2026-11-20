# Design: trim-monitoring-19k

Problem: sessions.py (20,000), operate.py (19,974) and reply_hook.py (19,866) exceed the 19,000 LF-byte rule, so later goals cannot change them.

Approaches:
1. Text-only trims (docstrings, comments, obvious function docstrings, one duplicated expression folded into a local lambda). Cost: small; risk: help text shrinks, behaviour unchanged.
2. Split code into a new module. Rejected: adds a shipped file, over the 100-file cap.

Chosen: 1. Output strings, hook TEMPLATE text, refusal messages and requirement IDs (MON-n, GRD-n) stay as they are.

Done lines: each script is at or under 19,000 bytes (now 18,918 / 18,996 / 18,670); the operate, reply-hook and session toys give the same PASS/FAIL set before and after, and a one-line change to a hook message fails test-reply-deps.py; no file or regression row added.

Open questions: none.
