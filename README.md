# AWS Lambda Cookbook - Elevate your handler's code
![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.8&color=blue?style=flat-square&logo=python)
[![codecov](https://codecov.io/gh/ran-isenberg/aws-lambda-handler-cookbook/branch/main/graph/badge.svg?token=P2K7K4KICF)](https://codecov.io/gh/ran-isenberg/aws-lambda-handler-cookbook)

What makes an AWS Lambda handler resilient, traceable and easy to maintain? How do you write such a code?

This repository provides a working, open source based, AWS Lambda handler skeleton Python code including DEPLOYMENT code with CDK.
This project can serve as a template for new services - deployment and handler are covered.

## CDK Deployment
The CDK code create an API GW with a path of /api/service which triggers the lambda on 'GET' requests.

The AWS Lambda handler uses a Lambda layer optimization which taken all the packages under the [packages] section in the Pipfile and downloads them in via a Docker instance.

This allows you to package any custom dependencies you might have, just add them to the Pipfile under the [packages] section.

## Handler Best Practices
Regarding the handler itself:
In addition, this AWS Lambda handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.
It will cover issues such as:
1.  Logging
2.  Observability: Monitoring and Tracing
3.  Observability: Business KPI Metrics
4.  Input validation
5.  Features flags & dynamic configuration
6.  Environment variables.


While the code examples are written in Python, the principles are valid to any supported AWS Lambda handler programming language.

Most of the code examples here are taken from the excellent AWS Lambda Powertools repository:  https://github.com/awslabs/aws-lambda-powertools-python


I've written several of the utilities which are mentioned in this blog series and donated 2 of them, the parser and feature flags to AWS Lambda Powertools.

This repository is the complementary code examples of my blog series "AWS Lambda Cookbook - Elevate your handler's code"


## The Blog Series
- First blog post - Logging:  https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-1-logging
- Second blog post- Observability: Monitoring and Tracing: https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-2-observability
- Third blog post- Observability: Business KPIs Metrics: https://isenberg-ran.medium.com/aws-lambda-cookbook-elevate-your-handlers-code-part-2-observability-eff158307180


## Getting started
You must install Docker and AWS CDK on your machine for the Lambda layer packaging process.
Then follow these commands:
```shell script
pipenv install --dev
make deploy
make pr
```

## Project Folders logic
CDK project is saved under 'cdk'.
Service handler code is saved under 'service'.
The assumption here that this is a service behind an API GW that shares code between handlers (each handler is bound

to a path in the API GW).
Handlers are written in their own files but share utilities (logger, tracer etc.) which can be found at the 'utils.infra' folder.


## CDK
Follow this guide https://docs.aws.amazon.com/cdk/v1/guide/getting_started.html

You must make sure your AWS account and machine can deploy stack and have all the tokens and configuration as described in the page above.

All Lambda function configuration are saved as constants at the cdk.aws_lambda_handler_cookbook.constants.py file and can easily be changed: lambda memory size, etc.


## Deleting the stack
```shell script
make destroy
```

## Unit tests
Unit tests can be found under the `tests` folder.
You can run the tests by using the following command:
```shell script
make unit
```

## E2E Tests
Make sure you deploy the stack first.
These tests send a 'GET' message to the deployed API GW and trigger the actual Lambda on AWS.

The tests are run automatically by:
```shell script
make e2e
```

## License
This library is licensed under the MIT License. See the LICENSE file.
