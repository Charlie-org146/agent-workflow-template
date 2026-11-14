"""The memory floor (GRD-2): free_gb reads the machine's free memory, and wait_memory holds a lane that is about to run rows
while it is below min_free_memory_gb."""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slots  # noqa: E402


def free_gb():
    """Free virtual memory in GB (Windows: the free page file; macOS: free, inactive and speculative pages; Linux: MemAvailable),
    LOOP_FREE_GB to fake it, None when it can't be read (a lane is then never held)."""
    try:
        if os.environ.get("LOOP_FREE_GB"):
            return float(os.environ["LOOP_FREE_GB"])
        if os.name == "nt":
            import ctypes
            class Status(ctypes.Structure):
                _fields_ = [("size", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(n, ctypes.c_ulonglong) for n in ("tp", "ap", "tpf", "apf", "tv", "av", "ae")]
            held = Status()
            held.size = ctypes.sizeof(held)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(held))
            return held.apf / 2 ** 30
        if sys.platform == "darwin":
            text = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
            page = int(re.search(r"page size of (\d+)", text).group(1))
            return sum(int(m) for m in re.findall(r"Pages (?:free|inactive|speculative):\s+(\d+)", text)) * page / 2 ** 30
        return int(re.search(r"MemAvailable:\s+(\d+) kB", open("/proc/meminfo").read()).group(1)) / 2 ** 20
    except Exception:
        return None


def wait_memory(root):
    """A lane about to run rows waits while free memory is below min_free_memory_gb (default 4, 0 is off); a lane already running is
    never stopped. Each wait is logged in <git common dir>/loop/memory-waits.log for the check-in and health; past 4x the lane's
    time limit (LOOP_MEMORY_WAIT_SECONDS) it gives up with exit 4."""
    try:
        need = json.load(open(os.path.join(root, ".loop", "config.json"))).get("min_free_memory_gb", 4)
    except (OSError, ValueError, AttributeError):
        need = 4
    need = need if isinstance(need, (int, float)) and not isinstance(need, bool) and need > 0 else 0
    began, told = time.time(), 0.0
    cap = float(os.environ.get("LOOP_MEMORY_WAIT_SECONDS") or 4 * slots.time_limit(root)[0])
    while need:
        free = free_gb()
        if free is None or free >= need:
            return
        if time.time() - told > 300:
            told = time.time()
            line = "LANE_MEMORY: %.1f GB free, min_free_memory_gb is %g; this lane waits and starts when memory frees (a lane already running is not stopped)" % (free, need)
            print(line, flush=True)
            try:
                done = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=root, capture_output=True, text=True)
                with open(os.path.join(os.path.abspath(os.path.join(root, done.stdout.strip())), "loop", "memory-waits.log"), "a") as log:
                    log.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), line))
            except OSError:
                pass
        if time.time() - began > cap:
            slots.note("LANE_WAIT_TIMEOUT: waited %ds for memory (%.1f GB free, min_free_memory_gb %g); nothing ran. Fix: free memory, or lower min_free_memory_gb" % (time.time() - began, free, need))
            sys.exit(slots.EXIT_WAIT)
        time.sleep(min(slots.POLL * 5, max(cap / 4, 0.05)))
