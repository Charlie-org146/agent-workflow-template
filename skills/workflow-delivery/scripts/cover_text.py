"""The L1 cover's PR text (cover.py imports it): the Regression lane part and, for the PR that moves the reach finder, its Limits
block. cover.py keeps the claim and the checks; this file only words them."""
import os


def limits(root):
    """The PR text's Limits block (binding rule 4), for the PR that moves the reach finder and its fingerprint."""
    import cover
    if "skills/workflow-regression/scripts/row_reach.py" not in cover.sh(["git", "diff", "--name-only", "origin/main...HEAD"], root)[1].split():
        return ""
    return ("\n### Limits\n\n- The first PRs after this merges run cold on GitHub: the runner fingerprint changed, so every cached plan and record is invalid.\n"
            "- Platform rows not on the skip list are covered on Ubuntu only; see the skip list.\n"
            "- This PR changes the regression scripts, so its own cover is off (the tooling-cover line); its measured with-and-without minutes cannot come from its own lanes.\n"
            "- Not tested: the full-lane rerun after a late loss (cover.late is tested, the goal_steps.py call is not), and flow.py qa end to end through the hook.\n")


def pr_part(runs, slug, keep=""):
    import cover
    claim = cover.load(runs, slug).get("claim")
    root = cover.sh(["git", "rev-parse", "--show-toplevel"])[1]
    if not claim:
        return keep + limits(root)
    times = {}
    try:
        for x in open(os.path.join(root, ".github", "workflows", "row-times.tsv")).read().splitlines():
            c = x.split("\t")
            times[c[0]] = float(c[1])
    except (OSError, ValueError, IndexError):
        pass
    saved = ("estimated avoided: about %.0f min (the covered rows' recorded times; an estimate)" % (
        sum(times.get(k, 0) for k in claim["covered"]) / 60) if times else "estimated avoided: unavailable")
    head = cover.sh(["git", "rev-parse", "--short=12", "HEAD"], root)[1]
    ran = sorted(set(claim["local"]) | set(claim.get("ran", [])))  # every row that ran locally at any step
    return ("\n### Regression lane\n\nCovered by %s, the PR's pull_request run (regression-pr), pending GitHub execution, head %s: %d rows (%s)\n\n"
            "Run locally: %d rows (%s)\n\n%s\n%s" % (cover.NAME, head, len(claim["covered"]), ", ".join(claim["covered"][:40]), len(ran),
                                                      ", ".join(ran[:40]) or "none", saved, limits(root)))
