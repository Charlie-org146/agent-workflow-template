# scripts-a design

Problem: 14 scripts in workflow-delivery and workflow-monitoring are over 19,000 LF bytes, several within 100 bytes of the 20,480 hard cap. Any growth breaks the size rule.

Approach A: trim comments, docstrings, dead code and repeated text in place. Cost: low; risk: low, behavior unchanged. Approach B: split modules. Cost: new files against the 98-file package cap; risk: higher. Chosen: A, with a fold into an existing module only where A cannot reach 19,000.

Done line needs: measure each script after replacing CRLF, trim, run each script's toys, keep the file count.

Open questions: none.

VERDICT: self: approve
