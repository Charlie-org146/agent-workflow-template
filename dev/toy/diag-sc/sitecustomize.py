"""Temporary diagnostic (removed before the pull request): log every python process that starts."""
import os
import sys
import time

try:
    with open(os.environ.get("DIAG_TRACE", "/tmp/diag-trace.txt"), "a") as out:
        out.write("%.3f pid=%d ppid=%d %s\n" % (time.time() % 100, os.getpid(), os.getppid(), " ".join(sys.argv)[-110:]))
except Exception:
    pass
