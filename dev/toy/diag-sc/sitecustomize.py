"""Temporary diagnostic (removed before the pull request): log every python process that starts and every Popen it makes."""
import os
import subprocess
import sys
import time


def log(text):
    try:
        with open(os.environ.get("DIAG_TRACE", "/tmp/diag-trace.txt"), "a") as out:
            out.write("%.3f pid=%d %s\n" % (time.time() % 100, os.getpid(), text))
    except Exception:
        pass


log("start ppid=%d %s" % (os.getppid(), " ".join(sys.argv)[-90:]))
_orig = subprocess.Popen.__init__


def _init(self, args, *a, **k):
    _orig(self, args, *a, **k)
    log("popen child=%d %s" % (self.pid, str(args)[:110]))


subprocess.Popen.__init__ = _init
