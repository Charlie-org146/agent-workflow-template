# Plan: backlog-triage
1. Run every distinct Regression row once (regression.py run) and health.py check at origin/main.
2. Close issues whose row passes or no longer exists, and health findings no longer reported, each with a one-line comment.
3. Write docs/triage-2026-11-14.md. Test: docs.py check passes; each closed issue carries its comment (log kept).
Could break: a row that skips on Windows reads as passing; the nightly run on Linux remains the proof. Out of scope: fixing any remaining finding.
