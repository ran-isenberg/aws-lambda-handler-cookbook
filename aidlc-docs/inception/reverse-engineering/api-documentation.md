# API Documentation

## REST APIs

### Create Order Endpoint

| Property           | Value                               |
| ------------------ | ----------------------------------- |
| **Method**         | POST                                |
| **Path**           | `/api/orders/`                      |
| **Purpose**        | Create a new customer order         |
| **Authentication** | None (WAF protection in production) |
| **Rate Limit**     | 2 requests/second, burst 10         |

#### Request Format

**Content-Type**: `application/json`

```json
{
  "customer_name": "string",
  "order_item_count": 1
}
```

**Request Schema** (from `service/models/input.py`):

| Field              | Type    | Required | Validation                          |
| ------------------ | ------- | -------- | ----------------------------------- |
| `customer_name`    | string  | Yes      | 1-20 characters                     |
| `order_item_count` | integer | Yes      | Positive integer (> 0), strict mode |

#### Response Format

**Success Response (200 OK)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "RanTheBuilder",
  "item_count": 5
}
```

**Response Schema** (from `service/models/output.py`):

| Field        | Type          | Description                           |
| ------------ | ------------- | ------------------------------------- |
| `id`         | string (UUID) | Unique order identifier               |
| `name`       | string        | Customer name (echoed from request)   |
| `item_count` | integer       | Number of items (echoed from request) |

**Validation Error Response (422 Unprocessable Entity)**:

```json
{
  "statusCode": 422,
  "detail": [
    {
      "loc": ["body", "customer_name"],
      "msg": "String should have at most 20 characters",
      "type": "string_too_long"
    }
  ]
}
```

**Internal Server Error Response (501)**:

```json
{
  "error": "internal server error"
}
```

### Swagger Documentation Endpoint

| Property    | Value                            |
| ----------- | -------------------------------- |
| **Method**  | GET                              |
| **Path**    | `/swagger`                       |
| **Purpose** | OpenAPI/Swagger UI documentation |

---

## Internal APIs

### DalHandler Interface

**Location**: `service/dal/db_handler.py`

```python
class DalHandler(ABC, metaclass=_SingletonMeta):
    @abstractmethod
    def create_order_in_db(
        self,
        customer_name: str,
        order_item_count: int
    ) -> Order:
        """
        Create an order in the database.

        Parameters:
            customer_name: Customer's name (1-20 chars)
            order_item_count: Number of items (positive int)

        Returns:
            Order: Created order with generated UUID

        Raises:
            InternalServerException: On database errors
        """
```

### Business Logic Interface

**Location**: `service/logic/create_order.py`

```python
@idempotent(
    persistence_store=persistence_layer,
    config=idempotency_config,
)
def handle_create_order(
    order_request: CreateOrderRequest,
    table_name: str,
    context: LambdaContext,
) -> CreateOrderOutput:
    """
    Handle order creation with idempotency.

    Parameters:
        order_request: Validated input from API
        table_name: DynamoDB table name
        context: Lambda execution context

    Returns:
        CreateOrderOutput: Created order details

    Features:
        - Idempotent (5-minute window)
        - Feature flag evaluation
        - Metrics emission
    """
```

### Configuration Interface

**Location**: `service/handlers/utils/dynamic_configuration.py`

```python
def get_configuration_store() -> FeatureFlags:
    """
    Get singleton AppConfig feature flags store.

    Returns:
        FeatureFlags: AWS Lambda Powertools FeatureFlags instance
    """

def parse_configuration(conf: dict) -> MyConfiguration:
    """
    Parse AppConfig JSON into typed configuration.

    Parameters:
        conf: Raw configuration dictionary

    Returns:
        MyConfiguration: Validated configuration object

    Raises:
        ConfigurationException: On parsing failures
    """
```

---

## Data Models

### CreateOrderRequest

**Location**: `service/models/input.py`

| Field              | Type        | Validation                  | Description     |
| ------------------ | ----------- | --------------------------- | --------------- |
| `customer_name`    | str         | min_length=1, max_length=20 | Customer's name |
| `order_item_count` | PositiveInt | strict=True, gt=0           | Number of items |

### Order

**Location**: `service/models/order.py`

| Field        | Type           | Description       |
| ------------ | -------------- | ----------------- |
| `name`       | str            | Customer name     |
| `item_count` | int            | Number of items   |
| `id`         | OrderId (UUID) | Unique identifier |

**OrderId Type**: `Annotated[str, AfterValidator(validate_uuid_id)]`

### CreateOrderOutput

**Location**: `service/models/output.py`

Extends `Order` - same fields for API response.

### OrderEntry (Database Schema)

**Location**: `service/dal/models/db.py`

| Field        | Type        | DynamoDB Type | Description    |
| ------------ | ----------- | ------------- | -------------- |
| `id`         | OrderId     | S (String)    | Primary key    |
| `name`       | str         | S             | Customer name  |
| `item_count` | PositiveInt | N             | Item count     |
| `created_at` | PositiveInt | N             | Unix timestamp |

### Environment Variable Models

**Location**: `service/handlers/models/env_vars.py`

| Model                  | Variables                                                                               | Purpose                        |
| ---------------------- | --------------------------------------------------------------------------------------- | ------------------------------ |
| `Observability`        | POWERTOOLS_SERVICE_NAME, POWERTOOLS_METRICS_NAMESPACE, LOG_LEVEL                        | Logging/tracing config         |
| `Idempotency`          | IDEMPOTENCY_TABLE_NAME                                                                  | DynamoDB table for idempotency |
| `DynamicConfiguration` | CONFIGURATION_APP, CONFIGURATION_ENV, CONFIGURATION_NAME, CONFIGURATION_MAX_AGE_MINUTES | AppConfig settings             |

### Feature Flag Configuration

**Location**: `service/handlers/models/dynamic_configuration.py`

| Flag                       | Type | Purpose                      |
| -------------------------- | ---- | ---------------------------- |
| `premium_features`         | bool | Enable premium user features |
| `ten_percent_off_campaign` | bool | Enable 10% discount campaign |

---

## Error Handling

### Custom Exceptions

| Exception                 | HTTP Code | Description                 |
| ------------------------- | --------- | --------------------------- |
| `InternalServerException` | 501       | Database or internal errors |
| `ConfigurationException`  | 501       | AppConfig fetch failures    |

### Exception Handler Flow

```
RequestValidationError → 422 Unprocessable Entity
InternalServerException → 501 Internal Server Error
ConfigurationException → 501 Internal Server Error
```
