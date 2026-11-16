# Design: page-reviews-o79

## Problem
The owner approved two page reviews in words ("finish these two", records o79, o80, o81): the Health page is still Unreviewed, and GRD-14 needs the pre-flight sub-bullet before it is reviewed again.

## Approaches
1. Apply the records as given: `criteria.py review Health --user --owner-record o79`; `unreview GRD-14` with o80; add the one sub-bullet; `review GRD-14` with o81. Cost: three commands and one line. Risk: none beyond the lock.
2. Edit the review stamps by hand. Rejected: stamps are the owner's, and the tool refuses it.

## Chosen
Approach 1. The sub-bullet is added as the last sub-bullet under GRD-14 with the wording from the goal, in the two-space indent its siblings use; no other wording changes.

## What each done line needs
1. Health.md's Review line reads Reviewed 2026-11-16 (set by the tool with o79) and `docs.py check` is clean.
2. GRD-14 is unreviewed with o80, holds exactly the quoted sub-bullet, and is reviewed again with o81; the diff shows only that line and the two stamps.

## Open questions
None.
