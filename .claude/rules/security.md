## Security

Cross-cutting security rules. This repo is scanned by OpenSSF Scorecard, CodeQL, and `cdk-nag`;
keep those green.

### Rules

- **Secrets:** never commit credentials, tokens, or ARNs of real accounts. No `aws_access_key`,
  no long-lived keys anywhere. CI authenticates to AWS via **OIDC** (`aws-actions/configure-aws-credentials`
  with `role-to-assume`); local runs use the developer's own profile.
- **IAM least privilege:** grant per-function roles with scoped `grant_*` helpers (see `cdk/rules`).
  Never attach broad managed policies or `*` resource/action permissions.
- **cdk-nag:** every stack runs `AwsSolutionsChecks`. New infra must pass. If a finding is a genuine
  false positive, add a `NagSuppression` **with a written justification** — never blanket-suppress.
- **Edge protection:** public API traffic goes through the `WafToApiGatewayConstruct` (WAF). Don't add
  publicly reachable endpoints that bypass it.
- **GitHub Actions:** pin to full commit SHAs, keep `permissions:` least-privilege (`contents: read`
  by default). See `.claude/rules/github-actions.md`.
- **Dependencies:** keep `npm audit` clean and Dependabot PRs current. See `.claude/rules/dependencies.md`.
- **Input validation:** all external input is validated by Pydantic models before use — untrusted data
  never reaches `logic/` or `dal/` unvalidated. See `.claude/rules/service.md`.
- If you spot a real vulnerability, surface it explicitly; don't silently work around it.
