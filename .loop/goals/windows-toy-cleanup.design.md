# Design: windows-toy-cleanup

## Problem

Three Python toys fail on Windows in their setup and cleanup only (#5766). (1) test-machines.py and test-desk.py end with the
process's own working directory inside the temp tree (`os.chdir(pc)`, `os.chdir(mac)`, `os.chdir(repo)`), and test-desk.py also
starts a background worker (`machines.start_worker`) whose log file may still be open; Windows refuses to remove a directory that
is a process's cwd or holds an open file, so TemporaryDirectory cleanup raises WinError 32. (2) test-restart-tick.py builds PATH
with ":" instead of os.pathsep, and its fake `gh` is a shell script, which CreateProcess cannot launch (it resolves "gh" to
gh.exe only); the tick therefore never calls the stub merge.py and merge.log is never written. No product script is the holder:
the cwd is the toy's own, and the worker's log is opened by machines.start_worker for a `python -c pass` child that exits at once.

## Approaches

1. Change product code so it closes handles or tolerates a missing gh. Rejected: outside the goal's conditions (toys only).
2. Fix only the toys. (a) At the end of test-machines.py and test-desk.py, `os.chdir` out of the temp tree (into the toy's own
   folder) before the TemporaryDirectory exits, in a try/finally; in test-desk.py also wait for the background worker's pid to
   end (bounded) before leaving. (b) In test-restart-tick.py, join PATH with os.pathsep; and on Windows only (os.name == "nt"),
   give the child tick a `sitecustomize.py` in a temp dir on PYTHONPATH that routes subprocess calls of "gh" to the existing
   fake script through bash, so the tick sees the same fake it sees on the Mac. Cost: a dozen lines per toy. Risk: the shim
   hides a real gh problem on Windows; it is confined to the toy's own child processes.

## Chosen

Approach 2. The Mac path is unchanged by construction: the cwd change is a no-op there, os.pathsep is ":" there, and the shim
is only written when os.name is "nt".

## What each done line needs

1. A try/finally chdir out of the temp tree (and the worker wait in test-desk.py) so cleanup raises no WinError 32 in test-machines.py and test-desk.py.
2. The PATH and gh shim in test-restart-tick.py, so the tick calls the stub merge.py and merge.log holds the expected calls.
3. The control: the same toys' PASS lines are unchanged on macOS. I cannot run macOS here; the Mac's lane is the proof, and on the PC I compare the PASS lines before and after the change.

## Open questions

None for the owner. If the file holder turns out to be a product script, stop: the goal goes back to full depth and to top.
