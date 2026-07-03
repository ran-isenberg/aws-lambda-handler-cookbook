## CLAUDE.md

Guidance for Claude Code in this repository. Topic rules live in [.claude/rules/](.claude/rules/)
and load automatically (path-scoped ones only when you touch matching files).

### Project

Production-grade blueprint for AWS Serverless services in Python: a Lambda handler skeleton
plus CDK deployment code, a CI/CD pipeline, and tests.

- **Runtime:** Python `>=3.14`, managed with `uv`. **Infra:** AWS CDK. **Docs:** MkDocs → GitHub Pages.

### Layout

- [service/](service/) — app code, layered `handlers/` → `logic/` → `dal/`, with `models/` (Pydantic) shared.
- [cdk/](cdk/) — CDK stacks and constructs (`cdk/service/`).
- [tests/](tests/) — `unit/`, `integration/`, `infrastructure/`, `e2e/`.
- [docs/](docs/) — documentation and runnable examples.

### Rules index

- `.claude/rules/makefile.md` — command reference; always use `make` targets. **(loaded every session)**
- `.claude/rules/github-actions.md` — CI workflows; SHA-pinning. *(scoped to `.github/workflows/`)*
- `.claude/rules/service.md` — handler/logic/dal layering, Powertools, Pydantic. *(scoped to `service/`)*
- `.claude/rules/models.md` — Pydantic model conventions and placement. *(scoped to `service/**/models/`)*
- `.claude/rules/testing.md` — unit / integration / e2e / infra test patterns. *(scoped to `tests/`)*
- `.claude/rules/cdk.md` — construct and stack structure. *(scoped to `cdk/`)*
- `.claude/rules/docs.md` — Zensical build, markdownlint, OpenAPI sync. *(scoped to `docs/`)*
- `.claude/rules/security.md` — secrets, IAM, cdk-nag, WAF, OIDC. **(loaded every session)**
- `.claude/rules/dependencies.md` — uv + npm, `make update-deps`, audits. **(loaded every session)**
- `.claude/rules/git-pr.md` — Conventional Commits, release bumps, PR labels. **(loaded every session)**

### Planning (plan mode)

- Explore the relevant `service/` layer and its tests before proposing changes; name the files you'll touch.
- Respect the layering — never move logic into handlers or bypass the DAL.
- Every behavior change names the suite that covers it and updates/adds tests.
- **Never run cloud-mutating commands while planning or exploring** — `make deploy`/`destroy`,
  `cdk deploy/destroy`, `aws …`. Planning uses read-only and local commands only.
- Verify before claiming done: run `make lint` plus the narrowest relevant suite; report real output.
