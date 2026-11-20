# The records tools catch up with DOC-2 as revised under o664 (#5562): sessions.py owner-words and criteria.py accept a new record kind 'delegated' that cites the operation-top decision number, the owner's asking words verbatim and DOC-2's revision. A delegated record is accepted for revise and review ONLY when the change is not a safety class; every safety-class check stays exactly as it is, and each delegated record is listed in the next check-in (TD465)

- Slug: delegation-records
- Touches: skills, dev/toy
- ETA: 465 active minutes (estimate 370m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a delegated record for a wording change that is not a safety class, then criteria.py revise and review accept it, and a toy proves it
2. Given a delegated record for a safety-class change, then it is refused exactly as before, shown by the same toy, and no existing safety-class check changes
3. Given this goal's diff, then every script stays under 20,480 bytes, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
1. Run `python3 dev/toy/test-delegated-records.py`.
   Expect: 10 PASS: a delegated record is written (TD number, DOC-2 revision, asking words), revise and review accept it for a wording change, both refuse a safety-class change (even with --user), a plain record with no --user is refused as before, and the check-in lists the record.
2. Run `sessions.py owner-words "<the owner's asking words>" --ids SLUG,ID --from top --delegated TD465 --doc2 r6` in a scratch repo.
   Expect: `OWNER-WORDS oN covers SLUG,ID`; with words naming a safety class, REFUSED.
