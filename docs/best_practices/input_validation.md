---
title: Input Validation
description: Input Validation
---
This utility provides input validation and advanced parsing. It mitigates any hidden input assumption including value constraints.

**Rule of thumb: Always, always, always (!), validate all input.**

![Input Validation](../media/pydantic.png){: style="height:50%;width:20%"}


## **Key features**

The Parser will validate the incoming event, extract the input business payload, decode it and validate it according to a predefined schema.

This schema will verify that all required parameters exist, their type is as expected and validate any value constraints.

And all this will be achieved with one line of code.

This "magic" line will allow you to focus on your business logic and not worry about metadata and encapsulating services.


## **Service Envelope**
When an AWS Service sends an event that triggers your AWS Lambda function, metadata information is added to the event, and the business logic payload is encapsulated.

Let's call this metadata information 'envelope.'

The envelope contains valuable information, interesting headers, and the interesting part, the business logic input that you wish to process.

That's where it gets tricky.

Each AWS service has its envelope structure and may encapsulate the business logic payload differently.



## **Supported AWS Services**

For a complete list click [**here**](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/parser/#built-in-envelopes).




## **Define Business Logic Schema**
Use Pydantic schemas to define the expected input format. Extend 'BaseModel' class.

Define type and value constraints.


=== "schemas/input.py"

    ```python hl_lines="14"
    from pydantic import BaseModel, PositiveInt, constr

    class Input(BaseModel):
        my_name: constr(min_length=1, max_length=20)
        order_item_count: PositiveInt
    ```

The schema defines:

1. 'my_name' - customer name, a non-empty string with up to 20 characters.
2. 'order_item_count' - a positive integer representing the number of ordered items that 'my_name' placed.


Learn about models [**here**](https://pydantic-docs.helpmanual.io/usage/models/) and about advanced parsing [**here**](https://pydantic-docs.helpmanual.io/usage/validators/).

## **Usage in Handler**
The parser is a called with the function 'parse'.

Use the envelope class that matches the AWS service that triggers your AWS Lambda function.

```python hl_lines="13" title="my_handler.py"
--8<-- "docs/examples/best_practices/input_validation/my_handler.py"
```

## Accessing Envelope Metadata

You can access the metadata parameters by extending the model class and parsing the input without the envelope class.

Read more about it [**here**](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/parser/#extending-built-in-models).


## **Blog Reference**
Read more about the importance of input validation and the potential pitfalls it prevents in my blog. Click [**HERE**](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-5-input-validation){:target="_blank" rel="noopener"}.


## **More Details**
You can find more information at the official documentation.

Go to [https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/parser/](https://awslabs.github.io/aws-lambda-powertools-python/latest/utilities/parser/){:target="_blank" rel="noopener"}
