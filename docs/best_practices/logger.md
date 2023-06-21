---
title: Logger
description: Logger
---
It’s a wrapper of Python’s logging library that provides extra capabilities such as JSON output configuration (and many more).

![Logger](../media/logger.png)

## **Key features**

* Capture key fields from Lambda context, cold start and structures logging output as JSON
* Log Lambda event when instructed (disabled by default)
* Append additional keys to structured log at any point in time

## **Usage in Handler**

```python hl_lines="8 12 13" title="my_handler.py"
--8<-- "docs/examples/best_practices/logger/my_handler.py"
```

## **Blog Reference**

Read more about the importance of the logger and how to use AWS CloudWatch logs in my blog. Click [**HERE**](https://www.ranthebuilder.cloud/post/aws-lambda-cookbook-elevate-your-handler-s-code-part-1-logging){:target="_blank" rel="noopener"}

## **More Details**

You can find more information at the official documentation.

Go to [https://docs.powertools.aws.dev/lambda-python/latest/core/logger/](https://docs.powertools.aws.dev/lambda-python/latest/core/logger/){:target="_blank" rel="noopener"}
