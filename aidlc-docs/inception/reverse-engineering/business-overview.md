# Business Overview

## Business Context Diagram

```
                    ┌────────────────────────────────────────────┐
                    │           Order Management System           │
                    │     (AWS Lambda Handler Cookbook)           │
                    └────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
            │   Customer    │   │   Feature     │   │   Campaign    │
            │   Orders      │   │   Management  │   │   Discounts   │
            └───────────────┘   └───────────────┘   └───────────────┘
```

## Business Description

- **Business Description**: This system is an **AWS Lambda serverless blueprint** that implements a simple **Order Management Service**. Customers can create orders specifying their name and the number of items they want to purchase. The system validates inputs, processes orders through a 3-layer architecture (Handler → Logic → DAL), and persists them in DynamoDB. It serves as a production-ready template demonstrating best practices for building serverless applications on AWS.

- **Business Transactions**:

| Transaction      | Description                                                                                                                                                                                                                 | Endpoint            | Actor    |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | -------- |
| **Create Order** | A customer creates a new order by providing their name and item count. The system validates the input, checks for applicable discounts via feature flags, creates an order with a unique ID, and stores it in the database. | `POST /api/orders/` | Customer |

- **Business Dictionary**:

| Term                 | Definition                                                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Order**            | A customer transaction representing a purchase request containing customer name, item count, and a unique identifier (UUID) |
| **Customer Name**    | A string identifier (1-20 characters) for the customer placing the order                                                    |
| **Order Item Count** | A positive integer representing the number of items in the order                                                            |
| **Premium User**     | A customer that qualifies for special discounts based on feature flag rules evaluated against their customer name           |
| **Campaign**         | A promotional discount (e.g., "10% off campaign") controlled by feature flags in AWS AppConfig                              |
| **Idempotency**      | Ensures that duplicate order requests (within 5 minutes) return the same order without creating duplicates                  |
| **Feature Flag**     | A dynamic configuration toggle (via AWS AppConfig) that controls business features without code deployment                  |

## Component Level Business Descriptions

### service/ - Application Code
- **Purpose**: Contains the core business logic for order management
- **Responsibilities**:
  - Handle incoming API requests
  - Validate customer input
  - Apply business rules (discounts, premium features)
  - Persist orders to database
  - Return order confirmation to customers

### cdk/ - Infrastructure Code
- **Purpose**: Defines all AWS resources needed to run the order service
- **Responsibilities**:
  - Provision API Gateway, Lambda, DynamoDB
  - Configure security (WAF, IAM)
  - Set up monitoring and alerting
  - Manage feature flag configuration

### tests/ - Quality Assurance
- **Purpose**: Ensures system reliability and correctness
- **Responsibilities**:
  - Validate input/output contracts
  - Test business logic in isolation
  - Verify end-to-end order flow
  - Validate infrastructure compliance
