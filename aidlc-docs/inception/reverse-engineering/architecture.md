# System Architecture

## System Overview

The AWS Lambda Handler Cookbook is a **production-ready serverless order management service** built on AWS. It demonstrates best practices for:
- 3-layer architecture (Handler → Logic → DAL)
- Observability (logging, tracing, metrics)
- Security (WAF, IAM, input validation)
- Infrastructure as Code (AWS CDK)
- Feature flags and dynamic configuration

## Architecture Diagram

```
                                         ┌──────────────┐
                                         │   AWS WAF    │
                                         │ (Production) │
                                         └──────┬───────┘
                                                │
    ┌─────────────┐     POST /api/orders    ┌───▼───────────┐
    │   Client    │ ──────────────────────► │  API Gateway  │
    │  (Browser/  │ ◄────────────────────── │  (REST API)   │
    │    App)     │       Response          │ Rate: 2 req/s │
    └─────────────┘                         └───────┬───────┘
                                                    │
                                            ┌───────▼───────┐
                                            │    Lambda     │
                                            │ CreateOrder   │
                                            │  (Python 3.14)│
                                            │  ARM64, 128MB │
                                            └───────┬───────┘
                     ┌──────────────────────────────┼──────────────────────────┐
                     │                              │                          │
             ┌───────▼───────┐              ┌───────▼───────┐          ┌───────▼───────┐
             │   AppConfig   │              │   DynamoDB    │          │   DynamoDB    │
             │ Feature Flags │              │    Orders     │          │  Idempotency  │
             │ Configuration │              │    Table      │          │    Table      │
             └───────────────┘              └───────────────┘          └───────────────┘
```

## Component Descriptions

### service/ - Application Package
- **Purpose**: Core business logic for order management
- **Responsibilities**:
  - HTTP request handling
  - Input validation
  - Business logic execution
  - Database operations
- **Dependencies**: AWS Lambda Powertools, Pydantic, pydynox, boto3
- **Type**: Application

### cdk/service/ - Infrastructure Package
- **Purpose**: AWS CDK infrastructure definitions
- **Responsibilities**:
  - Define AWS resources (API Gateway, Lambda, DynamoDB)
  - Configure security (WAF, IAM roles)
  - Set up monitoring (CloudWatch dashboards, alarms)
  - Manage AppConfig feature flags
- **Dependencies**: aws-cdk-lib, cdk-nag, cdk-monitoring-constructs
- **Type**: Infrastructure

### tests/ - Test Package
- **Purpose**: Quality assurance and verification
- **Responsibilities**:
  - Unit tests for models and validation
  - Integration tests with mocked AWS services
  - E2E tests against deployed infrastructure
  - Infrastructure compliance tests
- **Dependencies**: pytest, moto, pytest-mock
- **Type**: Test

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Create Order Flow                                   │
└──────────────────────────────────────────────────────────────────────────────┘

Client                API Gateway         Lambda Handler         Logic            DAL           DynamoDB
  │                        │                    │                  │               │                │
  │  POST /api/orders/     │                    │                  │               │                │
  │ {name, item_count}     │                    │                  │               │                │
  │───────────────────────►│                    │                  │               │                │
  │                        │  Lambda Invoke     │                  │               │                │
  │                        │───────────────────►│                  │               │                │
  │                        │                    │                  │               │                │
  │                        │                    │ @tracer          │               │                │
  │                        │                    │ @logger          │               │                │
  │                        │                    │ @metrics         │               │                │
  │                        │                    │                  │               │                │
  │                        │                    │  Validate Input  │               │                │
  │                        │                    │─────────────────►│               │                │
  │                        │                    │                  │               │                │
  │                        │                    │                  │ @idempotent   │                │
  │                        │                    │                  │───────────────►               │
  │                        │                    │                  │               │  Check Key    │
  │                        │                    │                  │               │──────────────►│
  │                        │                    │                  │               │               │
  │                        │                    │                  │ Check Flags   │               │
  │                        │                    │                  │ (AppConfig)   │               │
  │                        │                    │                  │               │               │
  │                        │                    │                  │ create_order  │               │
  │                        │                    │                  │───────────────►               │
  │                        │                    │                  │               │  PutItem      │
  │                        │                    │                  │               │──────────────►│
  │                        │                    │                  │               │               │
  │                        │                    │  Return Order    │               │               │
  │                        │◄──────────────────────────────────────│               │               │
  │  200 OK {id, name,     │                    │                  │               │               │
  │          item_count}   │                    │                  │               │               │
  │◄───────────────────────│                    │                  │               │               │
```

## Integration Points

### External APIs
- **AWS AppConfig**: Feature flags and dynamic configuration
- **AWS CloudWatch**: Metrics, logs, and dashboards
- **AWS X-Ray**: Distributed tracing
- **AWS SNS**: Alarm notifications

### Databases
- **DynamoDB - Orders Table**: Primary storage for orders (id, name, item_count, created_at)
- **DynamoDB - Idempotency Table**: Tracks request idempotency keys with TTL

### Third-party Services
- None (fully self-contained AWS service)

## Infrastructure Components

### CDK Stacks

| Stack            | Purpose                                 |
| ---------------- | --------------------------------------- |
| **ServiceStack** | Main stack orchestrating all constructs |

### CDK Constructs

| Construct                  | Purpose                                                      |
| -------------------------- | ------------------------------------------------------------ |
| **ConfigurationConstruct** | AppConfig application, environment, and hosted configuration |
| **ApiConstruct**           | API Gateway, Lambda function, Lambda layer                   |
| **ApiDbConstruct**         | DynamoDB tables (Orders, Idempotency)                        |
| **WafConstruct**           | Web Application Firewall (production only)                   |
| **Monitoring**             | CloudWatch dashboards and alarms                             |

### Deployment Model
- **Single Region**: Deployed to one AWS region
- **Environment-based**: Different configurations for dev/staging/prod
- **WAF**: Only enabled in production environment
- **CI/CD**: GitHub Actions workflow

### Security
- **WAF Rules** (Production):
  - AWSManagedRulesCommonRuleSet
  - AWSManagedRulesAmazonIpReputationList
  - AWSManagedRulesAnonymousIpList
  - AWSManagedRulesKnownBadInputsRuleSet
- **IAM**: Least privilege roles for Lambda
- **cdk-nag**: AwsSolutionsChecks for compliance
- **Input Validation**: Pydantic models with strict typing
