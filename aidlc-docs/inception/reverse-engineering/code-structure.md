# Code Structure

## Build System
- **Type**: Python (hatchling) + Node.js (npm for CDK)
- **Configuration**:
  - `pyproject.toml` - Python project configuration and dependencies
  - `package.json` - CDK dependencies
  - `cdk.json` - CDK application configuration
  - `Makefile` - Developer workflow automation

## Project Structure

```
aws-lambda-handler-cookbook/
├── service/                    # Application code (Python)
│   ├── __init__.py
│   ├── handlers/               # Lambda entry points
│   │   ├── __init__.py
│   │   ├── handle_create_order.py  # Main Lambda handler
│   │   ├── models/             # Handler-specific models
│   │   │   ├── __init__.py
│   │   │   ├── dynamic_configuration.py  # Feature flag names
│   │   │   └── env_vars.py     # Environment variable schemas
│   │   └── utils/              # Handler utilities
│   │       ├── __init__.py
│   │       ├── dynamic_configuration.py  # AppConfig fetching
│   │       ├── observability.py  # Logger, tracer, metrics
│   │       └── rest_api_resolver.py  # API Gateway resolver
│   ├── logic/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── create_order.py     # Order creation logic
│   │   └── utils/
│   │       └── idempotency.py  # Idempotency configuration
│   ├── dal/                    # Data access layer
│   │   ├── __init__.py
│   │   ├── db_handler.py       # Abstract DAL interface
│   │   ├── dynamo_dal_handler.py  # DynamoDB implementation
│   │   └── models/
│   │       ├── __init__.py
│   │       └── db.py           # Database schema (OrderEntry)
│   └── models/                 # Domain models
│       ├── __init__.py
│       ├── exceptions.py       # Custom exceptions
│       ├── input.py            # API input validation
│       ├── order.py            # Core Order model
│       └── output.py           # API response models
├── cdk/                        # Infrastructure (CDK)
│   ├── __init__.py
│   ├── pyproject.toml
│   └── service/
│       ├── __init__.py
│       ├── api_construct.py    # API Gateway + Lambda
│       ├── api_db_construct.py # DynamoDB tables
│       ├── constants.py        # Stack constants
│       ├── monitoring.py       # CloudWatch monitoring
│       ├── service_stack.py    # Main CDK stack
│       ├── utils.py            # CDK utilities
│       ├── waf_construct.py    # WAF configuration
│       └── configuration/
│           ├── __init__.py
│           ├── configuration_construct.py  # AppConfig
│           ├── schema.py       # Configuration schema
│           └── json/           # Configuration JSON files
├── tests/                      # Test suites
│   ├── __init__.py
│   ├── utils.py                # Test utilities
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── infrastructure/         # CDK tests
├── docs/                       # Documentation (MkDocs)
│   └── swagger/
│       └── openapi.json        # Generated OpenAPI spec
├── app.py                      # CDK app entry point
├── pyproject.toml              # Python project config
├── package.json                # NPM dependencies
├── cdk.json                    # CDK configuration
└── Makefile                    # Build automation
```

## Key Classes/Modules

### Service Layer Class Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         HANDLERS LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  handle_create_order.py                                         │
│  ├── create_order() → route handler                            │
│  └── lambda_handler() → entry point                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          LOGIC LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  create_order.py                                                │
│  └── handle_create_order(                                       │
│        order_request: CreateOrderRequest,                       │
│        table_name: str,                                         │
│        context: LambdaContext                                   │
│      ) → CreateOrderOutput                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           DAL LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  db_handler.py                                                  │
│  ├── DalHandler(ABC, Singleton)                                │
│  │   └── create_order_in_db(customer_name, count) → Order      │
│  │                                                              │
│  dynamo_dal_handler.py                                          │
│  └── DynamoDalHandler(DalHandler)                              │
│      └── create_order_in_db() → Order                          │
└─────────────────────────────────────────────────────────────────┘
```

### Existing Files Inventory

#### Handler Files
- `service/handlers/handle_create_order.py` - Lambda handler for POST /api/orders/
- `service/handlers/models/env_vars.py` - Environment variable Pydantic models
- `service/handlers/models/dynamic_configuration.py` - Feature flag configuration models
- `service/handlers/utils/observability.py` - Logger, tracer, metrics setup
- `service/handlers/utils/dynamic_configuration.py` - AppConfig integration
- `service/handlers/utils/rest_api_resolver.py` - API Gateway resolver with Swagger

#### Logic Files
- `service/logic/create_order.py` - Core business logic for order creation
- `service/logic/utils/idempotency.py` - Idempotency configuration

#### DAL Files
- `service/dal/db_handler.py` - Abstract DAL interface (Singleton pattern)
- `service/dal/dynamo_dal_handler.py` - DynamoDB implementation
- `service/dal/models/db.py` - DynamoDB table schema (OrderEntry)

#### Model Files
- `service/models/input.py` - CreateOrderRequest model
- `service/models/output.py` - CreateOrderOutput, InternalServerErrorOutput
- `service/models/order.py` - Order domain model with OrderId type
- `service/models/exceptions.py` - InternalServerException

#### CDK Files
- `app.py` - CDK application entry point
- `cdk/service/service_stack.py` - Main CDK stack
- `cdk/service/api_construct.py` - API Gateway + Lambda construct
- `cdk/service/api_db_construct.py` - DynamoDB tables construct
- `cdk/service/waf_construct.py` - WAF construct
- `cdk/service/monitoring.py` - CloudWatch monitoring construct
- `cdk/service/configuration/configuration_construct.py` - AppConfig construct

## Design Patterns

### Singleton Pattern
- **Location**: `service/dal/db_handler.py`
- **Purpose**: Ensure single instance of DAL handler per Lambda execution context
- **Implementation**: `_SingletonMeta` metaclass with `_instances` dictionary

### Abstract Factory / Repository Pattern
- **Location**: `service/dal/db_handler.py`, `service/dal/dynamo_dal_handler.py`
- **Purpose**: Decouple business logic from database implementation
- **Implementation**: `DalHandler` ABC with `DynamoDalHandler` concrete implementation

### Decorator Pattern
- **Location**: `service/handlers/handle_create_order.py`, `service/logic/create_order.py`
- **Purpose**: Add cross-cutting concerns (observability, idempotency) without modifying core logic
- **Implementation**:
  - `@logger.inject_lambda_context`
  - `@metrics.log_metrics`
  - `@tracer.capture_lambda_handler`
  - `@idempotent`

### 3-Layer Architecture
- **Location**: `service/handlers/`, `service/logic/`, `service/dal/`
- **Purpose**: Separation of concerns
- **Implementation**: Handler → Logic → DAL with clear boundaries

## Critical Dependencies

### AWS Lambda Powertools
- **Version**: ≥3.22.1
- **Usage**: Observability (logging, tracing, metrics), feature flags, idempotency
- **Purpose**: Production-ready Lambda utilities

### Pydantic
- **Version**: ≥2.12.0
- **Usage**: Input validation, environment variables, configuration models
- **Purpose**: Type-safe data validation and serialization

### pydynox
- **Version**: 0.24.0 or higher
- **Usage**: DynamoDB ORM in `service/dal/models/db.py`
- **Purpose**: Pydantic-based DynamoDB table definitions

### boto3
- **Version**: ≥1.26.125
- **Usage**: AWS SDK for DynamoDB, AppConfig
- **Purpose**: AWS service interactions
