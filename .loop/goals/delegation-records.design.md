# delegation-records design (TD465; agreed by operation-mac as written)

A delegated record is the same 5-column row as any owner-words record (id, time, session, JSON text, covers), so every reader of
`owner-words.tsv` keeps working. What marks it: the session column reads `operation-top:delegated:TDn:DOC-2:rN` (the decision number and
DOC-2's revision it rests on); the text is the owner's ASKING words, verbatim.

- Written by `sessions.py owner-words TEXT --ids SLUG,ID --from top --delegated TDn --doc2 rN` (auto.add_owner_words): refused unless it
  is --from top and TDn / rN are well formed; the asking words go through the unchanged `layers.relay` safety-class refusal.
- Used by `criteria.py review` (no --user needed) and `criteria.py revise`, and only when DOC-2 has the revision row rN and neither the
  asking words nor the requirement text being reviewed or revised matches the unchanged `auto.CLASSES` (read from workflow-monitoring where
  it lives, never copied; unreadable counts as a safety class). A safety-class change is refused exactly as before, and even with --user a
  delegated record is never the owner's own words for a safety-class requirement.
- Listed in the next check-in (`Delegated approvals`), once each.
