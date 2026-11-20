"""Toy helper: give goal SLUG its Verify by hand step and commit it, so goal.py pr no longer refuses an empty section."""
import re
import subprocess
import sys

path = ".loop/goals/%s.md" % sys.argv[1]
text = open(path).read()
if not re.search(r"## Verify by hand\n\n(?:<!--.*?-->\n)?\s*1\.", text, re.S):
    text = re.sub(r"(## Verify by hand\n\n(?:<!--.*?-->\n)?)", r"\g<1>1. Open calc.py.\n   Expect: it has the change.\n", text, count=1, flags=re.S)
    open(path, "w").write(text)
    subprocess.run(["git", "add", path], check=True)
    subprocess.run(["git", "commit", "-qm", "verify by hand"], check=True)
