"""Helpers moved whole out of update.py to keep it within its size line."""
import os
import subprocess

os.environ.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1", GIT_EDITOR="true", GIT_ASKPASS="true", SSH_ASKPASS="true")  # no prompt can hang a script


def stop(proc, sig):
    """Kill proc's tree on Windows, else signal its group; an ended one is fine."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        return
    try:
        os.killpg(proc.pid, sig)  # posix-only branch
    except ProcessLookupError:
        pass
