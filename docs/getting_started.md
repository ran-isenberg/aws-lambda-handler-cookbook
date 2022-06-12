---
title: Getting Started
description: AWS Lambda Cookbook Project Getting started
---
## **Prerequisites**
* **Docker** - install [Docker](https://www.docker.com/){target="_blank"}. Required for the Lambda layer packaging process.
* **[AWS CDK](cdk.md)** - Required for synth & deploying the AWS Cloudformation stack.
* Python 3.8


## **Creating a Virtual Python Environment**
Run ``make dev``

## **Deploy CDK**
Create a cloudformation stack by running ``make deploy``


## **Unit Tests**
Unit tests can be found under the ``tests/unit`` folder.

You can run the tests by using the following command: ``make unit``

## **Integration Tests**
Make sure you deploy the stack first as these tests trigger your lambda handler LOCALLY but they can communicate with AWS services.

These tests allow you to debug in your IDE your AWS Lambda function.

Integration tests can be found under the ``tests/integration`` folder.

You can run the tests by using the following command: ``make unit``

## **E2E Tests**
Make sure you deploy the stack first.

E2E tests can be found under the ``tests/e2e`` folder.

These tests send a 'POST' message to the deployed API GW and trigger the Lambda function on AWS.

The tests are run automatically by: ``make e2e``


## **Deleting the stack**
CDK destroy can be run with ``make destroy``

## **Preparing Code for PR**
Run ``make pr``. This command will run all the required checks, pre commit hooks, linters, code formats, pylint and tests, so you can be sure GitHub's pipeline will pass.

The command auto fixes errors in the code for you.

If there's an error in the pre-commit stage, it gets auto fixed. However, are required to run ``make pr`` again so it continues to the next stages.

Be sure to commit all the changes that ``make pr`` does.

## **GitHub Pages Documentation**
``make docs`` can be run to start a local HTTP server with the project's documentation pages.

## **Building dev/lambda_requirements.txt**
### lambda_requirements.txt
This command is used during ``make pr`` to generate a requirements.txt files for CDK Lambda layer creation (lambda_requirements.txt).

CDK requires a requirements.txt in order to create a zip file with the Lambda layer dependencies. It's based on the project's Pipfile.lock file.

Due to a bug in CDK zip creation, it doesn't work with Pipfile.lock file but only with lambda_requirements.txt.

This command will generate the required file out of the Pipfile.lock file. It's important to commit this file when you update your Pipfile.

Make sure to run  ``make pr`` or ``make deploy`` or so the file is updated.

### dev_requirements.txt
This file is used during GitHub CI to install all the required Python libraries without using pipenv.

File contents are created out of the Pipfile.lock.

Make sure to run  ``make pr`` or ``make deploy`` so the file is updated.
