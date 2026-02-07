---
title: Contributing
description: How to contribute to the AWS Lambda Handler Cookbook
---

Thank you for your interest in contributing to AWS Lambda Handler Cookbook! Whether it's a bug report, new feature, correction, or additional documentation, we greatly value feedback and contributions from our community.

## Quick Start

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/aws-lambda-handler-cookbook.git
cd aws-lambda-handler-cookbook

# Set up development environment
make dev

# Run all checks before submitting
make pr
```

## Reporting Bugs/Feature Requests

!!! tip "Before Opening an Issue"
    Check existing [open issues](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/issues){:target="_blank"} to avoid duplicates.

Use the GitHub issue tracker to:

- :bug: Report bugs
- :sparkles: Suggest new features
- :book: Propose documentation improvements

## Contributing via Pull Requests

!!! warning "Open an Issue First"
    Please open an [issue](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/issues){:target="_blank"} before starting implementation. This ensures alignment and saves your time.

### Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your change (e.g., `feature/add-new-utility`)
3. **Make your changes** following the code style
4. **Run checks**: `make pr`
5. **Commit** with [conventional commit](https://www.conventionalcommits.org/){:target="_blank"} messages:
    - `feat:` for new features
    - `fix:` for bug fixes
    - `docs:` for documentation
    - `chore:` for maintenance
6. **Open a Pull Request**

### Commit Message Format

```text
<type>: <description>

[optional body]
```

Examples:

```text
feat: add retry mechanism for DynamoDB operations
fix: handle empty response from AppConfig
docs: update getting started guide
```

## Development Setup

[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/from-referrer/){:target="_blank"}

### Local Development

```bash
# Install dependencies
make dev

# Run tests
make unit
make integration
make e2e

# Run all PR checks
make pr

# Start local docs server
make docs
```

### Makefile Commands

| Command            | Description                         |
| ------------------ | ----------------------------------- |
| `make dev`         | Set up development environment      |
| `make pr`          | Run all checks before PR submission |
| `make unit`        | Run unit tests                      |
| `make integration` | Run integration tests               |
| `make e2e`         | Run end-to-end tests                |
| `make lint`        | Run linting and type checks         |
| `make format`      | Format code                         |
| `make docs`        | Start local documentation server    |

## Code of Conduct

Please read our [Code of Conduct](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/CODE_OF_CONDUCT.md){:target="_blank"} before contributing.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](https://github.com/ran-isenberg/aws-lambda-handler-cookbook/blob/main/LICENSE){:target="_blank"}.
