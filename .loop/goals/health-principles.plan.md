# Plan: health-principles
1. rules.py: principle_map(root) reads Principles.md Part 1 into {n: [ids]}; checks(root, rows) returns RED reasons.
2. judge.principles(): call it; RED when no Reviewed requirement, or no group rule that can fail; a Reviewed requirement under no principle FAILs Requirements by ID.
3. review: per-principle block (requirements, their tests, weak = Reviewed with no test).
4. Toys: controls on broken copies; one-word README difference fails health naming the line.
5. Rows: fold into existing rows, seen red, net 0 or fewer; sizes checked.
