---
title: Homepage
description: AWS Lambda Handler Cookbook - a Serverless Service Blueprint
---
## **AWS Lambda Handler Cookbook - A Serverless Service Blueprint**

[<img alt="AWS Lambda Handler Cookbook" src="./media/banner.png" />](https://www.ranthebuilder.cloud/)

## AWS Recommendation

This repository was recommended in an AWS blog post [Best practices for accelerating development with serverless blueprints](https://aws.amazon.com/blogs/infrastructure-and-automation/best-practices-for-accelerating-development-with-serverless-blueprints/){:target="_blank" rel="noopener"}

<img alt="aws article" src="./media/article.png" />

## Concepts

I spoke at AWS re:invent 2023 with Heitor Lessa, former Chief Architect of Powertools for AWS Lambda about the concepts I implemented in this project.

<iframe width="560" height="315" src="https://www.youtube.com/embed/52W3Qyg242Y" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## **The Problem**

Starting a Serverless service can be overwhelming. You need to figure out many questions and challenges that have nothing to do with your business domain:

- How to deploy to the cloud? What IAC framework do you choose?
- How to write a SaaS-oriented CI/CD pipeline? What does it need to contain?
- How do you handle observability, logging, tracing, metrics?
- How do you handle testing?

## **The Solution**

This project aims to reduce cognitive load and answer these questions for you by providing a skeleton Python Serverless service blueprint that implements best practices for AWS Lambda, Serverless CI/CD, and AWS CDK in one blueprint project.

### Serverless Service - The Order service

```mermaid
flowchart LR
    subgraph AWS["AWS Cloud"]
        subgraph APIGW["API Gateway"]
            REST["REST API<br/>POST /api/orders"]
        end

        subgraph Security["Security (Production)"]
            WAF["WAF WebACL<br/>AWS Managed Rules"]
        end

        subgraph Compute["Compute"]
            LAMBDA["Lambda Function<br/>Python 3.14"]
            LAYER["Lambda Layer<br/>Common Dependencies"]
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
    REST --> LAMBDA
    LAMBDA --> LAYER
    LAMBDA --> APPCONFIG
    LAMBDA --> DDB
    LAMBDA --> IDEMPOTENCY

    style CLIENT fill:#f9f,stroke:#333
    style WAF fill:#ff6b6b,stroke:#333
    style REST fill:#4ecdc4,stroke:#333
    style LAMBDA fill:#ffe66d,stroke:#333
    style LAYER fill:#ffe66d,stroke:#333
    style APPCONFIG fill:#95e1d3,stroke:#333
    style DDB fill:#4a90d9,stroke:#333
    style IDEMPOTENCY fill:#4a90d9,stroke:#333
```

<p class="mermaid-hint">Click diagram to zoom</p>

- This project provides a working orders service where customers can create orders of items.

- The project deploys an API GW with an AWS Lambda integration under the path POST /api/orders/ and stores orders data in a DynamoDB table.

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

<p class="mermaid-hint">Click diagram to zoom</p>

### **Features**

- Python Serverless service with a recommended file structure.
- CDK infrastructure with infrastructure tests and security tests.
- CI/CD pipelines based on Github actions that deploys to AWS with python linters, complexity checks and style formatters.
- CI/CD pipeline deploys to dev/staging and production environment with different gates between each environment
- Makefile for simple developer experience.
- The AWS Lambda handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.
- AWS Lambda handler uses [AWS Lambda Powertools](https://docs.powertools.aws.dev/lambda-python/){:target="_blank" rel="noopener"}.
- AWS Lambda handler 3 layer architecture: handler layer, logic layer and data access layer
- Features flags and configuration based on AWS AppConfig
- CloudWatch dashboards - High level and low level including CloudWatch alarms
- Idempotent API
- REST API protected by WAF with four AWS managed rules in production deployment
- Unit, infrastructure, security, integration and E2E tests.
- Automatically generated OpenAPI endpoint: /swagger with Pydantic schemas for both requests and responses
- Automated protection against API breaking changes

The GitHub blueprint project can be found at [https://github.com/ran-isenberg/aws-lambda-handler-cookbook](https://github.com/ran-isenberg/aws-lambda-handler-cookbook){:target="_blank" rel="noopener"}.

## **AI-Assisted Development**

This project uses [AI-DLC (AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows){:target="_blank" rel="noopener"} for AI-assisted software development. Learn more about AI-DLC in this [blog post](https://www.ranthebuilder.cloud/post/ai-driven-sdlc){:target="_blank" rel="noopener"}.

AI-DLC provides a structured, adaptive workflow for:

- **Requirements Analysis** - Intelligent requirements gathering and clarification
- **Architecture Design** - AI-assisted architectural decisions
- **Code Generation** - Structured code implementation with best practices
- **Testing** - Comprehensive test generation and validation

The AI-DLC workflow artifacts are stored in the `aidlc-docs/` directory.

## **Serverless Best Practices**

The AWS Lambda handler will implement multiple best practice utilities.

Each utility is implemented when a new blog post is published about that utility.

The utilities cover multiple aspects of a production-ready service, including:

- [**Logging**](best_practices/logger.md)
- [**Observability: Monitoring and Tracing**](best_practices/tracer.md)
- [**Observability: Business KPI Metrics**](best_practices/metrics.md)
- [**Environment Variables**](best_practices/environment_variables.md)
- [**Input Validation**](best_practices/input_validation.md)
- [**Dynamic configuration & features flags**](best_practices/dynamic_configuration.md)
- [**Serverless Monitoring**](https://www.ranthebuilder.cloud/post/how-to-effortlessly-monitor-serverless-applications-with-cloudwatch-part-one)
- [**API Idempotency**](https://www.ranthebuilder.cloud/post/serverless-api-idempotency-with-aws-lambda-powertools-and-cdk){:target="_blank" rel="noopener"}
- [**Learn How to Write AWS Lambda Functions with Three Architecture Layers**](https://www.ranthebuilder.cloud/post/learn-how-to-write-aws-lambda-functions-with-architecture-layers){:target="_blank" rel="noopener"}
- [**Serverless OpenAPI Documentation with AWS Powertools**](https://www.ranthebuilder.cloud/post/serverless-open-api-documentation-with-aws-powertools){:target="_blank" rel="noopener"}

While the code examples are written in Python, the principles are valid to any supported AWS Lambda handler programming language.

## **License**

This library is licensed under the MIT License. See the [LICENSE](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/LICENSE) file.
