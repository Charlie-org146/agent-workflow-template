# operate.py forward and apply exit nonzero on failure (issue #5287; TOP-DECISION 155/156; PC record o242); lands before known-red-size.

- Slug: operate-exit-codes
- Touches: not declared
- ETA: 260 active minutes (estimate 208m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. operate.py forward and apply exit nonzero on every failure path, each proven by a negative control seen red
2. No row that passes on main turns red, and operate.py stays under the 20,480-byte cap

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
