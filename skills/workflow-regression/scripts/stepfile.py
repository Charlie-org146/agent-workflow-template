"""The workflow step that previews the step causes (filing is off) (DEL-19), appended to slots.SUMMARY_JOB: actions.py takes both from here."""
from slots import ROUTINE_STEP, SUMMARY_JOB as _SUMMARY  # noqa: F401
FILE_STEP = r"""      - name: Preview the step causes
        if: always()
        continue-on-error: true
        run: |
          f=skills/workflow-docs/scripts/steps_page.py
          if [ -f "$f" ]; then python3 "$f" file; else echo "NOTE: $f is not in this repo, so step causes are not previewed (SC_MISSING). Fix: install the workflow package's skills here"; fi
"""

SUMMARY_JOB = _SUMMARY + FILE_STEP
