# AWS Lambda Cookbook - Elevate your handler's code
[![license](https://img.shields.io/github/license/ran-isenberg/aws-lambda-handler-cookbook)](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/master/LICENSE)
![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.8&color=blue?style=flat-square&logo=python)
[![codecov](https://codecov.io/gh/ran-isenberg/aws-lambda-handler-cookbook/branch/main/graph/badge.svg?token=P2K7K4KICF)](https://codecov.io/gh/ran-isenberg/aws-lambda-handler-cookbook)
![version](https://img.shields.io/github/v/release/ran-isenberg/aws-lambda-handler-cookbook)
![issues](https://img.shields.io/github/issues/ran-isenberg/aws-lambda-handler-cookbook)



What makes an AWS Lambda handler resilient, traceable and easy to maintain? How do you write such a code?

The project is a template project that is based on my AWS Lambda handler cookbook blog series that I publish in [ranthebuilder.cloud](https://www.ranthebuilder.cloud) and attempt to answer those questions.

This project provides a working, open source based, AWS Lambda handler skeleton Python code including DEPLOYMENT code with CDK and a pipeline.

The project deploys an API GW with an AWS Lambda integration under the path GET /api/service/.
The AWS Lambda handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.

This project can serve as a template for new Serverless services - CDK deployment code, pipeline and handler are covered.


## CDK Deployment
The CDK code create an API GW with a path of /api/service which triggers the lambda on 'GET' requests.

The AWS Lambda handler uses a Lambda layer optimization which takes all the packages under the [packages] section in the Pipfile and downloads them in via a Docker instance.

This allows you to package any custom dependencies you might have, just add them to the Pipfile under the [packages] section.

## Serverless Best Practices
The AWS Lambda handler will implement multiple best practice utilities.

Each utility is implemented when a new blog post is published about that utility.

The utilities cover multiple aspect of a production-ready service, including:

1.  Logging
2.  Observability: Monitoring and Tracing
3.  Observability: Business KPI Metrics
4.  Environment variables.
5.  Input validation
6.  Features flags & dynamic configuration


## The Blog Series
- First blog post - [Logging](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-1-logging)
- Second blog post- [Observability: Monitoring and Tracing](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-2-observability)
- Third blog post- [Observability: Business KPIs Metrics](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-3-business-domain-observability)


#
I've written 3 of the mentioned utilities (parser, feature flags and environment variables) and donated two of them, the [parser](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/parser/) and [feature flags](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/) to [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/).

While the code examples are written in Python, the principles are valid to any supported AWS Lambda handler programming language.


This repository is the complementary code examples of my blog series "AWS Lambda Cookbook - Elevate your handler's code"



## Getting started
Head over to the complete project documentation pages at GitHub pages at [https://ran-isenberg.github.io/aws-lambda-handler-cookbook](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/)


## License
This library is licensed under the MIT License. See the [LICENSE](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/LICENSE) file.
