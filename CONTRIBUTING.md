<!-- markdownlint-disable MD043 MD041 -->
# Table of contents <!-- omit in toc -->

- [Contributing Guidelines](#contributing-guidelines)
  - [Reporting Bugs/Feature Requests](#reporting-bugsfeature-requests)
  - [Contributing via Pull Requests](#contributing-via-pull-requests)
    - [Dev setup](#dev-setup)

# Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional
documentation, we greatly value feedback and contributions from our community.

Please read through this document before submitting any issues or pull requests to ensure we have all the necessary
information to effectively respond to your bug report or contribution.

## Reporting Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs, suggest features, or documentation improvements.

When filing an issue, please check existing open, or recently closed, issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can.

## Contributing via Pull Requests

Contributions via pull requests are much appreciated. Before sending us a pull request, please ensure that:

1. You are working against the latest source on the **main** branch.
2. You check existing open, and recently merged pull requests to make sure someone else hasn't addressed the problem already.
3. You open an [issue](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/issues) before you begin any implementation. We value your time and bandwidth. As such, any pull requests created on non-triaged issues might not be successful.

### Dev setup

[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/from-referrer/)

Firstly, [fork the repository](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/fork).


use `make dev` within your local virtual environment.
For more information on getting started check out the [official documentation](https://ran-isenberg.github.io/aws-lambda-handler-cookbook/getting_started/)

To send us a pull request, please follow these steps:

1. Create a new branch to focus on the specific change you are contributing e.g. `improve/service_logic`
2. Run all tests, and code baseline checks: `make pr`
    - Git hooks will run linting and formatting while `make pr` run deep checks that also run in the CI process
3. Commit to your fork using clear commit messages.
4. Open an issue in the repository and wait for feedback. We will to respond within a few days, please be patient.
5. Once the issue is agreed to be implemented, open a PR.

GitHub provides additional document on [forking a repository](https://help.github.com/articles/fork-a-repo/) and
[creating a pull request](https://help.github.com/articles/creating-a-pull-request/).
