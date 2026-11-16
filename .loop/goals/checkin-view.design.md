# checkin-view design

Problem: the check-in loses the owner: no expected times next to each goal, no machine status, no release or feature grouping, and no sign of which machine runs a goal.

Approaches:
1. Print the facts in checkin.py (Machine line already exists; add release/feature groups and one `[m] slug ~time left machine` line per goal) and make the reply hook check them. Small, one script plus one hook function; risk: low.
2. Move the board's page layout into the check-in. Larger, and MON-4/MON-5 keep the board out of the check-in. Rejected.

Chosen: 1. The release comes from the goal's `## Batch:` heading in queue.md, the feature from the page defining the first requirement ID in the goal line, the machine from the goal's pod record (stamped when the pod creates it; this machine when absent). Another pod's goals stay the one line MON-17 specifies, now marked with its machine.

Each done line: 1 needs MON-5, MON-14 and MON-16 text under owner records o44 and o45; 2 needs checkin.py output; 3 needs the hook checks with negative controls.

Open questions: none for the owner. The wording "another pod's repo drawn from its last report" is kept to the one-line form of MON-17.
