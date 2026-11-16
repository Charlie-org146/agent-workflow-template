# Health's script-size warning sits at the 19,000-byte cap instead of 90% of it (#4370, #4560)

- Slug: size-warn-at-cap
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. The health size rule warns only for a script over 19,000 bytes, so a script between 18,432 and 19,000 bytes raises no warning, and the regression size rows size-139 and size-141 pass on main; a toy checks scripts at 18,900 and 19,100 bytes, with a negative control.
2. The open size-warning health issues that the new line clears are closed with a comment naming this goal, and #4370 and #4560 are closed with the proof.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
