---
title: AWS CDK
description: AWS Lambda Cookbook CDK Project
---
## **Prerequisites**

- Follow this [getting started with CDK guide](https://docs.aws.amazon.com/cdk/v1/guide/getting_started.html){:target="_blank" rel="noopener"}
- Make sure your AWS account and machine can deploy an AWS Cloudformation stack and have all the tokens and configuration as described in the page above.
- CDK Best practices [blog](https://ranthebuilder.cloud/blog/aws-cdk-best-practices-from-the-trenches/){:target="_blank" rel="noopener"}
- Lambda layers best practices [blog](https://ranthebuilder.cloud/blog/aws-lambda-layers-best-practices/){:target="_blank" rel="noopener"}

## **CDK Deployment**

```mermaid
flowchart LR
    subgraph AWS["AWS Cloud"]
        subgraph APIGW["API Gateway"]
            REST["REST API<br/>POST /api/orders<br/>GET /api/orders/{id}<br/>GET /api/orders (list)<br/>DELETE /api/orders/{id}"]
        end

        subgraph Security["Security (Production)"]
            WAF["WAF WebACL<br/>AWS Managed Rules"]
        end

        subgraph Compute["Compute"]
            CREATE["Create Order<br/>Lambda Function"]
            GET["Get Order<br/>Lambda Function"]
            DELETE["Delete Order<br/>Lambda Function"]
            LAYER["Lambda Layer<br/>Common Dependencies"]
        end

        subgraph LMI["Lambda Managed Instances (VPC)"]
            LIST_ALIAS["ListOrders Alias: live"]
            LIST["List Orders<br/>Lambda Function"]
            CP["Capacity Provider<br/>EC2 pool, 2 AZs"]
        end

        subgraph Config["Configuration"]
            APPCONFIG["AppConfig<br/>Feature Flags"]
        end

        subgraph Storage["Storage"]
            DDB[("DynamoDB<br/>Orders Table")]
            IDEMPOTENCY[("DynamoDB<br/>Idempotency Table")]
        end
    end

    CLIENT((Client)) --> WAF
    WAF --> REST
    REST --> CREATE
    REST --> GET
    REST --> DELETE
    REST --> LIST_ALIAS
    LIST_ALIAS --> LIST
    LIST -.runs on.-> CP
    CREATE --> LAYER
    GET --> LAYER
    DELETE --> LAYER
    CREATE --> APPCONFIG
    CREATE --> DDB
    CREATE --> IDEMPOTENCY
    GET --> DDB
    DELETE --> DDB
    LIST --> DDB

    style CLIENT fill:#f9f,stroke:#333
    style WAF fill:#ff6b6b,stroke:#333
    style REST fill:#4ecdc4,stroke:#333
    style CREATE fill:#ffe66d,stroke:#333
    style GET fill:#ffe66d,stroke:#333
    style DELETE fill:#ffe66d,stroke:#333
    style LAYER fill:#ffe66d,stroke:#333
    style LIST fill:#ffa500,stroke:#333
    style LIST_ALIAS fill:#4ecdc4,stroke:#333
    style CP fill:#ff6b6b,stroke:#333
    style APPCONFIG fill:#95e1d3,stroke:#333
    style DDB fill:#4a90d9,stroke:#333
    style IDEMPOTENCY fill:#4a90d9,stroke:#333
```

<p class="mermaid-hint">Click diagram to zoom</p>

All CDK project files can be found under the CDK folder.

The CDK code creates an API GW with paths /api/orders (POST) and /api/orders/{order_id} (GET, DELETE), each backed by a dedicated Lambda function.

The AWS Lambda handler uses a Lambda layer optimization which takes all the packages under the [packages] section in the Pipfile and downloads them in via a Docker instance.

This allows you to package any custom dependencies you might have.

In order to add a new dev dependency, add it to the pyproject.toml under the ``[dependency-groups]`` dev section and run ``uv lock && uv sync``.

In order to add a new Lambda runtime dependency, add it to the pyproject.toml under the ``[project]`` dependencies section and run ``uv lock && uv sync``.

### **CDK Constants**

All AWS Lambda function configurations are saved as constants at the `cdk.service.constants.py` file and can easily be changed.

- Memory size
- Timeout in seconds
- Lambda dependencies build folder location
- Lambda Layer dependencies build folder location
- Various resources names
- Lambda function environment variables names and values

### **Deployed Resources**

- AWS Cloudformation stack: **cdk.service.service_stack.py** which is consisted of one construct
- Construct: **cdk.service.api_construct.py** which includes:
    - **Lambda Layer** - deployment optimization meant to be used with multiple handlers under the same API GW, sharing code logic and dependencies. You can read more in [my blog post on Lambda layers best practices](https://ranthebuilder.cloud/blog/aws-lambda-layers-best-practices/){:target="_blank" rel="noopener"}.
    - **Lambda Functions** - Four Lambda handler functions for create, get, delete, and list order operations. Handler code is taken from the service `folder`.
    - **Lambda Roles** - Dedicated least-privilege IAM roles for each Lambda function.
    - **API GW with Lambda Integrations** - API GW with Lambda integrations: POST /api/orders (create), GET /api/orders/{order_id} (get), DELETE /api/orders/{order_id} (delete), and GET /api/orders/ (list, served via an alias over a Lambda Managed Instances capacity provider).
    - **Lambda Managed Instances Construct** - `cdk.service.lambda_managed_instance_construct.py` provisions the VPC, private subnets across two AZs, security group, DynamoDB gateway endpoint, Logs and X-Ray interface endpoints, IAM operator role, and the `AWS::Lambda::CapacityProvider` for LIST. See the [deep-dive](best_practices/managed_instances.md).
    - **AWS DynamoDB table** - stores request data. Created in the `api_db_construct.py` construct.
    - **AWS DynamoDB table** - stores idempotency data. Created in the `api_db_construct.py` construct.
- Construct: **cdk.service.configuration.configuration_construct.py** which includes:
    - AWS AppConfig configuration with an environment, application, configuration and deployment strategy. You can read more in the [dynamic configuration documentation](best_practices/dynamic_configuration.md).

### **Infrastructure CDK & Security Tests**

Under tests there is an `infrastructure` folder for CDK infrastructure tests.

The first test, `test_cdk` uses CDK's testing framework which asserts that required resources exists so the application will not break anything upon deployment.

The security tests are based on `cdk_nag`. It checks your cloudformation output for security best practices. It can be found in the `service_stack.py` as part of the stack definition. It will fail the deployment when there is a security issue.

For more information see the [AWS CDK-Nag documentation](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/check-aws-cdk-applications-or-cloudformation-templates-for-best-practices-by-using-cdk-nag-rule-packs.html){:target="_blank" rel="noopener"}.
