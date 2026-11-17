# howto-per-requirement design

Problem: a feature's How-to-use page doesn't show, requirement by requirement, how each is delivered; and (#4666) the DOC-16 routine shape is wrongly applied to every How-to-use Runbooks section.

Approaches:
1. docs check reads the feature page's functional requirement IDs and requires an item "- ID: how it is delivered" for each on its How-to-use page (and refuses an unknown ID); apply the routine shape only to routines the repo schedules on that page. Small, additive.
2. A new section per requirement in the skeleton. Changes the fixed skeleton the Mac already uses. Rejected.

Chosen: 1, with the items written under "How to reach or run it", generated from each requirement's title and the first test row naming it.

Each done line: 1 needs the check and its negative controls; 2 needs the items on all eight pages and a clean docs check; 3 needs DOC-19 on the Documentation page, Unreviewed, with test rows.

Open questions: the owner reviews DOC-19's wording (nothing is marked Reviewed here).
