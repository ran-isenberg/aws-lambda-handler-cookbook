---
paths:
  - ".github/workflows/**"
---

## GitHub Actions

Workflows: `main-serverless-service.yml` (push to main → staging → production → pages/release),
`pr-serverless-service.yml` (PR checks + OpenAPI breaking-change diff), `codeql-analysis.yml.yml`,
`scorecard.yml`, `pr-labeler.yml`, `comment_issues.yml`.

### Rules

- **Pin every action to a full 40-char commit SHA**, never a tag or branch. Keep a trailing
  `# vX.Y.Z` comment so humans can read the version:

  ```yaml
  uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
  ```

- To bump an action, resolve the release tag to its commit SHA rather than trusting a floating tag:

  ```bash
  gh api repos/OWNER/REPO/releases/latest -q .tag_name
  gh api repos/OWNER/REPO/git/ref/tags/TAG -q .object.sha   # deref annotated tags if needed
  ```

  Update the SHA **and** the version comment together.
- Keep `permissions:` minimal and least-privilege at the workflow/job level (`contents: read` by
  default; add `id-token: write` only for the OIDC AWS-auth jobs, `pages: write` only for Pages).
- AWS auth uses OIDC via `aws-actions/configure-aws-credentials` with `role-to-assume` — never
  long-lived keys. Secrets come from `secrets.*`; never inline credentials.
- Prefer the `ubuntu-24.04-arm` runners already used here for build/deploy jobs (faster ARM64).
- After editing a workflow, sanity-check YAML and that every `uses:` line still carries a SHA:
  `grep -rEn "uses: .+@[0-9a-f]{40} # v" .github/workflows/`.
