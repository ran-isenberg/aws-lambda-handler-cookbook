---
title: CI/CD Pipeline
description: AWS Lambda Cookbook - Elevate Your Handler's Code Python pipeline
---

## **CI/CD Pipeline**

The GitHub CI/CD pipeline includes the following steps.

The pipelines uses environment secrets (under the defined environment dev) for code coverage and for the role to deploy to AWS.

When you clone this repository or use the [cookiecutter variation](https://github.com/ran-isenberg/cookiecutter-serverless-python), be sure to define an environment in your [repo settings](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) and add two environment secrets:

1. AWS_ROLE - to role to assume for your GitHub worker as defined [here](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) .
2. CODECOV_TOKEN - for [code coverage integration](https://app.codecov.io/).

### Makefile Commands

All steps can be run locally using the makefile. See details below:

- Create Python environment
- Install dev dependencies
- Run pre-commit checks as defined in `.pre-commit-config.yaml`
- Lint with flake8 as defined in `.flake8` - run `make lint` in the IDE
- Static type check with mypy as defined in `.mypy.ini` - run `make mypy-lint` in the IDE
- Verify that Python imports are sorted according to standard - run `make sort` in the IDE
- Python formatter Yapf as defined in `.style`  - run `make yapf` in the IDE
- Python complexity checks: radon and xenon  - run `make complex` in the IDE
- Unit tests. Run `make unit` to run unit tests in the IDE
- Infrastructure test. Run `make infra-tests` to run the CDK infrastructure tests in the IDE
- Code coverage by [codecov.io](https://about.codecov.io/)
- Deploy CDK - run `make deploy` in the IDE, will also run security tests based on cdk_nag
- E2E tests  - run `make e2e` in the IDE
- Code coverage tests  - run `make coverage-tests` in the IDE after CDK dep
- Update GitHub documentation branch

### Other Capabilities

- Automatic Python dependencies update with Dependabot
- Easy to use makefile allows to run locally all commands in the GitHub actions
- Run local docs server, prior to push in pipeline - run `make docs`  in the IDE
- Prepare PR, run all checks with one command - run `make pr` in the IDE
