---
title: Changelog
description: AWS Lambda Handler Cookbook - Release History
---

All notable changes to this project are documented in GitHub Releases.

## Versioning

This project follows [Semantic Versioning](https://semver.org/){:target="_blank"}:

- **MAJOR** version for breaking changes
- **MINOR** version for new features (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

## Release Process

Releases are automatically created when PRs are merged to main:

1. **PR Labeling** - PRs are automatically labeled based on commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`)
2. **Version Bump** - Version is determined by commit analysis or `pyproject.toml`
3. **Release Notes** - Auto-generated from merged PRs, categorized by labels

See the [Pipeline documentation](pipeline.md#create_release) for details.
