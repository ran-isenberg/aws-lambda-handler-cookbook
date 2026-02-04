# Dependencies

## Internal Dependencies Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Internal Package Dependencies                         │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │      service.handlers           │
                    │   (handle_create_order.py)      │
                    └─────────────────┬───────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ service.handlers.   │  │   service.logic     │  │   service.models    │
│      utils          │  │  (create_order.py)  │  │    (input.py)       │
│ (observability.py)  │  └──────────┬──────────┘  │   (output.py)       │
│ (rest_api_resolver) │             │             └─────────────────────┘
│ (dynamic_config)    │             │
└─────────────────────┘             │
                                    ▼
                         ┌─────────────────────┐
                         │     service.dal     │
                         │ (dynamo_dal_handler)│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  service.dal.models │
                         │      (db.py)        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   service.models    │
                         │    (order.py)       │
                         └─────────────────────┘
```

## Internal Dependencies Detail

### service.handlers → service.logic
- **Type**: Runtime
- **Reason**: Handler delegates business logic to logic layer

### service.handlers → service.models
- **Type**: Runtime
- **Reason**: Uses CreateOrderRequest for input validation

### service.handlers → service.handlers.utils
- **Type**: Runtime
- **Reason**: Uses observability (logger, tracer, metrics), API resolver, dynamic configuration

### service.logic → service.dal
- **Type**: Runtime
- **Reason**: Logic layer uses DAL for database operations

### service.logic → service.models
- **Type**: Runtime
- **Reason**: Uses CreateOrderOutput for response formatting

### service.dal → service.dal.models
- **Type**: Runtime
- **Reason**: DAL uses OrderEntry schema for DynamoDB operations

### service.dal.models → service.models
- **Type**: Runtime
- **Reason**: OrderEntry uses OrderId type from service.models

### tests → service
- **Type**: Test
- **Reason**: All test packages import service code for testing

## External Dependencies

### AWS Lambda Powertools
- **Version**: ≥3.22.1
- **Purpose**: Production-ready Lambda utilities
- **Usage Locations**:
  - `service/handlers/utils/observability.py` - Logger, Tracer, Metrics
  - `service/handlers/utils/dynamic_configuration.py` - FeatureFlags
  - `service/logic/create_order.py` - Idempotency
  - `service/handlers/utils/rest_api_resolver.py` - APIGatewayRestResolver
- **License**: MIT-0

### Pydantic
- **Version**: ≥2.12.0
- **Purpose**: Data validation and serialization
- **Usage Locations**:
  - `service/models/*.py` - All domain models
  - `service/handlers/models/*.py` - Environment and configuration models
  - `service/dal/models/db.py` - Database schema
- **License**: MIT

### pydynox
- **Version**: 0.24.0 or higher
- **Purpose**: DynamoDB ORM with Pydantic
- **Usage Locations**:
  - `service/dal/models/db.py` - OrderEntry table definition
- **License**: MIT

### boto3
- **Version**: ≥1.26.125
- **Purpose**: AWS SDK for Python
- **Usage Locations**:
  - `service/dal/dynamo_dal_handler.py` - DynamoDB operations
  - `service/handlers/utils/dynamic_configuration.py` - AppConfig
- **License**: Apache-2.0

### aws-lambda-env-modeler
- **Version**: Latest
- **Purpose**: Environment variable validation
- **Usage Locations**:
  - `service/handlers/models/env_vars.py` - Init decorators
- **License**: MIT

### cachetools
- **Version**: Latest
- **Purpose**: Caching utilities
- **Usage Locations**:
  - `service/handlers/utils/dynamic_configuration.py` - Configuration caching
- **License**: MIT

### email-validator
- **Version**: Latest
- **Purpose**: Email validation for Pydantic
- **Usage Locations**:
  - Transitive dependency via Pydantic
- **License**: CC0

## CDK Dependencies

### aws-cdk-lib
- **Version**: ≥2.180.0
- **Purpose**: CDK core library
- **License**: Apache-2.0

### cdk-nag
- **Version**: >2.0.0
- **Purpose**: Security and compliance checks
- **License**: Apache-2.0

### cdk-monitoring-constructs
- **Version**: Latest
- **Purpose**: CloudWatch dashboards and alarms
- **License**: Apache-2.0

### aws-cdk-aws-lambda-python-alpha
- **Version**: ≥2.180.0a0
- **Purpose**: Python Lambda bundling
- **License**: Apache-2.0

## Dependency Graph (Simplified)

```
aws-lambda-handler-cookbook
├── Runtime
│   ├── pydantic >= 2.12.0
│   │   └── email-validator
│   ├── aws-lambda-powertools[tracer] >= 3.22.1
│   ├── pydynox[pydantic] == 0.24.0
│   ├── cachetools
│   ├── boto3 >= 1.26.125
│   └── aws-lambda-env-modeler
└── Development
    ├── aws-cdk-lib >= 2.180.0
    │   └── constructs >= 10.0.0
    ├── cdk-nag > 2.0.0
    ├── cdk-monitoring-constructs
    ├── pytest
    │   ├── pytest-mock
    │   ├── pytest-cov
    │   └── pytest-html
    ├── ruff
    ├── mypy
    ├── pre-commit
    └── mkdocs-material
```
