# AWS Lambda Handler Cookbook (Python)

[![license](https://img.shields.io/github/license/ran-isenberg/aws-lambda-handler-cookbook)](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/master/LICENSE)
![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.14&color=blue?style=flat-square&logo=python)
[![codecov](https://codecov.io/github/ran-isenberg/aws-lambda-handler-cookbook/graph/badge.svg?token=P2K7K4KICF)](https://codecov.io/github/ran-isenberg/aws-lambda-handler-cookbook)
![version](https://img.shields.io/github/v/release/ran-isenberg/aws-lambda-handler-cookbook)
![github-star-badge](https://img.shields.io/github/stars/ran-isenberg/aws-lambda-handler-cookbook.svg?style=social)
![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/ran-isenberg/aws-lambda-handler-cookbook/badge)
![issues](https://img.shields.io/github/issues/ran-isenberg/aws-lambda-handler-cookbook)

![alt text](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/docs/media/banner.png?raw=true)

This project provides a working, open source based, AWS Lambda handler skeleton Python code includingx DEPLOYMENT code with CDK and a pipeline.

This project can serve as a blueprint for new Serverless services - CDK deployment code, pipeline and handler are covered.

**[📜Documentation](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/)** | **[Blogs website](https://ranthebuilder.cloud/)**
> **Contact details | mailto:ran.isenberg@ranthebuilder.cloud**

[![Twitter Follow](https://img.shields.io/twitter/follow/IsenbergRan?label=Follow&style=social)](https://twitter.com/RanBuilder)
[![Website](https://img.shields.io/badge/Website-www.ranthebuilder.cloud-blue)](https://ranthebuilder.cloud/)

## AWS Recommendation

This repository was recommended in an AWS blog post [Best practices for accelerating development with serverless blueprints](https://aws.amazon.com/blogs/infrastructure-and-automation/best-practices-for-accelerating-development-with-serverless-blueprints/)

![aws_article](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/docs/media/article.png?raw=true)

## Concepts

I spoke at AWS re:invent 2023 with Heitor Lessa, former Chief Architect of Powertools for AWS Lambda about the concepts I implemented in this project.

[![Watch the video](https://img.youtube.com/vi/52W3Qyg242Y/maxresdefault.jpg)](https://www.youtube.com/watch?v=52W3Qyg242Y)

## Getting Started

You can start with a clean service out of this blueprint repository without using the 'Template' button on GitHub.

You can use Cookiecutter.

* Cookiecutter - install with pip/brew ``brew install cookiecutter`` or ``pip install cookiecutter``

Then run:

```bash
cookiecutter gh:ran-isenberg/cookiecutter-serverless-python
```

Answer the questions to select repo name, service name, etc.:

![logo](https://github.com/ran-isenberg/cookiecutter-serverless-python/blob/main/media/howto.png?raw=true)

**That's it, your developer environment has been set! you are ready to deploy the service:**

```bash
cd {new repo folder}
uv sync
make deploy
```

Make sure you have [uv](https://docs.astral.sh/uv/) installed.

You can also run 'make pr' will run all checks, synth, file formatters , unit tests, deploy to AWS and run integration and E2E tests.

## **The Problem**

Starting a Serverless service can be overwhelming. You need to figure out many questions and challenges that have nothing to do with your business domain:

* How to deploy to the cloud? What IAC framework do you choose?
* How to write a SaaS-oriented CI/CD pipeline? What does it need to contain?
* How do you handle observability, logging, tracing, metrics?
* How do you write a Lambda function?
* How do you handle testing?
* What makes an AWS Lambda handler resilient, traceable, and easy to maintain? How do you write such a code?

## **The Solution**

This project aims to reduce cognitive load and answer these questions for you by providing a skeleton Python Serverless service blueprint that implements best practices for AWS Lambda, Serverless CI/CD, and AWS CDK in one blueprint project.

### Serverless Service - The Order service

* This project provides a working orders service where customers can create, get, and delete orders of items.

* The project deploys an API GW with AWS Lambda integrations and stores data in a DynamoDB table:
    * `POST /api/orders/` - Create a new order
    * `GET /api/orders/{order_id}` - Get an order by ID
    * `DELETE /api/orders/{order_id}` - Delete an order by ID
    * `GET /api/orders/?limit={n}&next_token={cursor}` - List orders with pagination, served by an **AWS Lambda Managed Instances** pool

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

#### **LIST orders via AWS Lambda Managed Instances**

The `GET /api/orders/` endpoint is deliberately powered by
[AWS Lambda Managed Instances](https://aws.amazon.com/blogs/aws/introducing-aws-lambda-managed-instances-serverless-simplicity-with-ec2-flexibility/)
(LMI) rather than standard Lambda. LMI maintains a warm pool of execution
environments on an EC2-backed capacity provider, so paginated list traffic
avoids cold starts, runs inside a private VPC with DynamoDB and observability
VPC endpoints, and can cap concurrency per environment (useful for bounding
DynamoDB Scan pressure). The CRUD endpoints stay on standard Lambda — LMI is
picked per-function, only where its extra surface area pays off.

See the
[Lambda Managed Instances deep-dive](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/best_practices/managed_instances/)
for tuning knobs (memory-to-vCPU ratio, min/max environments, per-env
concurrency), the matching CDK construct, and the gotchas around version
publishing and memory/CPU constraints.

#### **Monitoring Design**

```mermaid
flowchart TB
    subgraph Monitoring["CloudWatch Monitoring"]
        subgraph Dashboards["Dashboards"]
            HL["High-Level Dashboard<br/>API Gateway Metrics<br/>Business KPIs"]
            LL["Low-Level Dashboard<br/>Lambda Metrics<br/>DynamoDB Metrics"]
        end

        subgraph Alarms["CloudWatch Alarms"]
            API_ALARM["API Gateway Alarms<br/>5XX Errors, Latency"]
            LAMBDA_ALARM["Lambda Alarms<br/>Errors, P90 Latency"]
            DDB_ALARM["DynamoDB Alarms<br/>Throttles, Errors"]
        end
    end

    subgraph Notification["Notification"]
        SNS["SNS Topic<br/>KMS Encrypted"]
    end

    subgraph Resources["Monitored Resources"]
        APIGW["API Gateway"]
        LAMBDA["Lambda Function"]
        DDB["DynamoDB Tables"]
    end

    APIGW --> API_ALARM
    LAMBDA --> LAMBDA_ALARM
    DDB --> DDB_ALARM

    API_ALARM --> SNS
    LAMBDA_ALARM --> SNS
    DDB_ALARM --> SNS

    API_ALARM --> HL
    LAMBDA_ALARM --> LL
    DDB_ALARM --> LL

    style HL fill:#4ecdc4,stroke:#333
    style LL fill:#4ecdc4,stroke:#333
    style SNS fill:#ff6b6b,stroke:#333
    style API_ALARM fill:#ffe66d,stroke:#333
    style LAMBDA_ALARM fill:#ffe66d,stroke:#333
    style DDB_ALARM fill:#ffe66d,stroke:#333
```

### **Features**

* Python Serverless service with a recommended file structure.
* CDK infrastructure with infrastructure tests and security tests.
* CI/CD pipelines based on Github actions that deploys to AWS with python linters, complexity checks and style formatters.
* CI/CD pipeline deploys to dev/staging and production environments with different gates between each environment
* Automatic GitHub releases with semantic versioning based on conventional commits
* Automatic PR labeling based on commit message prefixes (feat, fix, docs, chore)
* Makefile for simple developer experience.
* The AWS Lambda handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.
* AWS Lambda handler uses [AWS Lambda Powertools](https://docs.powertools.aws.dev/lambda-python/).
* AWS Lambda handler 3 layer architecture: handler layer, logic layer and data access layer
* Features flags and configuration based on AWS AppConfig
* Idempotent API
* REST API protected by WAF with four AWS managed rules in production deployment
* CloudWatch dashboards - High level and low level including CloudWatch alarms
* Unit, infrastructure, security, integration and end to end tests.
* Automatically generated OpenAPI endpoint: /swagger with Pydantic schemas for both requests and responses
* CI swagger protection - fails the PR if your swagger JSON file (stored at docs/swagger/openapi.json) is out of date
* Automated protection against API breaking changes
* AWS Lambda Managed Instances pool powers the paginated LIST endpoint (VPC, capacity provider, warm environments)

## CDK Deployment

The CDK code creates an API GW with paths /api/orders (POST) and /api/orders/{order_id} (GET, DELETE), each backed by a dedicated Lambda function.

The AWS Lambda handler uses a Lambda layer optimization which takes all the packages under the [packages] section in the Pipfile and downloads them in via a Docker instance.

This allows you to package any custom dependencies you might have, just add them to the Pipfile under the [packages] section.

## Serverless Best Practices

The AWS Lambda handler will implement multiple best practice utilities.

Each utility is implemented when a new blog post is published about that utility.

The utilities cover multiple aspect of a production-ready service, including:

* [Logging](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-elevate-your-handler-s-code-part-1-logging/)
* [Observability: Monitoring and Tracing](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-elevate-your-handler-s-code-part-2-observability/)
* [Observability: Business KPIs Metrics](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-elevate-your-handler-s-code-part-3-business-domain-observability/)
* [Environment Variables](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-environment-variables/)
* [Input Validation](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-elevate-your-handler-s-code-part-5-input-validation/)
* [Dynamic Configuration & feature flags](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-part-6-feature-flags-configuration-best-practices/)
* [Start Your AWS Serverless Service With Two Clicks](https://ranthebuilder.cloud/blog/aws-lambda-cookbook-part-7-how-to-use-the-aws-lambda-cookbook-github-template-project/)
* [CDK Best practices](https://ranthebuilder.cloud/blog/aws-cdk-best-practices-from-the-trenches/)
* [Serverless Monitoring](https://ranthebuilder.cloud/blog/how-to-effortlessly-monitor-serverless-applications-with-cloudwatch-part-one/)
* [API Idempotency](https://ranthebuilder.cloud/blog/serverless-api-idempotency-with-aws-lambda-powertools-and-cdk/)
* [Serverless OpenAPI Documentation with AWS Powertools](https://ranthebuilder.cloud/blog/serverless-open-api-documentation-with-aws-powertools/)

## Getting started

Head over to the complete project documentation pages at GitHub pages at [https://ran-isenberg.github.io/aws-lambda-handler-cookbook](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/)

## Code Contributions

Code contributions are welcomed. Read this [guide.](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/CONTRIBUTING.md)

## Code of Conduct

Read our code of conduct [here.](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/CODE_OF_CONDUCT.md)

## Connect

- Email: ran.isenberg@ranthebuilder.cloud
- Blog: https://ranthebuilder.cloud/
- Bluesky: [@ranthebuilder.cloud](https://bsky.app/profile/ranthebuilder.cloud)
- X:       [@RanBuilder](https://twitter.com/RanBuilder)
- LinkedIn: https://www.linkedin.com/in/ranbuilder/

## AI-Assisted Development

This project uses [AI-DLC (AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows) for AI-assisted software development. Learn more about AI-DLC in this [blog post](https://ranthebuilder.cloud/blog/ai-driven-sdlc/).

AI-DLC provides a structured, adaptive workflow for:

* **Requirements Analysis** - Intelligent requirements gathering and clarification
* **Architecture Design** - AI-assisted architectural decisions
* **Code Generation** - Structured code implementation with best practices
* **Testing** - Comprehensive test generation and validation

The AI-DLC workflow artifacts are stored in the `aidlc-docs/` directory.

## Credits

* [AWS Lambda Powertools (Python)](https://github.com/aws-powertools/powertools-lambda-python)
* [AI-DLC Workflows](https://github.com/awslabs/aidlc-workflows)

## License

This library is licensed under the MIT License. See the [LICENSE](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/LICENSE) file.

Copyright (c) 2026 Ran Isenberg
