---
title: CI/CD Pipeline
description: AWS Lambda Cookbook - Elevate Your Handler's Code Python pipeline
---

## **CI/CD Pipeline**

The GitHub CI/CD pipeline includes the following steps.

All steps can be run locally using the makefile. See details below:

- Create Python environment
- Install dev dependencies
- Run pre-commit checks as defined in `.pre-commit-config.yaml`
- Lint with flake8 as defined in `.flake8` - run `make lint` in the IDE
- Verify that Python imports are sorted according to standard - run `make sort` in the IDE
- Python formatter Yapf as defined in `.style`  - run `make yapf` in the IDE
- Python complexity checks: radon and xenon  - run `make complex` in the IDE
- Unit tests. Run `make unit` to run unit tests in the IDE
- Code coverage by [codecov.io](https://about.codecov.io/)
- Deploy CDK - not run in GitHub yet (add your own AWS secrets), can be run locally at this moment - run `make deploy` in the IDE
- E2E tests  - not run in GitHub yet (add your own AWS secrets), can be run locally at this moment - run `make e2e` in the IDE
- Update GitHub documentation branch


### Other Capabilities

- Automatic Python dependencies update with Dependabot
- Easy to use makefile allows to run locally all commands in the GitHub actions
- Run local docs server, prior to push in pipeline - run `make docs`  in the IDE
- Prepare PR, run all checks with one command - run `make pr` in the IDE
