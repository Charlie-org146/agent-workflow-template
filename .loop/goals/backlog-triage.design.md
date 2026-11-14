# Design: backlog-triage
Problem: 195 "Regression:" and 109 "health:" issues sit open before the v1.0.0 go/no-go; most cover rows that now pass, rows that were retired, or findings health no longer reports.
Approaches: (1) close by hand, issue by issue; (2) run each distinct row once and re-read health.py check, close on that evidence with a one-line comment, and write one report. Chosen: 2, it is repeatable and leaves a record.
Done line: docs/triage-2026-11-14.md with counts per verdict and feature, the issues closed and why, and a ranked goal list; nothing deleted.
Open questions: none. Rows that fail only off this machine would be labeled; none failed.
