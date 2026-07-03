---
paths:
  - "service/**/models/**/*.py"
  - "service/models/**/*.py"
---

## Pydantic models

All typed boundaries in the service are Pydantic models. Extends `.claude/rules/service.md`.

### Where models live

- `service/models/` — domain models shared across layers: `input.py` (request models),
  `output.py` (response models), `order.py` (domain entity), `exceptions.py` (typed errors).
- `service/handlers/models/` — handler-scoped models: `env_vars.py` (environment variables),
  `dynamic_configuration.py` (AppConfig / feature-flag schema).
- `service/dal/models/` — persistence models: `db.py` (DynamoDB item shape).

### Rules

- Put each model in the layer that owns its concern; don't leak a DAL model into a handler response
  or vice versa. Map between layers explicitly.
- Request/response models are the contract: they drive validation **and** the generated OpenAPI schema.
  Changing a field is an API change — regenerate the schema (`make openapi`) and update tests.
- Constrain fields at the model (types, `Field(...)` bounds, validators) so bad input raises
  `ValidationError` at the edge — don't defer validation into `logic/`.
- Environment variables are always modeled (`env_vars.py`) and read via
  `get_environment_variables(model=...)`; never `os.environ` directly.
- Keep models declarative — no I/O, no boto3, no side effects inside a model.
- Prefer extending an existing model over adding a parallel dict-shaped payload.
