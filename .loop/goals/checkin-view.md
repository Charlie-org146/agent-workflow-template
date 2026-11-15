# The check-in shows the machine, the release and feature grouping, and each goal's status, time and machine (MON-5, MON-14, MON-16; #4496)

- Slug: checkin-view
- Touches: not declared

## Done lines

Frozen. A wrong done line needs a new goal.

1. The Monitoring page's MON-5, MON-14 and MON-16 say, in reviewed text under owner record o44, that every check-in shows a Machine line (free RAM, free commit memory, CPU, claude and node counts), groups each repo's Dependencies map by release milestone and then by feature, and shows for each goal its status marker, expected time left and the machine that runs it.
2. checkin.py prints the Machine line first, groups each repo block by release milestone then feature milestone, and prints each goal with its status marker, time left and machine (pc or mac, from the goal's pod record); a repo owned by another pod is drawn from that pod's last report and marked with its machine.
3. The reply hook flags a check-in with no Machine line, or a Dependencies goal with no status marker, no time or no machine, and passes one that has them, with a negative control for each (closes #4496).

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
