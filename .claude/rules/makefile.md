## Makefile & commands

Drive everything through the Makefile. Don't invoke `uv`, `pytest`, `ruff`, `cdk`, or `npx`
ad hoc when a target exists — targets encode the right flags, env, and ordering.

### Command reference

| Target | What it does |
| --- | --- |
| `make dev` | Install all dependencies (Python + Node). |
| `make format` / `make format-fix` | Ruff format (check / apply). |
| `make lint` | Ruff lint. |
| `make mypy-lint` | Type check. |
| `make complex` | Complexity checks. |
| `make pre-commit` | Run pre-commit hooks. |
| `make unit` | Unit tests — fast, no AWS. |
| `make infra-tests` | CDK synth assertions (`tests/infrastructure/`). |
| `make integration` | Integration tests (may touch AWS). |
| `make coverage-tests` | Unit + integration with coverage. |
| `make e2e` | End-to-end tests against deployed stack. |
| `make deploy` / `make destroy` | **Cloud-mutating** — CDK deploy / destroy. |
| `make docs` / `make lint-docs` / `make publish-docs` | Docs build / markdownlint / publish. |
| `make openapi` / `make compare-openapi` | Generate / diff the OpenAPI schema. |
| `make update-deps` | Bump Python + Node dependencies. |
| `make pr` | Full local CI gate (see below). |

### Rules

- Before opening a PR, run `make pr` — it chains
  `deps format pre-commit complex lint lint-docs unit deploy coverage-tests e2e openapi`.
- `make deploy`, `make destroy`, and any AWS-touching suite (`integration`, `coverage-tests`, `e2e`)
  hit real cloud resources. Never run them during planning/exploration or without a clear reason.
- When editing the Makefile: keep targets `.PHONY`, one responsibility per target, and compose
  higher-level targets from smaller ones (as `pr` does) rather than duplicating command lines.
