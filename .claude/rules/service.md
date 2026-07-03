---
paths:
  - "service/**/*.py"
---

## Service code (handlers / logic / dal / models)

Strict layering — keep each layer's job separate:

- `service/handlers/` — Lambda entry points. **Thin.** Wire Powertools, parse/validate the event
  into a Pydantic model, call one `logic/` function, map the result to an output model. No business
  logic, no direct DB calls.
- `service/logic/` — business logic. Pure-ish functions that take/return models; no event or HTTP
  concerns.
- `service/dal/` — data access (DynamoDB). All persistence goes through here; nothing above touches
  boto3 directly.
- `service/models/` — Pydantic models shared across layers (`input`, `output`, plus DAL/env-var/config
  models under the layer that owns them).

### Conventions (as seen in this codebase)

- REST via **AWS Lambda Powertools** `event_handler` resolver; each handler is an `@app.<method>`
  route that declares `summary`/`description`/`responses`/`tags` for OpenAPI generation.
- Observability from `service/handlers/utils/observability.py` — reuse the shared `logger`, `tracer`,
  `metrics`; add a metric per meaningful event (e.g. `metrics.add_metric(...)`). Don't instantiate
  new Powertools objects.
- Environment variables: model them (`aws_lambda_env_modeler` + an env-vars Pydantic model) and read
  via `get_environment_variables(model=...)`; never read `os.environ` directly in logic.
- Validate all input with Pydantic models; return typed output models — don't hand-build dicts.
- Dynamic config / feature flags go through `parse_configuration(...)`, not ad-hoc AppConfig calls.
- Ruff is the source of truth: line length 150, py314, rules `E,W,F,I,C,B` (see `pyproject.toml`).
- Any behavior change ships with a test — see `.claude/rules/testing.md`.
