#!/usr/bin/env python3
"""Create GitHub labels and issues from specs/backlog.yaml.

Requires: gh (authenticated), PyYAML (pip install pyyaml).

  python3 scripts/create_issues.py --repo OWNER/REPO --dry-run
  python3 scripts/create_issues.py --repo OWNER/REPO
  python3 scripts/create_issues.py --repo OWNER/REPO --include-day2

Issues with no unmet dependency get `agent-ready`; the rest get `blocked`.
Dependencies are written as "Blocked by #N" lines, which the orchestrator
workflow (.github/workflows/orchestrator.md) reads.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ["architect", "designer", "backend", "frontend", "qa", "security", "devops", "docs"]

LABELS = (
    [(f"agent:{a}", "5319E7", f"Handled by the {a} agent") for a in AGENTS]
    + [(f"wave:{w}", "BFD4F2", f"Build wave {w}") for w in range(1, 7)]
    + [
        ("agent-backlog", "0E8A16", "Part of the agent-built backlog"),
        ("agent-ready", "0E8A16", "Unblocked; orchestrator may assign it"),
        ("agent-in-progress", "FBCA04", "Assigned to an agent"),
        ("blocked", "B60205", "Waiting on another issue"),
        ("stretch", "C5DEF5", "Optional scope"),
        ("day-2", "D4C5F9", "Day-2 demo scenario"),
        ("feature", "1D76DB", "New feature"),
        ("security", "B60205", "Security finding"),
    ]
)


def sh(args, dry, stdin=None):
    if dry:
        print("  $", " ".join(args))
        return "https://github.com/DRY/RUN/issues/0"
    out = subprocess.run(args, input=stdin, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"gh failed: {' '.join(args)}\n{out.stderr}")
    return out.stdout.strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--include-day2", action="store_true")
    a = p.parse_args()

    backlog = yaml.safe_load((ROOT / "specs" / "backlog.yaml").read_text())["issues"]
    backlog = [i for i in backlog if a.include_day2 or not i.get("day2")]
    ids = {i["id"] for i in backlog}

    print("Ensuring labels...")
    for name, color, desc in LABELS:
        sh(["gh", "label", "create", name, "--repo", a.repo, "--color", color,
            "--description", desc, "--force"], a.dry_run)

    number = {}
    for i in sorted(backlog, key=lambda x: x["id"]):
        deps = [d for d in i.get("depends_on", []) if d in ids]
        missing = [d for d in deps if d not in number]
        if missing:
            sys.exit(f"issue {i['id']} depends on {missing}, which is created later; fix ordering")
        blockers = "".join(f"Blocked by #{number[d]}\n" for d in deps)
        header = (
            f"**Agent:** `agent:{i['agent']}` · **Wave:** {i['wave']} · "
            f"**Spec:** [`specs/SPEC.md`](../blob/main/specs/SPEC.md)\n\n"
        )
        body = header + i["body"].rstrip() + "\n\n---\n" + (blockers or "No blockers.\n")
        labels = ["agent-backlog", f"agent:{i['agent']}", f"wave:{i['wave']}",
                  "blocked" if deps else "agent-ready"] + i.get("labels", [])
        cmd = ["gh", "issue", "create", "--repo", a.repo, "--title", i["title"], "--body-file", "-"]
        for l in labels:
            cmd += ["--label", l]
        url = sh(cmd, a.dry_run, stdin=body)
        number[i["id"]] = int(url.rstrip("/").split("/")[-1])
        print(f"#{number[i['id']]:>3}  [{i['agent']:<9}] {i['title']}")


if __name__ == "__main__":
    main()
