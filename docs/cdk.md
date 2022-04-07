---
title: AWS CDK
description: AWS Lambda Cookbook CDK Project
---
## **Prerequisites**
- Follow this [getting started with CDK guide](https://docs.aws.amazon.com/cdk/v1/guide/getting_started.html){:target="_blank" rel="noopener"}
- You must make sure your AWS account and machine can deploy an AWS Cloudformation stack and have all the tokens and configuration as described in the page above.



## **CDK Deployment**

<img alt="alt_text" src="../media/cdk.png" />

All CDK project files can be found under the CDK folder.

The CDK code create an API GW with a path of /api/service which triggers the lambda on 'POST' requests.

The AWS Lambda handler uses a Lambda layer optimization which takes all the packages under the [packages] section in the Pipfile and downloads them in via a Docker instance.

This allows you to package any custom dependencies you might have.

In order to add a new dependency, add it to the Pipfile under the [packages] section and run ``pipenv update --dev`` and then ``make deps``.

### **CDK Constants**
All ASW Lambda function configurations are saved as constants at the `cdk.aws_lambda_handler_cookbook.service_stack.constants.py` file and can easily be changed.

- Memory size
- Timeout in seconds
- Lambda dependencies build folder location
- Lambda Layer dependencies build folder location
- Various resources names
- Lambda function environment variables names and values

### **Deployed Resources**
- AWS Cloudformation stack: **cdk.aws_lambda_handler_cookbook.service_stack.cookbook_stack.py** which is consisted of one construct
- Construct: **cdk.aws_lambda_handler_cookbook.service_stack.cookbook_construct.py** which includes:
    * **Lambda Layer** - deployment optimization meant to be used with multiple handlers under the same API GW, sharing code logic and dependencies. You can read more about it in Yan - Cui's [blog](https://medium.com/theburningmonk-com/lambda-layer-not-a-package-manager-but-a-deployment-optimization-85ddcae40a96){:target="_blank" rel="noopener"}
    * **Lambda Function** - The Lambda handler function itself. Handler code is taken from the service `folder`.
    * **Lambda Role** - The role of the Lambda function.
    * **API GW with Lambda Integration** - API GW with a Lambda integration POST /api/service that triggers the Lambda function.
