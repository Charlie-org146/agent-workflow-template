"""Helpers moved whole out of update.py to keep it within its size line."""
import os
import subprocess


def stop(proc, sig):
    """Kill proc's tree on Windows, else signal its group; an ended one is fine."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
        return
    try:
        os.killpg(proc.pid, sig)  # posix-only branch
    except ProcessLookupError:
        pass
