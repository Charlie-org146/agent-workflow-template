# Restart-safe item 1 (TD487, MCH-1 'a restart loses nothing'): a 300-second launch-agent tick runs the operation pass and the check-in, and the PR and run watchers become file-backed jobs the tick resumes, so session-only crons and shell watchers stop being lost at a restart. Build the installer and its toy on the existing automation.py local install pattern; installing and loading it on this Mac (launchctl bootstrap) stays the owner's

- Slug: restart-tick
- Touches: skills, dev/toy
- ETA: 470 active minutes (estimate 373m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given the installer, then it writes a LaunchAgent plist with StartInterval 300 running the tick, a toy checks the plist and an uninstall that removes it, and nothing is loaded by the build or its tests
2. Given a watcher job file left by a stopped session, when the tick runs, then it resumes the watch (arm on clean green, or report red) once and records the result, shown by a toy with a fake gh
3. Given this goal's diff, then every script stays under 20,480 bytes, package.py --static, docs.py check and criteria.py render --check pass, and each new regression row has a red proof (regression.py red)

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
