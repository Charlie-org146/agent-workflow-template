# Health judge findings get stable keys, so a later round updates its open finding instead of re-filing it (#4543)

- Slug: judge-stable-keys
- Touches: not declared
- ETA: 200 active minutes (estimate 160m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A judge finding's key comes from its rule and its subject (feature, page or file), not a hash of its wording, so a later round with reworded advice on the same subject comments on or updates the open issue instead of filing a new one; a toy runs two rounds with reworded advice on one subject and sees one issue, and a finding on a different subject still files a new one (negative control).
2. An open judge issue filed under an old wording-hash key is matched by rule and subject on the next round and is not re-filed; a toy fixture with one old-key issue shows the match.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
