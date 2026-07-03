## Git & pull requests

This repo uses Conventional Commits, and release automation depends on them — get the prefix right.

### Commit / PR titles

- Allowed types (enforced on PR titles by `.github/semantic.yml`, `titleOnly`):
  `feature`, `fix`, `docs`, `refactor`, `perf`, `test`, `chore`, `revert`.
- Format: `type: short imperative summary` (e.g. `fix: unique name of capacity provider`).
  A scope is optional (`chore(deps): ...`); a breaking change uses `!:` (e.g. `feature!: ...`).
- **The release job parses commit messages** (`main-serverless-service.yml`): `feat`/`feature`
  ⇒ minor bump, `breaking` or `!:` ⇒ major bump, anything else ⇒ patch. A mislabeled commit ships
  the wrong version — match the change to the type.

### Workflow

- Don't commit or push unless asked. Never push directly to `main`; branch first and open a PR.
- Run `make pr` (the full local gate) before opening a PR so CI passes on the first try.
- PR labels drive the generated changelog (`.github/release.yml`): `breaking-change`, `enhancement`,
  `bug`, `documentation`, `chore`, `dependencies`. Label PRs so they land in the right section.
- Keep the OpenAPI schema in sync with API changes (`make openapi`); the PR check diffs it and fails
  if it drifted. See `.claude/rules/docs.md`.
- End commit messages authored by Claude with the required `Co-Authored-By` trailer.
