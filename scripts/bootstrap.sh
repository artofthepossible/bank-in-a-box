#!/usr/bin/env bash
# One-time setup for a fresh copy of this repo. Run from the repo root.
#   ./scripts/bootstrap.sh OWNER/REPO
set -euo pipefail

REPO="${1:?usage: bootstrap.sh OWNER/REPO}"

command -v gh >/dev/null || { echo "gh CLI required"; exit 1; }
gh auth status >/dev/null

echo "==> Installing gh-aw extension"
gh extension install github/gh-aw 2>/dev/null || gh extension upgrade gh-aw || true

echo "==> Compiling agentic workflows (.md -> .lock.yml)"
gh aw compile

echo "==> Secrets"
echo "Create these yourself; this script will not handle token values:"
echo "  gh secret set COPILOT_GITHUB_TOKEN -R $REPO    # PAT that lets the Copilot engine run"
echo "  gh secret set GH_AW_AGENT_TOKEN   -R $REPO    # fine-grained PAT used to assign issues to Copilot"
echo "See README 'Prerequisites' for the scopes."

echo "==> Creating labels and issues (dry run first)"
python3 scripts/create_issues.py --repo "$REPO" --dry-run
read -r -p "Create them for real? [y/N] " ok
[[ "$ok" == "y" ]] && python3 scripts/create_issues.py --repo "$REPO"

echo "Done. Trigger the first run:  gh aw run orchestrator"
