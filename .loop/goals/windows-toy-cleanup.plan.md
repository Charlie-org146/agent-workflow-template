# Plan: windows-toy-cleanup

Depth condensed (TD871/TD872: toy fixtures only, no product file). If any product file turns out to be needed, stop: the goal
goes back to full depth and to top.

## Checked against the code

- dev/toy/test-desk.py ends with `os.chdir(repo)` (line ~72) and `machines.start_worker(...)`; its TemporaryDirectory is the
  outermost `with` (line 25). dev/toy/test-machines.py has `os.chdir(pc)` / `os.chdir(mac)` at lines 89-123 inside
  `with tempfile.TemporaryDirectory() as TMP` (line 43). The process cwd inside the temp tree is the toy's own, not a product script's.
- dev/toy/test-restart-tick.py: `run()` (line ~58) starts `sys.executable mailbox.py ...` with `env`; `env` sets
  `PATH=bin_ + ":" + PATH`; `bin_/gh` and `bin_/launchctl` are `#!/bin/sh` scripts; mailbox.py calls `subprocess.run(["gh", ...])`
  (lines 137, 291) and `LOOP_LAUNCHCTL` (line 358) by name. CreateProcess resolves "gh" to gh.exe only, so the stub never runs.
  mailbox.py is not changed.

## Build steps (after the plan gate)

1. test-machines.py and test-desk.py: a small helper `wait_pid(pid, seconds=15)` that waits for a process to end (on Windows
   ctypes OpenProcess(SYNCHRONIZE) plus WaitForSingleObject; elsewhere poll `os.kill(pid, 0)`; never `os.kill(pid, 0)` on
   Windows, which terminates the process; an append-open of the log proves nothing because Python's open shares the file).
   The background worker the toy starts is `worker.py loop` (watch.launch), which outlives the call, has the temp tree as its
   cwd and the log as stdout: in test-desk.py (`machines.start_worker`, state["pid"]) and in test-machines.py (the `take` child,
   pid in its state). Before the temp tree is removed: wait for each such pid, then `os.chdir(HERE)` in a finally. If a worker
   is still running after the wait the toy says so (it never hides it); a worker that never ends is a product finding: stop.
2. test-restart-tick.py: flip the marker from `# windows: skip` to `# windows: ok`; `PATH=bin_ + os.pathsep + PATH`; when
   `os.name == "nt"`, write a `sitecustomize.py` into a temp dir and put it first on PYTHONPATH, keeping the existing
   PYTHONPATH entries after it and importing any sitecustomize already on the path (check-reads.sh puts one there). The shim
   wraps `subprocess.run` and `subprocess.Popen` so a call whose argv[0] is `gh` or the LOOP_LAUNCHCTL path runs
   `bash <script with forward slashes> args`. Nothing is written on other systems.
3. Run the three toys directly on the PC, before and after: the PASS lines the Mac prints must all be present and none removed.

## Tests per done line (no new rows; the existing rows run these toys)

1. machines-handover, machines-handover-4787, desk-lists, desk-lists-4805: seen red on the PC (#5766), expected green.
2. restart-tick-agent: seen red (FileNotFoundError merge.log), expected green with merge.log's calls asserted by the toy itself.
3. macOS control: I cannot run macOS here. The proof on the PC is that the diff leaves every `check(...)` line and every PASS
   string unchanged and only adds setup/cleanup (chdir, os.pathsep, a Windows-only shim). The Mac's lane is the actual proof;
   I do not claim it.

## What could break

- The shim hides a real gh problem on Windows: confined to this toy's child processes, written only when os.name is "nt".
- The worker wait could hang: bounded at 10 s, then the toy proceeds and cleanup may still fail loudly (not silently).
- A stale handle other than cwd or the worker log: found by running the toys; if the holder is a product script, stop and report.

## Out of scope

Every product script, make.sh, DOC-19, the home guard, the known list, G1's toys.

## Review

Red-team (fresh reviewer, run from this worktree: pwd /c/Users/chang/code/agent-workflow-template/.git/loop/worktrees/windows-toy-cleanup, HEAD 56a18493e): CHANGES on the worker child (worker.py loop outlives the call, also in test-machines.py), the wait method, the `# windows: skip` marker and the sitecustomize chaining; all folded into the build steps above. No product file is needed so far.
