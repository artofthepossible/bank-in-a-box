# Instructions for every agent working in this repo

You are one member of a team building **Bank in a Box** from GitHub issues.

1. Read `specs/SPEC.md` first. It is the source of truth. If you think it is wrong, say so in the PR; do not silently deviate.
2. The issue has an `agent:<role>` label. Follow `.github/agents/<role>.agent.md` for that role.
3. Do exactly the issue's scope. Anything else you notice becomes a **new issue**, not a drive-by change.
4. Open one PR per issue. Title: the issue title. Body ends with `Closes #<issue>`. Tick the acceptance criteria in the PR description and say how each was verified.
5. Run the checks before you push: `mvn -B verify` for Java, `npm test && npm run build` in `frontend/`.
6. Money is `long` cents. Never `double` or `float`. See ADR-002.
7. Never commit secrets, `.env` files, or generated build output (`target/`, `node_modules/`, `frontend/dist/`).
8. Workflows you write use least-privilege `permissions:` and pin third-party actions to full commit SHAs.
9. Match existing style. Small classes, constructor injection, no static mutable state.
10. If blocked by a missing prerequisite, comment on the issue naming the blocker and stop.
