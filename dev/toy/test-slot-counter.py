#!/usr/bin/env python3
# reads: skills/workflow-regression/scripts/slots.py skills/workflow-setup/scripts/settings.py
"""Check-slot command: fake gh, no network."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

script = Path(__file__).resolve().parents[2] / 'skills/workflow-regression/scripts/slots.py'
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    subprocess.run(['git', 'init', '-q', temp], check=True)
    (root / '.loop').mkdir()
    (root / 'nested').mkdir()
    gh = root / 'gh'
    gh.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$FIXTURE/calls"\ncat "$FIXTURE/prs.json"\n')
    gh.chmod(0o755)
    env = dict(os.environ, PATH=temp + os.pathsep + os.environ['PATH'], FIXTURE=temp)
    pending = {'number': 1, 'statusCheckRollup': [{'status': 'QUEUED'}, {'status': 'IN_PROGRESS'}]}
    completed = {'number': 2, 'statusCheckRollup': [{'status': 'COMPLETED', 'conclusion': 'FAILURE'}]}

    def check(label, prs, config, code, output):
        (root / '.loop/config.json').write_text(json.dumps(config))
        (root / 'prs.json').write_text(json.dumps(prs))
        (root / 'calls').write_text('')
        done = subprocess.run(['python3', str(script), 'slots'], cwd=root / 'nested', env=env, capture_output=True, text=True)
        assert (done.returncode, done.stdout.strip()) == (code, output), (label, done.returncode, done.stdout, done.stderr)
        calls = (root / 'calls').read_text().splitlines()
        assert calls == ['pr list --state open --json number,statusCheckRollup --limit 1000000'], calls
        print('PASS:', label, output)

    check('two pending PRs fill cap', [pending, dict(pending, number=3), completed], {'check_slots': 2}, 1, 'SLOTS 2/2')
    check('one pending PR uses one slot', [pending, completed], {'check_slots': 2}, 0, 'SLOTS 1/2')
    check('negative control: completed checks and no checks use none', [completed, {'number': 4, 'statusCheckRollup': []}], {}, 0, 'SLOTS 0/2')
    check('cap override', [pending], {'check_slots': 1}, 1, 'SLOTS 1/1')
    check('a finished commit status (no status field) uses no slot', [{'number': 5, 'statusCheckRollup': [{'state': 'SUCCESS'}, {'status': 'COMPLETED'}]}], {}, 0, 'SLOTS 0/2')
    check('a pending commit status uses a slot', [{'number': 6, 'statusCheckRollup': [{'state': 'PENDING'}]}], {}, 0, 'SLOTS 1/2')
    gh.write_text('#!/bin/sh\necho "gh: not logged in" >&2\nexit 1\n')
    done = subprocess.run(['python3', str(script), 'slots'], cwd=root / 'nested', env=env, capture_output=True, text=True)
    assert done.returncode == 2 and done.stdout.startswith('SLOTS unknown: gh: not logged in'), (done.returncode, done.stdout)
    print('PASS: a gh that fails is exit 2 SLOTS unknown, never mistaken for full (1)')
