
# AWS Lambda Handler Cookbook (Python)

[![license](https://img.shields.io/github/license/ran-isenberg/aws-lambda-handler-cookbook)](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/master/LICENSE)
![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.11&color=blue?style=flat-square&logo=python)
[![codecov](https://codecov.io/gh/ran-isenberg/aws-lambda-handler-cookbook/branch/main/graph/badge.svg?token=P2K7K4KICF)](https://codecov.io/gh/ran-isenberg/aws-lambda-handler-cookbook)
![version](https://img.shields.io/github/v/release/ran-isenberg/aws-lambda-handler-cookbook)
![github-star-badge](https://img.shields.io/github/stars/ran-isenberg/aws-lambda-handler-cookbook.svg?style=social)
![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/ran-isenberg/aws-lambda-handler-cookbook/badge)
![issues](https://img.shields.io/github/issues/ran-isenberg/aws-lambda-handler-cookbook)

![alt text](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/docs/media/banner.png?raw=true)

This project provides a working, open source based, AWS Lambda handler skeleton Python code including DEPLOYMENT code with CDK and a pipeline.

This project can serve as a template for new Serverless services - CDK deployment code, pipeline and handler are covered.

**[📜Documentation](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/)** | **[Blogs website](https://www.ranthebuilder.cloud)**
> **Contact details | ran.isenberg@ranthebuilder.cloud**

[![Twitter Follow](https://img.shields.io/twitter/follow/IsenbergRan?label=Follow&style=social)](https://twitter.com/IsenbergRan)
[![Website](https://img.shields.io/badge/Website-www.ranthebuilder.cloud-blue)](https://www.ranthebuilder.cloud/)

## Getting Started

You can start with a clean service out of this template repository without using the 'Template' button on GitHub.

You can use Cookiecutter.

* Cookiecutter - install with pip/brew ``brew install cookiecutter`` or ``pip install cookiecutter`

Then run:

```
cookiecutter gh:ran-isenberg/cookiecutter-serverless-python
```

Answer the questions to select repo name, service name, etc.:

![logo](https://github.com/ran-isenberg/cookiecutter-serverless-python/blob/main/media/howto.png?raw=true)


**That's it, your developer environment has been set! you are ready to deploy the service:**

```
cd {new repo folder}
poetry shell
make deploy
```

You can also run 'make pr' will run all checks, synth, file formatters , unit tests, deploy to AWS and run integration and E2E tests.

## **The Problem**

Starting a Serverless service can be overwhelming. You need to figure out many questions and challenges that have nothing to do with your business domain:

- How to deploy to the cloud? What IAC framework do you choose?
- How to write a SaaS-oriented CI/CD pipeline? What does it need to contain?
- How do you handle observability, logging, tracing, metrics?
- How do you write a Lambda function?
- How do you handle testing?
- What makes an AWS Lambda handler resilient, traceable, and easy to maintain? How do you write such a code?


## **The Solution**

This project aims to reduce cognitive load and answer these questions for you by providing a skeleton Python Serverless service template that implements best practices for AWS Lambda, Serverless CI/CD, and AWS CDK in one template project.

### Serverless Service - The Order service

- This project provides a working orders service where customers can create orders of items.

- The project deploys an API GW with an AWS Lambda integration under the path POST /api/orders/ and stores data in a DynamoDB table.

![design](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/docs/media/design.png?raw=true)
<br></br>

#### **Monitoring Design**
![monitoring_design](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/docs/media/monitoring_design.png?raw=true)
<br></br>
### **Features**

- Python Serverless service with a recommended file structure.
- CDK infrastructure with infrastructure tests and security tests.
- CI/CD pipelines based on Github actions that deploys to AWS with python linters, complexity checks and style formatters.
- CI/CD pipeline deploys to dev/staging and production environments with different gates between each environment
- Makefile for simple developer experience.
- The AWS Lambda handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.
- AWS Lambda handler uses [AWS Lambda Powertools](https://docs.powertools.aws.dev/lambda-python/).
- AWS Lambda handler 3 layer architecture: handler layer, logic layer and data access layer
- Features flags and configuration based on AWS AppConfig
- Idempotent API
- REST API protected by WAF with four AWS managed rules in production deployment
- CloudWatch dashboards - High level and low level including CloudWatch alarms
- Unit, infrastructure, security, integration and end to end tests.


## CDK Deployment
The CDK code create an API GW with a path of /api/orders which triggers the lambda on 'POST' requests.

The AWS Lambda handler uses a Lambda layer optimization which takes all the packages under the [packages] section in the Pipfile and downloads them in via a Docker instance.

This allows you to package any custom dependencies you might have, just add them to the Pipfile under the [packages] section.

## Serverless Best Practices
The AWS Lambda handler will implement multiple best practice utilities.

Each utility is implemented when a new blog post is published about that utility.

The utilities cover multiple aspect of a production-ready service, including:

- [Logging](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-1-logging)
- [Observability: Monitoring and Tracing](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-2-observability)
- [Observability: Business KPIs Metrics](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-3-business-domain-observability)
- [Environment Variables](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-environment-variables)
- [Input Validation](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-5-input-validation)
- [Dynamic Configuration & feature flags](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-part-6-feature-flags-configuration-best-practices)
- [Start Your AWS Serverless Service With Two Clicks](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-part-7-how-to-use-the-aws-lambda-cookbook-github-template-project)
- [CDK Best practices](https://github.com/ran-isenberg/aws-lambda-handler-cookbook)
- [Serverless Monitoring](https://www.ranthebuilder.cloud/post/how-to-effortlessly-monitor-serverless-applications-with-cloudwatch-part-one)
- [API Idempotency](https://www.ranthebuilder.cloud/post/serverless-api-idempotency-with-aws-lambda-powertools-and-cdk)

## Getting started
Head over to the complete project documentation pages at GitHub pages at [https://ran-isenberg.github.io/aws-lambda-handler-cookbook](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/)

## Code Contributions
Code contributions are welcomed. Read this [guide.](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/CONTRIBUTING.md)

## Code of Conduct
Read our code of conduct [here.](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/CODE_OF_CONDUCT.md)

## Connect
* Email: [ran.isenberg@ranthebuilder.cloud](mailto:ran.isenberg@ranthebuilder.cloud)
* Blog Website [RanTheBuilder](https://www.ranthebuilder.cloud)
* LinkedIn: [ranisenberg](https://www.linkedin.com/in/ranisenberg/)
* Twitter: [IsenbergRan](https://twitter.com/IsenbergRan)

## Credits
* [AWS Lambda Powertools (Python)](https://github.com/aws-powertools/powertools-lambda-python)

## License
This library is licensed under the MIT License. See the [LICENSE](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/LICENSE) file.
