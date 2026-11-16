# hard-eta: design

Problem: a goal's time budget (240 minutes by default) is raised by the operation session whenever it is hit, so v1-go-no-go slid from 13:00 to 18:17 (#4512, owner o52). Nothing records an ETA when a goal is frozen, nothing stops a goal at it, and nothing makes the owner choose.

Approaches:
- A. Keep one number: let the operation session raise the budget as it does today and only make the board louder. Cost: low. Risk: it changes nothing; the slide is a human habit, so the gate has to refuse.
- B. A separate hard ETA recorded at freeze, gated like the budget but extendable only on owner words (chosen). Freeze computes the estimate from the board's estimate model (the high end for a goal of this size) plus a margin, rounded up to 5 minutes, falling back to the time budget when no estimate exists, and records it in the run record and the goal file. Past it, a step or pr is refused (ETA_PAST) and the goal is put under Needs you with three choices: ship now, extend once by a stated amount, or defer. The only ways out are `goal.py set` with an owner-words record: --eta-extend N, --eta-choice ship, --eta-choice defer; raising a time budget needs a record too.
- C. Make the cap the same number as the budget. Rejected: the owner wants the ETA from the estimate, and the budget stays the outer limit.

Chosen: B.

What each done line needs:
1. Freeze: fit.frozen_fields records eta (minutes, estimate, margin, basis); the goal file shows an ETA line; the check-in's left column shows each goal's ETA clock time and a past-ETA goal is called out.
2. Gate: fit.budget_stop refuses a new step or pr past the ETA, stores the three-choice ask in the run's waiting field so the existing Needs-you item and options show it, and `goal.py set` refuses an ETA extension or a budget raise without --owner-record ID (an owner-words.tsv record covering the slug, used once).
3. Health: a rule each for a live goal with no ETA (WARN), an ETA extended without a record (FAIL) and an overrun goal not under Needs you (FAIL), each with a negative control; GRD-6 on the Guardrails page states it under o52.

Package and size: the package is at its 99-file cap and every script is near 19,000 bytes, so no file is added. The ETA code lives in workflow-monitoring's auto.py (beside owner words, 12 KB) and thin hooks call it; fit.py's queue and adopt commands move to batch.py to make room.

Open questions: none.
