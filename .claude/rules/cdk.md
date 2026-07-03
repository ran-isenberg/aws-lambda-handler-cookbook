---
paths:
  - "cdk/**/*.py"
---

## CDK infrastructure (constructs & stack)

Code lives in `cdk/service/`. `app.py` (repo root) is the CDK entry point that instantiates the stack.

### Structure

- **Stack** — `cdk/service/service_stack.py` (`ServiceStack`). Composes constructs and owns
  cross-cutting concerns: stack tags, security checks (`cdk-nag` `AwsSolutionsChecks` +
  `NagSuppressions`). It wires constructs together; it does **not** define individual resources.
- **Constructs** — one construct per cohesive capability, each in its own file:
  `api_construct.py` (API GW + Lambda integrations), `api_db_construct.py` (DynamoDB tables),
  `monitoring.py` (`CrudMonitoring`), `waf_construct.py` (WAF), `lambda_managed_instance_construct.py`,
  `configuration/configuration_construct.py` (AppConfig). A construct subclasses `constructs.Construct`
  and builds its resources in `__init__` via small `_build_*` / `_add_*` helper methods.
- **Constants** — `cdk/service/constants.py` for names, tags, resource paths. Don't hardcode strings
  in constructs; reference constants. Resource logical names use `get_construct_name(...)` from
  `utils.py` so they stay unique per environment.

### Rules

- Add a new capability as a **new construct** and compose it in `ServiceStack`; keep the stack thin.
- Lambda defaults are class constants on the construct (`PYTHON_3_14`, `ARM_64`, JSON logging) — reuse
  them; don't drift runtime/arch per function.
- IAM: grant least privilege with per-function roles and `grant_*` helpers; never attach broad managed
  policies. New resources must pass `cdk-nag` (v3) — fix the finding, or acknowledge it **with a reason**.
  cdk-nag v3 suppresses via CDK's native `Validations.of(scope).acknowledge(Acknowledgment(id, reason))`
  (there is no more `NagSuppressions`). Granular IAM findings use bracketed ids
  (`AwsSolutions-IAM5[Resource::*]`); ids with multiple `::` can't pass `acknowledge()`, so the stack
  records them via `_acknowledge_nag_findings` (metadata under `Validations.ACKNOWLEDGED_RULES_METADATA_KEY`).
- Any change here must keep `tests/infrastructure/test_cdk.py` green — update the `Template` assertions
  (resource counts/properties) in the same PR. Run `make infra-tests`.
- Never run `cdk deploy`/`destroy` or `make deploy`/`destroy` while iterating; use `make infra-tests`
  (synth) to validate.
