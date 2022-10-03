---
title: Homepage
description: AWS Lambda Cookbook - Elevate Your Handler's Code for Python
---
## **AWS Lambda Cookbook - Elevate Your Handler's Code**

[<img alt="alt_text" src="./media/banner.png" />](https://www.ranthebuilder.cloud/)

What makes an AWS Lambda handler resilient, traceable and easy to maintain? How do you write such a code?

The project is a template project that is based on my AWS Lambda handler cookbook blog series that I publish in [ranthebuilder.cloud](https://www.ranthebuilder.cloud){:target="_blank" rel="noopener"} and attempt to answer those questions.

The GitHub template project can be found at [https://github.com/ran-isenberg/aws-lambda-handler-cookbook](https://github.com/ran-isenberg/aws-lambda-handler-cookbook){:target="_blank" rel="noopener"}.

- This project provides a working, open source based, AWS Lambda handler skeleton Python code including DEPLOYMENT code with CDK.

- The project deploys an API GW with an AWS Lambda integration under the path POST /api/service/.

- The AWS Lambda handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.

- This project can serve as a template for new Serverless services - CDK deployment code, pipeline and handler are covered.

- The CDK project has infrastructure tests and security tests and follows the AWS CDK best practices.

## **The Blog Series**

- First blog post   - [Logging](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-1-logging){:target="_blank" rel="noopener"}
- Second blog post  - [Observability: Monitoring and Tracing](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-2-observability){:target="_blank" rel="noopener"}
- Third blog post   - [Observability: Business KPIs Metrics](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-3-business-domain-observability){:target="_blank" rel="noopener"}
- Fourth blog post  - [Environment Variables](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-environment-variables){:target="_blank" rel="noopener"}
- Fifth blog post   - [Input Validation](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-5-input-validation){:target="_blank" rel="noopener"}
- Sixth blog post   - [Dynamic Configuration & feature flags](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-part-6-feature-flags-configuration-best-practices){:target="_blank" rel="noopener"}
- Seventh blog post - [Start Your AWS Serverless Service With Two Clicks](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-part-7-how-to-use-the-aws-lambda-cookbook-github-template-project){:target="_blank" rel="noopener"}
- CDK  post         - [CDK Best practices](https://github.com/ran-isenberg/aws-lambda-handler-cookbook){:target="_blank" rel="noopener"}

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

I've written 3 of the mentioned utilities (parser, feature flags and environment variables) and donated two of them, the [parser](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/parser/) and [feature flags](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/) to [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/).

While the code examples are written in Python, the principles are valid to any supported AWS Lambda handler programming language.

## **License**

This library is licensed under the MIT License. See the [LICENSE](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/LICENSE) file.
