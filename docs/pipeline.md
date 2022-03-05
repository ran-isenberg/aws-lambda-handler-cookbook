---
title: Pipeline
description: AWS Lambda Cookbook - Elevate Your Handler's Code Python pipeline
---
The GitHub CI/CD pipeline includes the following steps:

- Create Python environment
- Install dev dependencies
- Run pre-commit checks as defined in `.pre-commit-config.yaml`
- Lint with flake8 as defined in `.flake8`
- Python formatter yapf as defined in `.style`
- Python complexity checks: radon and xenon
- Unit tests
- Code coverage by [codecov.io](https://about.codecov.io/)
- Deploy CDK - not run in GitHub yet, can be run locally at this moment - `make deploy`
- E2E tests  - not run in GitHub yet, can be run locally at this moment - `make e2e`
- Publish documentation
