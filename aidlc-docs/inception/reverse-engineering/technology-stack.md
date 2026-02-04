# Technology Stack

## Programming Languages

| Language                  | Version | Usage                                    |
| ------------------------- | ------- | ---------------------------------------- |
| **Python**                | 3.14    | Application code, Lambda handlers, tests |
| **TypeScript/JavaScript** | -       | CDK constructs (via aws-cdk-lib)         |

## Frameworks

| Framework                 | Version  | Purpose                                     |
| ------------------------- | -------- | ------------------------------------------- |
| **AWS Lambda Powertools** | ≥3.22.1  | Observability, feature flags, idempotency   |
| **Pydantic**              | ≥2.12.0  | Data validation, serialization, type safety |
| **pydynox**               | 0.24.0   | DynamoDB ORM with Pydantic integration      |
| **AWS CDK**               | ≥2.180.0 | Infrastructure as Code                      |

## Infrastructure (AWS Services)

| Service                | Purpose                                     |
| ---------------------- | ------------------------------------------- |
| **AWS Lambda**         | Serverless compute (Python 3.14, ARM64)     |
| **Amazon API Gateway** | REST API endpoint                           |
| **Amazon DynamoDB**    | NoSQL database (Orders, Idempotency tables) |
| **AWS AppConfig**      | Feature flags and dynamic configuration     |
| **AWS WAF**            | Web Application Firewall (production)       |
| **Amazon CloudWatch**  | Logging, metrics, dashboards, alarms        |
| **AWS X-Ray**          | Distributed tracing                         |
| **AWS SNS**            | Alarm notifications                         |
| **AWS IAM**            | Identity and access management              |

## Build Tools

| Tool           | Version | Purpose                              |
| -------------- | ------- | ------------------------------------ |
| **hatchling**  | -       | Python build backend                 |
| **uv**         | -       | Python package manager (recommended) |
| **npm**        | -       | Node.js package manager for CDK      |
| **Make**       | -       | Build automation (Makefile)          |
| **pre-commit** | -       | Git hooks for code quality           |

## Testing Tools

| Tool            | Version | Purpose             |
| --------------- | ------- | ------------------- |
| **pytest**      | -       | Test framework      |
| **pytest-mock** | -       | Mocking support     |
| **pytest-cov**  | -       | Coverage reporting  |
| **pytest-html** | -       | HTML test reports   |
| **moto**        | -       | AWS service mocking |

## Code Quality Tools

| Tool        | Purpose                  |
| ----------- | ------------------------ |
| **ruff**    | Linting and formatting   |
| **mypy**    | Static type checking     |
| **radon**   | Code complexity analysis |
| **xenon**   | Complexity thresholds    |
| **cdk-nag** | CDK security compliance  |

## Documentation Tools

| Tool                | Purpose                      |
| ------------------- | ---------------------------- |
| **MkDocs**          | Documentation site generator |
| **mkdocs-material** | Material theme for MkDocs    |
| **OpenAPI/Swagger** | API documentation            |

## CI/CD

| Tool               | Purpose                 |
| ------------------ | ----------------------- |
| **GitHub Actions** | CI/CD pipeline          |
| **Codecov**        | Code coverage reporting |

## Runtime Dependencies Summary

```
pydantic>=2.12.0
email-validator
aws-lambda-powertools[tracer]>=3.22.1
pydynox[pydantic]>=0.22.0
cachetools
boto3>=1.26.125
aws-lambda-env-modeler
```

## Development Dependencies Summary

```
aws-cdk-lib>=2.180.0
constructs>=10.0.0
cdk-nag>2.0.0
aws-cdk-aws-lambda-python-alpha>=2.180.0a0
cdk-monitoring-constructs
pytest
pytest-mock
pytest-cov
ruff
mypy
pre-commit
mkdocs-material
```
