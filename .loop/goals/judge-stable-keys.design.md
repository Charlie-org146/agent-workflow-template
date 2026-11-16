# judge-stable-keys design

## Problem
Each health round re-filed the judge's advice under a new key (#4543: 29 issues from 4 rounds, 20 closed as duplicates). A savings finding's rule was `saves-` plus a hash of its fix wording (#4326, #4327 and #4328 are one advice reworded); a review finding's subject was a hash of every citation, so a round citing a slightly different set filed again.

## Approaches
1. **Key by rule and subject** (chosen). `issues.about(where)` is the first file or test row a savings finding names (else its first six words); its rule is `saves-` and the hash of that. A review finding's subject is its feature and a hash of its first citation. The judge prompt asks for the file or row first, spelled the same each round. An open issue under an old key is found by `judge.twin` from the subject in its body, updated under the new key and not closed as gone; an owner-closed one stays closed. Cost: about 60 lines across issues.py, judge.py and file.py. Risk: a judge that names another file for the same advice files again; two findings on one subject in a round share an issue.
2. Ask the judge for a subject field. Changes the answer format and every saved answer.
3. Compare wording by similarity. Fuzzy and untestable.

## What each done line needs
1. Two rounds with reworded advice on one file update one issue; another file files a second; review findings behave the same on the first citation (rows judge-key-savings, judge-key-review).
2. An open issue under an old wording-hash or citation-set key is matched and updated, not re-filed or closed; owner-closed stays closed; another subject files (row judge-key-old).

## Open questions
None for the owner. Existing issues are not touched; they move to the new key the next time their subject is found.
