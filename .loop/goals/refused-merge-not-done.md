# A merge.py that is refused or fails leaves the goal failed (never done) while its PR is open, so goal.py resume works and the board shows it not finished; merge.py can be run again from a failed goal with a release error

- Slug: refused-merge-not-done
- Touches: .loop/regression.tsv

## Done lines

Frozen. A wrong done line needs a new goal.

1. A toy runs a refused merge.py and shows the goal's status is not done
2. goal.py resume brings the refused goal back to a live state at pr
3. merge.py run again after the fix merges a goal left failed by a refusal and leaves it done

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
