---
title: Getting Started
description: AWS Lambda Cookbook Project Getting started
---
## **Prerequisites**

* **Docker** - install [Docker](https://www.docker.com/){target="_blank"}. Required for the Lambda layer packaging process.
* **[AWS CDK](cdk.md)** - Required for synth & deploying the AWS Cloudformation stack.
* Python 3.11
* [poetry](https://pypi.org/project/poetry/){target="_blank"} - Make sure to run ``poetry config --local virtualenvs.in-project true`` so all dependencies are installed in the project '.venv' folder.
* For Windows based machines, use the Makefile_windows version (rename to Makefile). Default Makefile is for Mac/Linux.

## Getting Started

You can start with a clean service out of this template repository without using the 'Template' button on GitHub.

You can use Cookiecutter.

* Cookiecutter - install with pip/brew ``brew install cookiecutter`` or ``pip install cookiecutter`

Then run:

**[`cookiecutter gh:ran-isenberg/cookiecutter-serverless-python`](#){: .copyMe}:clipboard:**

Answer the questions to select repo name, service name, etc.:

![logo](https://github.com/ran-isenberg/cookiecutter-serverless-python/blob/main/media/howto.png?raw=true)

**That's it, your developer environment has been set! you are ready to deploy the service:**

## **Creating a Developer Environment (without cookiecutter)**

1. Run ``make dev``

## **Deploy CDK**

Create a cloudformation stack by running ``make deploy``.

## **Unit Tests**

Unit tests can be found under the ``tests/unit`` folder.

You can run the tests by using the following command: ``make unit``.

## **Integration Tests**

Make sure you deploy the stack first as these tests trigger your lambda handler LOCALLY but they can communicate with AWS services.

These tests allow you to debug in your IDE your AWS Lambda function.

Integration tests can be found under the ``tests/integration`` folder.

You can run the tests by using the following command: ``make integration``.

## **E2E Tests**

Make sure you deploy the stack first.

E2E tests can be found under the ``tests/e2e`` folder.

These tests send a 'POST' message to the deployed API GW and trigger the Lambda function on AWS.

The tests are run automatically by: ``make e2e``.

## **Deleting the stack**

CDK destroy can be run with ``make destroy``.

## **Preparing Code for PR**

Run ``make pr``. This command will run all the required checks, pre commit hooks, linters, code formatters, import sorting and tests, so you can be sure GitHub's pipeline will pass.

The command auto fixes errors in the code for you.

If there's an error in the pre-commit stage, it gets auto fixed. However, are required to run ``make pr`` again so it continues to the next stages.

Be sure to commit all the changes that ``make pr`` does for you.

## **GitHub Pages Documentation**

``make docs`` can be run to start a local HTTP server with the project's documentation pages.

## **Building dev/lambda_requirements.txt**

### lambda_requirements.txt

CDK requires a requirements.txt in order to create a zip file with the Lambda layer dependencies. It's based on the project's poetry.lock file.

``make deploy`` command will generate it automatically for you.

### dev_requirements.txt

This file is used during GitHub CI to install all the required Python libraries without using poetry.

File contents are created out of the Pipfile.lock.

``make deploy`` and ``make deps`` are commands generate it automatically.
