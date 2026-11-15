#!/usr/bin/env python3
# windows: ok
# reads: skills/workflow-setup/scripts/setup.py
"""#2874: setup's first output says that un-reviewing a locked requirement needs the owner's own sentence."""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
setup = os.path.join(here, "..", "..", "skills", "workflow-setup", "scripts", "setup.py")
env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.test", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.test")
with tempfile.TemporaryDirectory() as tmp:
    for cmd in (["git", "init", "-q"], ["git", "commit", "-q", "--allow-empty", "-m", "start"]):
        subprocess.run(cmd, cwd=tmp, check=True, env=env)
    out = subprocess.run([sys.executable, setup, "--dry-run", "--bare"], cwd=tmp, capture_output=True, text=True, env=env).stdout
ok = "OWNER_WORDS" in out and "owner's own sentence" in out
print(("PASS: " if ok else "FAIL: ") + "#2874: setup's dry run says un-reviewing a locked requirement needs the owner's own sentence")
if not ok:
    print(out[:600])
sys.exit(0 if ok else 1)
