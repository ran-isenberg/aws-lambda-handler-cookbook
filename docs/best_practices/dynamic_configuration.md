---
title: Dynamic Configuration & Smart Feature Flags
description: Dynamic Configuration & Smart Feature Flags
---

Feature flags are used to modify behaviour without changing the application's code. These flags can be static or dynamic.

Static flags. Indicates something is simply on or off, for example TRACER_ENABLED=True.

Dynamic flags. Indicates something can have varying states, for example enable a list of premium features for customer X not Y.

SDK for dynamic configuration stored in AWS AppConfig and smart feature flags support.

This SDK is based on the [Feature Flags utility of AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/){:target="_blank" rel="noopener"} github repository that I designed and developed. 


![Dynamic Configuration & Feature Flags](../media/appconfig.png){: style="height:50%;width:20%"}


## **Blog Reference**
Read more about the importance of static vs dynamic configuration and feature flags and how this utility works. Click [**HERE**](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-environment-variables){:target="_blank" rel="noopener"}


## **Key features**
* CDK construct that deploys your JSON configuration to AWS AppConfig
* Use JSON file to describe both configuration values and smart feature flags. 
* Provide one simple API to get configuration anywhere in the AWS Lambda function code.
* Provide one simple API to evaluate smart feature flags values.
* During runtime, store the configuration in a local cache with a configurable TTL to reduce API calls to AWS (to fetch the JSON configuration) and total cost. 
* Built-in support for [Pydantic](https://pydantic-docs.helpmanual.io/){:target="_blank" rel="noopener"} models. We've used Pydantic to serialize and validate JSON configuration (input validation and environment variables) throughout this blog series, so it makes sense to use it to parse dynamic configuration.

## **What is AWS AppConfig**
AWS AppConfig is a self-managed service that stores plain text/YAML/JSON configuration to be consumed by multiple clients. 

We will use it in the context of dynamic configuration and feature toggles and store a single JSON file that contains both feature flags and configuration values.

Let's review its advantages:

- FedRAMP High certified
- Fully Serverless
- Out of the box support for schema validations that run before a configuration update.
- Out-of-the-box integration with AWS CloudWatch alarms triggers an automatic configuration revert if a configuration update fails your AWS Lambda functions. Read more about it here.
- You can define configuration deployment strategies. Deployment strategies define how and when to change a configuration. Read more about it here.
- It provides a single API that provides configuration and feature flags access—more on that below.
- AWS AppConfig provides integrations with other services such as Atlassian Jira and AWS CodeDeploy. Click here for details. 

## **CDK Construct**
'configuration_construct.py' defines a CDK v2 AWS AppConfig configuration with the following entities:
1. Application (service)
2. Environment
3. Deployment strategy - immediate deploy, 0 minutes wait, no validations or AWS CloudWatch alerts
4. The JSON configuration. It uploads the files ‘cdk/aws_lambda_handler_cookbook/service_stack/configuration/json/{environment}_configuration.json’, where environment is a construct argument (default is 'dev') 

Make sure to deploy this construct in a separate pipeline from the AWS Lambda function (unlike in this example), otherwise it wont be a true dynamic configuration.


## **AWS Lambda CDK Changes**
You need to add two new settings in order to use this utility:
1. New environment variables:
   - AWS AppConfig configuration application name (‘CONFIGURATION_APP’)
   - AWS AppConfig environment name (‘CONFIGURATION_ENV’)
   - AWS AppConfig configuration name to fetch (‘CONFIGURATION_NAME’)
   - Cache TTL in minutes (‘CONFIGURATION_MAX_AGE_MINUTES’)
2. AWS Lambda IAM role to include allow 'appconfig:GetConfiguration' on '*'.

## **Smart Feature Flags**
Smart feature flags are feature flags that are evaluated in runtime and can change their values according to session context.
Read more about them [here](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/#schema){:target="_blank" rel="noopener"}

## **Fetching Configuration**
You need to model your dynamic configuration as a Pydantic schema class (excluding feature flags) in a Pydantic schema class that extend Pydantic's BaseModel class.
The 'parse_configuration' function will fetch the JSON configuration from AWS AppConfig and use your Pydantic model to validate it and return a valid dataclass instance.

=== "my_handler.py"
```python hl_lines="6"
--8<-- "docs/examples/best_practices/dynamic_configuration/parse_configuration.py"
```

## **Evaluating Feature Flags**
It is recommended to store feature flags under the 'features' key in the configuration JSON as the utilities described here are configured as such.

For example:

=== "my_handler.py"
```python hl_lines="6" title="my_handler.py"
--8<-- "docs/examples/best_practices/dynamic_configuration/evaluate_feature_flags.py"
```

## **More Details**

Read [here](https://pydantic-docs.helpmanual.io/usage/types/){:target="_blank" rel="noopener"} about Pydantic field types.

Read [here](https://pydantic-docs.helpmanual.io/usage/validators/){:target="_blank" rel="noopener"} about custom validators and advanced value constraints.
