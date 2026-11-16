---
description: Daily stand-up report on the agent team's progress, posted as an issue.
on:
  schedule: daily on weekdays
  workflow_dispatch:
permissions:
  contents: read
  issues: read
  pull-requests: read
engine: copilot
tools:
  github:
    toolsets: [issues, pull_requests]
safe-outputs:
  create-issue:
    title-prefix: "[standup] "
    labels: [report]
    max: 1
    expires: 7
timeout-minutes: 10
---

# Daily stand-up

Write a stand-up for the Bank in a Box agent team. Be concise and factual; only report what you can see in issues and pull requests.

Include:

1. **Progress by wave**: for waves 1–5, closed vs total issues labelled `agent-backlog`.
2. **Done since yesterday**: merged PRs and closed issues, with links and the agent role.
3. **In flight**: issues labelled `agent-in-progress` with their open PR and its check status.
4. **Blocked**: issues labelled `blocked` and the specific open issue each is waiting on.
5. **Needs a human**: PRs waiting on review for more than a day, failing checks, closed-unmerged PRs, and any open issue labelled `security`.

End with one sentence on whether the build is on track and the single biggest risk.
