# Design: ci-fail-output

Problem: the full CI regression run lists failing rows by name only, because most rows hide output behind `| grep -q`, so 100 failures have no cause (#4516).

Approaches: (1) write each failing row's last 20 lines to the shard job's own step summary; (2) upload row logs as artifacts. Chosen: 1 (small, in the summary the owner reads). It reuses `shown()`, which reruns a quiet row loudly, and the same text now also fills the issue body.

Done lines: line 1 is the shard's summary write; line 2 is a toy that runs the committed workflow block over one failing and one passing row.
