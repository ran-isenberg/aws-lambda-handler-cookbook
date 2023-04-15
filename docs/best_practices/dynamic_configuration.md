---
title: Dynamic Configuration & Smart Feature Flags
description: Dynamic Configuration & Smart Feature Flags
---

![Dynamic Configuration & Feature Flags](../media/appconfig.png)

Feature flags are used to modify behavior without changing the application's code.

This pages describes a utility for fetching dynamic configuration and evaluating smart feature flags stored in AWS AppConfig as a JSON file.

This utility is based on the [Feature Flags utility of AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/){:target="_blank" rel="noopener"} Github repository that I designed and developed.

## **Blog Reference**

Read more about the differences between static and dynamic configurations, when to use each type how this utility works. Click [**HERE**](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-part-6-feature-flags-configuration-best-practices){:target="_blank" rel="noopener"}

## **Key features**

* CDK construct that deploys your JSON configuration to AWS AppConfig
* Uses a JSON file to describe both configuration values and smart feature flags.
* Provides one simple API to get configuration anywhere in the AWS Lambda function code.
* Provides one simple API to evaluate smart feature flags values.
* During runtime, stores the configuration in a local cache with a configurable TTL to reduce API calls to AWS (to fetch the JSON configuration) and total cost.
* Built-in support for [Pydantic](https://pydantic-docs.helpmanual.io/){:target="_blank" rel="noopener"} models. We've used Pydantic to serialize and validate JSON configuration (input validation and environment variables) throughout this blog series, so it makes sense to use it to parse dynamic configuration.

## **What is AWS AppConfig**

AWS AppConfig is a self-managed service that stores plain text/YAML/JSON configuration to be consumed by multiple clients.

We will use it in the context of dynamic configuration and feature toggles and store a single JSON file that contains both feature flags and configuration values.

Let's review its advantages:

* FedRAMP High certified
* Fully Serverless
* Out of the box support for schema validations that run before a configuration update.
* Out-of-the-box integration with AWS CloudWatch alarms triggers an automatic configuration revert if a configuration update fails your AWS Lambda functions. Read more about it here.
* You can define configuration deployment strategies. Deployment strategies define how and when to change a configuration. Read more about it here.
* It provides a single API that provides configuration and feature flags access—more on that below.
* AWS AppConfig provides integrations with other services such as Atlassian Jira and AWS CodeDeploy.

## **CDK Construct**

'configuration_construct.py' defines a CDK v2 AWS AppConfig configuration with the following entities:

1. Application (service)
2. Environment
3. Custom deployment strategy - immediate deploy, 0 minutes wait, no validations or AWS CloudWatch alerts
4. The JSON configuration. It uploads the files ‘cdk/my_service/configuration/json/{environment}_configuration.json’, where environment is a construct argument (default is 'dev')

The construct **validates** the JSON file and verifies that feature flags syntax is valid and exists under the 'features' key. Feature flags are optional.

Make sure to deploy this construct in a separate pipeline from the AWS Lambda function (unlike in this example), otherwise it wont be a dynamic configuration.

Read more about AWS AppConfig [here.](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html){:target="_blank" rel="noopener"}

### Configuration Stack Example

Args:

* scope (Construct): The scope in which to define this construct.
* id_ (str): The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
* environment (str): environment name. Used for loading the corresponding JSON file to upload under 'configuration/json/{environment}_configuration.json'
* service_name (str): application name.
* configuration_name (str): configuration name
* deployment_strategy_id (str, optional): AWS AppConfig deployment strategy.

=== "configuration_stack.py"

```python hl_lines="13"
--8<-- "docs/examples/best_practices/dynamic_configuration/cdk_appconfig.py"
```

The JSON configuration that is uploaded to AWS AppConfig resides under ``cdk/my_service/configuration/json/dev_configuration.json``

``dev`` represents the default environment. You can add multiple configurations for different environments.

Make sure the prefix remains the environment underscore configuration ``dev_configuration``, ``prod_configuration`` etc.

## **AWS Lambda CDK Changes**

You need to add two new settings in order to use this utility:

1. New environment variables:
   * AWS AppConfig configuration application name (‘CONFIGURATION_APP’)
   * AWS AppConfig environment name (‘CONFIGURATION_ENV’)
   * AWS AppConfig configuration name to fetch (‘CONFIGURATION_NAME’)
   * Cache TTL in minutes (‘CONFIGURATION_MAX_AGE_MINUTES’)
2. AWS Lambda IAM role to include allow 'appconfig:GetLatestConfiguration' and 'appconfig:StartConfigurationSession' on '*'.

=== "cdk_lambda.py"

```python hl_lines="15-22 46-49"
--8<-- "docs/examples/best_practices/dynamic_configuration/lambda_cdk.py"
```

## **Fetching Dynamic Configuration**

You need to model your dynamic configuration as a Pydantic schema class (excluding feature flags) extend Pydantic's BaseModel class.

The ``parse_configuration`` function will fetch the JSON configuration from AWS AppConfig and use your Pydantic model to validate it and return a valid dataclass instance.

Let's assume that our configuration looks like this:

=== "configuration.json"

```json
--8<-- "docs/examples/best_practices/dynamic_configuration/non_features_flags.json"
```

We need to define a Pydantic model that will parse and validate the JSON file and pass it as an argument to the function ``parse_configuration``.

=== "configuration_schema.py"

```python hl_lines="18 23"
--8<-- "docs/examples/best_practices/dynamic_configuration/configuration_schema.py"
```

Now we can call the ``parse_configuration`` function and pass it the ``MyConfiguration`` class name.

The function fetch the JSON file from AWS AppConfig and return a parsed instance of the configuration dataclass ``MyConfiguration``.

=== "my_handler.py"

```python hl_lines="15 18 23"
--8<-- "docs/examples/best_practices/dynamic_configuration/parse_configuration.py"
```

If you want to learn more about how ``parse_configuration`` function works, click [here](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-part-6-feature-flags-configuration-best-practices){:target="_blank" rel="noopener"}.

## **Feature Flags**

Feature flags can be evaluated to any valid JSON value.

However, in these snippets, they are all boolean for simplicity.

### **Smart Feature Flags**

Smart feature flags are feature flags that are evaluated in runtime and can change their values according to session context.

Smart feature flags require evaluation in runtime and can have different values for different AWS Lambda function sessions.

Imagine pushing a new feature into production but enabling it only for several specific customers.

A smart feature flag will need to evaluate the customer name and decide whether the final value is 'True/False'.

Smart feature flags are defined by rules, conditions, and actions determining the final value.

Read more about them [here](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/#schema){:target="_blank" rel="noopener"}

### **Regular Feature Flags**

Regular feature flags are flags that have a default value which does not change according to input context.

## **Evaluating Feature Flags**

It is mandatory to store feature flags under the 'features' key in the configuration JSON as the utilities described here are configured as such.

**Feature flags can have any valid JSON value but these examples use boolean.**

Let's assume that our AWS Lambda handler supports two feature flags: regular and smart.

1. Ten percent discount for the current order: ``True/False``.
2. Premium feature for the customer: ``True/False``.

Premium features are enabled only to specific customers. A ten percent discount is a simple feature flag. According to store policy, a ten percent discount can be turned on or off.

It doesn't change according to session input; it is ``True`` or ``False`` for all inputs.

On the other hand,  premium features are based on a rule. It's a smart feature flag.Its' value is ``False`` for all but specific customers.

To use AWS Lambda Powertools feature flags capabilities, we need to build a JSON file that matches the SDK language.

### Regular Feature Flags Definition

Defining the ten percent discount flag is simple. It has a key and a dictionary containing a ``default value`` key with a boolean value.

Let's assume the feature flags are enabled. Let's add it to the current configuration we already have:

=== "configuration.json"

```json
--8<-- "docs/examples/best_practices/dynamic_configuration/non_features_flags.json"
```

### **Smart Feature Flags JSON Definition**

Now, let's add the smart feature flag, premium features. We want to enable it only for customers by 'RanTheBuilder.'

The JSON structure is simple.

Each feature has a default value under the default key. It can any valid JSON value (boolean, int etc.).

Each feature can have optional rules that determine the evaluated value.

Each rule consists of a default value to return (in case of a match — when_match ) and a list of conditions. Only one rule can match.

Each condition consists of an action name (which is mapped to an operator in the rule engine code) and a key-value pair that serves as an argument to the SDK rule engine.

The combined JSON configuration look like this:

=== "configuration.json"

```json
--8<-- "docs/examples/best_practices/dynamic_configuration/configuration.json"
```

### **API Example**

=== "my_handler.py"

```python hl_lines="24-29 31-36"
--8<-- "docs/examples/best_practices/dynamic_configuration/evaluate_feature_flags.py"
```

In this example, we evaluate both feature flags' value and provide a context.

``ten_percent_off_campaign`` will be evaluated to ``True`` since it's a non smart feature flag with a default value of ``False`` in the JSON configuration.

The rule for ``premium_features`` is matched (which returns a ``True`` value for the flag) when the context dictionary has a key ``customer_name`` with a value of ``RanTheBuilder`` EQUALS ``RanTheBuilder``.

Line 31 will return a value of ``True`` for the context ``{'customer_name': 'RanTheBuilder'}`` and ``False`` for any other input.

There are several actions for conditions such as ``STARTSWITH``, ``ENDSWITH``, ``EQUALS``, etc.

You can read more about the rules, conditions, logic, and supported actions [here.](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/#rules){:target="_blank" rel="noopener"}

## **How To Locally Test Your Lambda In IDE**

You can and should mock the values that AWS AppConfig returns in order to check different types of configurations values and feature flags.

Make sure to always test your feature flags with all its possible values scope (enabled/disabled etc.)

You can also skip the mock and read the real values that are currently stored in AWS AppConfig.

However, I'd do that in the E2E tests.

=== "mock_test.py"

```python hl_lines="3 26-29 33"
--8<-- "docs/examples/best_practices/dynamic_configuration/mock.py"
```

Click [here](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/feature_flags/#testing-your-code) for more details.

## **Extra Documentation**

Read [here](https://pydantic-docs.helpmanual.io/usage/types/){:target="_blank" rel="noopener"} about Pydantic field types.

Read [here](https://pydantic-docs.helpmanual.io/usage/validators/){:target="_blank" rel="noopener"} about custom validators and advanced value constraints.
