"""Temporary diagnostic (removed before the pull request): log every regression.py or lane.py process that starts."""
import os
import sys
import time

try:
    name = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else ""
    if name in ("regression.py", "lane.py", "h.py", "-c"):
        with open(os.environ.get("DIAG_TRACE", "/tmp/diag-trace.txt"), "a") as out:
            out.write("%.3f pid=%d ppid=%d %s\n" % (time.time() % 100, os.getpid(), os.getppid(), " ".join(sys.argv)[:150]))
except Exception:
    pass
