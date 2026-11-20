# No release is made while main is known red (owner o672, TD507; REL-15, DEL-17): release.yml first asks GitHub for open issues labeled main-red (one API call); if any is open it ends green printing "held: main red (#N)" and publishes nothing, and the first push after the last one closes releases from that commit as usual. Whoever finds a red on main files it with the main-red label, and the red-on-main steps in machines.md and the check-in say so

- Slug: release-hold-red
- Touches: .github, skills, dev/toy
- ETA: 410 active minutes (estimate 328m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given an open issue labeled main-red, when release.yml runs on a push to main, then it ends green with "held: main red (#N)" and publishes nothing; given none open, it releases as before (toy with both cases, negative control)
2. Given the pull request, then its body says Fixes nothing and names TD507, a toy row proves both cases and is SEEN RED with the check removed, the main-red label step is in the red-on-main steps, and docs.py check and criteria.py render --check pass
3. Given this goal's diff, then no file is added to the package (100 files), no script newly crosses 19,000 bytes, every script stays under 20,480, and the private scan is clean

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
