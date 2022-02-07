# AWS Lambda Cookbook - Elevate your handler's code

What makes an AWS Lambda handler resilient, traceable and easy to maintain? How do you write such a code?

This repository provides a working, open source based, AWS Lambda handler skeleton Python code.
This handler embodies Serverless best practices and has all the bells and whistles for a proper production ready handler.
It will cover issues such as:
1.  Logging
2.  Tracing
3.  Input validation
4.  Features flags & dynamic configuration
5.  Environment variables.


While the code examples are written in Python, the principles are valid to any supported AWS Lambda handler programming language.

Most of the code examples here are taken from the excellent AWS Lambda Powertools repository:  https://github.com/awslabs/aws-lambda-powertools-python


I've written several of the utilities which are mentioned in this blog series and donated 2 of them, the parser and feature flags to AWS Lambda Powertools.

This repository is the complementary code examples of my blog series "AWS Lambda Cookbook - Elevate your handler's code"

First blog post: https://isenberg-ran.medium.com/aws-lambda-cookbook-elevate-your-handlers-code-part-1-bc160a10679a


## Getting started
```shell script
pipenv install --dev
make pr
```

### Unit tests
Unit tests can be found under the `tests` folder.
You can run the tests by using the following command:
```shell script
pytest -v
```


To calculate test code coverage us the command:
```shell script
pytest --cov
```
