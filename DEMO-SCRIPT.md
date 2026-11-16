# Demo script (about 30 minutes, adjustable)

## 0. Before you go on stage
- Fresh repo from this template; `bootstrap.sh` already run; secrets set.
- Ruleset on `main`: PR required, `ci` required once issue 4 lands, Copilot code review on.
- Pre-run waves 1–2 on a backup repo in case the live run is slow.

## 1. Core: the plan is the product (3 min)
- Show `specs/SPEC.md` and the issue list: 25 issues, `Blocked by` links, `agent:` and `wave:` labels.
- Point out: acceptance criteria are checkboxes; every PR must tick them.

## 2. Workflows: the orchestrator (5 min)
- Open `.github/workflows/orchestrator.md`: plain-English instructions, `safe-outputs` allowlist, read-only permissions.
- `gh aw run orchestrator`. Only issue 1 (ADRs) has no blocker, so it is the only one assigned. After you merge it, issues 2, 3 and 12 unblock and the orchestrator starts two of them.
- Show the compiled `.lock.yml` and the firewall/threat-detection steps.

## 3. Copilot: the team at work (8 min)
- Open a Copilot PR: session log, `Closes #N`, ticked criteria.
- Show `.github/agents/backend.agent.md` and `copilot-instructions.md`.
- Request Copilot code review on the PR; merge; show the orchestrator unblocking the next issue.
- Open the Copilot app / agents panel to show parallel sessions.

## 4. GHAS: security as code (6 min)
- Issue 21's PR: CodeQL, dependency review, Dependabot config, SECURITY.md.
- **Live plant:** on a branch, add a vulnerable dependency version and a hard-coded test token. Show dependency review failing the PR and push protection blocking the secret.
- Issue 22's threat model: findings filed as `security` issues, assigned back to the team.
- Show security overview and a Copilot Autofix suggestion on a CodeQL alert.

## 5. Ship it (4 min)
- `docker compose up --build`, open http://localhost:8080, create an account, deposit, withdraw too much (inline 422 message).
- Tag `v0.1.0`; show GHCR image, SBOM, and provenance attestation.

## 6. Day-2 (4 min)
- Assign issue 26 (overdraft protection) to Copilot live.
- Show Dependabot PRs and the standup issue from `standup.md`.

## 7. Universe slot
Add this year's new capabilities here, one line each with the click path. Verified so far: **GitHub Agentic Workflows GA (Oct 28, 2026)**.

## Fallbacks
- Copilot slow → switch to the backup repo's finished PRs.
- Token errors → `gh aw run orchestrator` logs show which secret is missing.
- Network flaky → rehearse locally with `docker agent run dev-team.yaml`.
