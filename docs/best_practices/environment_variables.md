---
title: Environment Variables
description: Environment Variables
---
Environment Variables decorator is a simple parser for environment variables that run at the start of the handler invocation.

![Environment Variables](../media/pydantic.png){: style="height:50%;width:20%"}

## **Key features**

* A defined [Pydantic](https://pydantic-docs.helpmanual.io/){:target="_blank" rel="noopener"} schema for all required environment variables
* A decorator that parses and validates environment variables, value constraints included
* Global getter for parsed & valid schema dataclass with all environment variables

The best practice for handling environment variables is to validate & parse them according to a predefined schema as soon as the AWS Lambda function is triggered.

In case of misconfiguration, a validation exception is raised with all the relevant exception details.

## **Open source**

The code in this post has been moved to an open source project you can use:

The [AWS Lambda environment variables modeler](https://github.com/ran-isenberg/aws-lambda-env-modeler){:target="_blank" rel="noopener"}

## **Blog Reference**

Read more about the importance of validating environment variables and how this utility works. Click [**HERE**](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-environment-variables){:target="_blank" rel="noopener"}

## **Schema Definition**

You need to define all your environment variables in a Pydantic schema class that extend Pydantic's BaseModel class.

For example:

```python hl_lines="6" title="schemas/env_vars.py"
--8<-- "docs/examples/best_practices/environment_variables/env_vars.py"
```

All Pydantic schemas extend Pydantic’s ‘BaseModel’ class, turning them into a dataclass.

The schema defines four environment variables: ‘LOG_LEVEL,’ ‘POWERTOOLS_SERVICE_NAME,’ ‘ROLE_ARN,’ and ‘REST_API.’

This schema makes sure that:

* ‘LOG_LEVEL’ is one of the strings in the Literal list.
* ‘ROLE_ARN’ exists and is between 20 and 2048 characters long, as defined here.
* ‘REST_API’ is a valid HTTP URL.
* ‘POWERTOOLS_SERVICE_NAME’ is a non-empty string.

Read [here](https://pydantic-docs.helpmanual.io/usage/models/){:target="_blank" rel="noopener"} about Pydantic Model capabilities.

## **Decorator Usage**

The decorator 'init_environment_variables' is defined under the utility folder **service.utils.env_vars_parser.py** and imported in the handler.

The decorator requires a **model** parameter, which in this example is the name of the schema class we defined above.

```python hl_lines="11" title="handlers/my_handler.py"
--8<-- "docs/examples/best_practices/environment_variables/my_handler.py"
```

## **Global Getter Usage**

The getter function 'get_environment_variables' is defined under the utility folder **service.utils.env_vars_parser.py** and imported in the handler.

The getter function returns a parsed and validated global instance of the environment variables Pydantic schema class.

It can be used *anywhere* in the function code, not just the handler.

```python hl_lines="13" title="handlers/my_handler.py"
--8<-- "docs/examples/best_practices/environment_variables/getter.py"
```

## **More Details**

Read [here](https://pydantic-docs.helpmanual.io/usage/types/){:target="_blank" rel="noopener"} about Pydantic field types.

Read [here](https://pydantic-docs.helpmanual.io/usage/validators/){:target="_blank" rel="noopener"} about custom validators and advanced value constraints.
