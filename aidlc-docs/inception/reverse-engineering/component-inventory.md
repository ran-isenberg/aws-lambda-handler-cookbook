# Component Inventory

## Application Packages

| Package                     | Location                   | Purpose                                                                    |
| --------------------------- | -------------------------- | -------------------------------------------------------------------------- |
| **service**                 | `service/`                 | Main application code containing handlers, business logic, DAL, and models |
| **service.handlers**        | `service/handlers/`        | Lambda function entry points and HTTP request handling                     |
| **service.handlers.utils**  | `service/handlers/utils/`  | Observability setup, API resolver, dynamic configuration                   |
| **service.handlers.models** | `service/handlers/models/` | Environment variables and configuration schemas                            |
| **service.logic**           | `service/logic/`           | Business logic layer with order creation logic                             |
| **service.logic.utils**     | `service/logic/utils/`     | Idempotency configuration                                                  |
| **service.dal**             | `service/dal/`             | Data access layer with DynamoDB implementation                             |
| **service.dal.models**      | `service/dal/models/`      | Database schemas and table definitions                                     |
| **service.models**          | `service/models/`          | Domain models, DTOs, and exceptions                                        |

## Infrastructure Packages

| Package              | Type | Purpose                               |
| -------------------- | ---- | ------------------------------------- |
| **cdk.service**      | CDK  | Main CDK service package              |
| **service_stack**    | CDK  | Main CloudFormation stack definition  |
| **api_construct**    | CDK  | API Gateway + Lambda construct        |
| **api_db_construct** | CDK  | DynamoDB tables (Orders, Idempotency) |
| **waf_construct**    | CDK  | Web Application Firewall (production) |
| **monitoring**       | CDK  | CloudWatch dashboards and alarms      |
| **configuration**    | CDK  | AWS AppConfig for feature flags       |

## Shared Packages

| Package                     | Type      | Purpose                                     |
| --------------------------- | --------- | ------------------------------------------- |
| **service.models**          | Models    | Shared domain models (Order, Input, Output) |
| **service.handlers.models** | Models    | Configuration and environment schemas       |
| **tests.utils**             | Utilities | Test utilities and helpers                  |

## Test Packages

| Package                  | Type           | Purpose                                          |
| ------------------------ | -------------- | ------------------------------------------------ |
| **tests.unit**           | Unit           | Unit tests for models and validation             |
| **tests.integration**    | Integration    | Integration tests with mocked AWS services       |
| **tests.e2e**            | E2E            | End-to-end tests against deployed infrastructure |
| **tests.infrastructure** | Infrastructure | CDK stack validation tests                       |

## Total Count

| Category           | Count |
| ------------------ | ----- |
| **Total Packages** | 17    |
| **Application**    | 9     |
| **Infrastructure** | 7     |
| **Shared**         | 3     |
| **Test**           | 4     |

## File Count by Directory

| Directory                    | Python Files | Purpose           |
| ---------------------------- | ------------ | ----------------- |
| `service/`                   | 1            | Root module       |
| `service/handlers/`          | 2            | Lambda handlers   |
| `service/handlers/utils/`    | 4            | Handler utilities |
| `service/handlers/models/`   | 3            | Handler models    |
| `service/logic/`             | 2            | Business logic    |
| `service/logic/utils/`       | 2            | Logic utilities   |
| `service/dal/`               | 3            | Data access layer |
| `service/dal/models/`        | 2            | DAL models        |
| `service/models/`            | 5            | Domain models     |
| `cdk/`                       | 1            | CDK root          |
| `cdk/service/`               | 7            | CDK constructs    |
| `cdk/service/configuration/` | 3            | AppConfig         |
| `tests/`                     | 2            | Test root         |
| `tests/unit/`                | 6            | Unit tests        |
| `tests/integration/`         | 4            | Integration tests |
| `tests/e2e/`                 | 2            | E2E tests         |
| `tests/infrastructure/`      | 2            | CDK tests         |
| **Total**                    | **~51**      | Python files      |
