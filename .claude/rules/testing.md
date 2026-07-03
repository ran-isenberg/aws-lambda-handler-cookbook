---
paths:
  - "tests/**/*.py"
---

## Testing

Four suites, each with a distinct scope and cost. Put a test at the lowest layer that can catch the bug.

| Suite | Dir | Scope | Command |
| --- | --- | --- | --- |
| Unit | `tests/unit/` | Pure logic & models, no AWS | `make unit` |
| Integration | `tests/integration/` | Handler + logic + DAL, AWS/mocks | `make integration` |
| Infrastructure | `tests/infrastructure/` | CDK synth assertions | `make infra-tests` |
| E2E | `tests/e2e/` | Deployed stack over HTTP | `make e2e` |

### Conventions (match existing tests)

- **Unit** (`tests/unit/`): exercise models and pure logic directly. Assert Pydantic
  `ValidationError` for bad input via `pytest.raises`. Use the `# Given / When & Then` comment
  structure already in the files. No AWS, no network.
- **Integration** (`tests/integration/`): build events with the helpers in `tests/utils.py`
  (`generate_api_gw_event`, `generate_context`, `generate_random_string`) and invoke the handler.
  Mock dynamic configuration / feature flags with an inline schema + `mocker` (see
  `test_feature_flags.py` / `mock_dynamic_configuration`); don't reach a live AppConfig.
- **Infrastructure** (`tests/infrastructure/test_cdk.py`): synth the stack and assert with
  `aws_cdk.assertions.Template` — resource counts and key properties (e.g. exactly one RestApi,
  two DynamoDB global tables). Add/adjust these whenever you change `cdk/`.
- **E2E** (`tests/e2e/`): run against a real deployed stack; needs credentials and a prior `make deploy`.
- Shared fixtures live in `conftest.py` at the suite level and `tests/conftest.py` at the root; reuse
  them and `tests/utils.py` instead of re-implementing helpers.
- New behavior → a test in the right suite, same PR. Run the narrowest suite locally before pushing.
