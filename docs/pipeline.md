---
title: CI/CD Pipeline
description: AWS Lambda Cookbook - Elevate Your Handler's Code Python pipeline
---

## **Getting Started**

The GitHub CI/CD pipeline includes the following steps.

!!! warning "Required Configuration"
    The deploy jobs use environment secrets (under the defined environment 'dev', 'staging' and 'production') for the role to deploy to AWS. The 'integration' jobs use no environment, so they never wait for an approval: they run against a local AWS Emulator, get no AWS credentials, and read `CODECOV_TOKEN` as a repository secret.

When you clone this repository be sure to define the environments in your [repo settings](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) and create a secret per environment:

- `AWS_ROLE_ARN` - the role ARN to assume for your GitHub worker as defined in the [GitHub OIDC documentation for AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

!!! tip "Quick Start"
    Run `make pr` locally to validate all checks before pushing. This runs the same checks as the CI pipeline.

### **Makefile Commands**

All steps can be run locally using the makefile. See details below:

- Create Python environment
- Install dev dependencies
- Run pre-commit checks as defined in `.pre-commit-config.yaml`
- Lint and format and sort imports with ruff (similar to flake8/yapf/isort) - run `make format` in the IDE
- Static type check with mypy as defined in `.mypy.ini` - run `make lint` in the IDE
- Verify that Python imports are sorted according to standard - run `make sort` in the IDE
- Python complexity checks: radon and xenon  - run `make complex` in the IDE
- Unit tests. Run `make unit` to run unit tests in the IDE
- Infrastructure test. Run `make infra-tests` to run the CDK infrastructure tests in the IDE
- Integration tests - run `make emulator-start`, then `make integration` in the IDE. They run against a local AWS Emulator, no AWS account needed. Stop it with `make emulator-stop`.
- Code coverage tests (unit + integration, against the AWS Emulator) - run `make coverage-tests` in the IDE, reported to [codecov.io](https://about.codecov.io/)
- Deploy CDK - run `make deploy` in the IDE, will also run security tests based on cdk_nag
- E2E tests  - run `make e2e` in the IDE, against the deployed stack
- OpenAPI Swagger file - run
- Update GitHub documentation branch
- Update dependencies and CDK version automatically to the latest versions: run `make update-deps`.

### **Other Capabilities**

- Automatic Python dependencies update with Dependabot
- Easy to use makefile allows to run locally all commands in the GitHub actions
- Run local docs server, prior to push in pipeline - run `make docs`  in the IDE
- Prepare PR, run all checks with one command - run `make pr` in the IDE

## **Environments & Pipelines**

All GitHub workflows are stored under `.github/workflows` folder.

The two most important ones are `pr-serverless-service`  and `main-serverless-service`.

### **pr-serverless-service**

```mermaid
flowchart LR
    subgraph PR["Pull Request Opened"]
        direction TB
        A[PR Created]
    end

    subgraph QS["quality_standards"]
        direction TB
        B1[Checkout] --> B2[Install uv & Python]
        B2 --> B3[Install Dependencies]
        B3 --> B4[Pre-commit Checks]
        B4 --> B5[Linting & Formatting]
        B5 --> B6[Complexity Scan]
    end

    subgraph Integration["integration (no AWS credentials)"]
        direction TB
        I1[Checkout & Setup] --> I2[Install & Start AWS Emulator]
        I2 --> I3[Unit Tests]
        I3 --> I4[Infrastructure Tests]
        I4 --> I5[Coverage Tests: unit + integration]
        I5 --> I6[Codecov]
    end

    subgraph Tests["deploy_and_e2e (dev environment)"]
        direction TB
        C1[Checkout & Setup] --> C2[Configure AWS OIDC]
        C2 --> C3[Deploy to AWS]
        C3 --> C4[OpenAPI Validation]
        C4 --> C5[E2E Tests]
        C5 --> C6[Destroy Stack]
    end

    PR --> QS
    QS -->|Success| Integration
    Integration -->|Success| Tests
    Tests -->|Success| D[Ready to Merge]

    classDef success fill:#2E7D32,stroke:#1B5E20,color:#fff
    class D success
```

<p class="mermaid-hint">Click diagram to zoom</p>

`pr-serverless-service` runs for every pull request you open. It expects a repository secret `CODECOV_TOKEN` for CodeCov integration, and GitHub environments by the name `dev`, `staging` and `production`, each with an `AWS_ROLE` that allows GitHub to deploy to that AWS account (one for dev, one for staging and one for production accounts).

Only the jobs that deploy use an environment, so a required reviewer on `dev` gates the deploy and E2E tests, not the unit and integration tests.

It includes three jobs: 'quality_standards', 'integration' and 'deploy_and_e2e'. Each job runs only if the previous one passed, and all of them MUST pass in order to be able to merge.

'quality_standards' includes all linters and pre-commit checks.

'integration' runs the unit, infrastructure and integration tests with code coverage. The integration tests run against a local [AWS Emulator](https://docs.aws.amazon.com/emulator/latest/userguide/){:target="_blank" rel="noopener"} installed on the runner, so this job has no AWS credentials, and a failing test stops the pipeline before anything is deployed.

The job fails if the emulator does not report its telemetry as disabled.

'deploy_and_e2e' deploys the service to AWS, checks that your OpenAPI file is up to date and corresponds to the actual deployment (fails if it does not, hence your documentation is out of date), runs security checks and E2E tests.

Stack is destroyed at the end. Stack has a 'dev' prefix as part of its name. Each environment has a pre-defined stack prefix.

Once merged, `main-serverless-service` will run.

### **main-serverless-service**

```mermaid
flowchart LR
    subgraph Trigger["PR Merged to Main"]
        direction TB
        A[Push to main]
    end

    subgraph Integration["integration (no AWS credentials)"]
        direction TB
        I1[Checkout & Setup] --> I2[Install & Start AWS Emulator]
        I2 --> I3[Unit & Infrastructure Tests]
        I3 --> I4[Coverage Tests: unit + integration]
        I4 --> I5[Codecov]
    end

    subgraph Staging["staging"]
        direction TB
        S1[Checkout & Setup] --> S2[Configure AWS OIDC]
        S2 --> S3[Deploy to AWS]
        S3 --> S4[E2E Tests]
    end

    subgraph Production["production"]
        direction TB
        P1[Checkout & Setup] --> P2[Configure AWS OIDC]
        P2 --> P3[Deploy to AWS]
    end

    subgraph Parallel["Post-Production (parallel)"]
        direction TB
        subgraph Docs["publish_github_pages"]
            D1[Generate & Deploy Docs]
        end
        subgraph Release["create_release"]
            R1[Read pyproject.toml version]
            R1 --> R2[Determine semver bump]
            R2 --> R3[Create GitHub Release]
        end
    end

    Trigger --> Integration
    Integration -->|Success| Staging
    Staging -->|Success| Production
    Production -->|Success| Parallel
```

<p class="mermaid-hint">Click diagram to zoom</p>

`main-serverless-service` runs for every MERGED pull request that runs on the main branch. It expects you defined a GitHub environments by the name `staging` and `production` and that both includes a secret by the name of `AWS_ROLE`.

It includes the jobs 'integration', 'staging', 'production', 'publish_github_pages' and 'create_release'.

'integration' is the same job as in the PR pipeline: unit, infrastructure and integration tests against a local AWS Emulator, with code coverage and no AWS credentials.

'staging' does not run any of the 'quality_standards' checks, since they were already checked before the code was merged. It deploys and runs the E2E tests. Stack is not deleted. Stack has a 'staging' prefix as part of its name.
Any failure in staging will stop the pipeline and production environment will not get updated with the new code.

'production' does not run any of the 'quality_standards' checks, since they were already checked before the code was merged. It does not run any test at the moment. Stack is not deleted. Stack has a 'production' prefix as part of its name.

### **create_release**

After successful production deployment, the `create_release` job automatically creates a GitHub release with auto-generated release notes.

**How versioning works:**

1. The job reads the version from `pyproject.toml`
2. If this version hasn't been released yet, it uses it as-is
3. If already released, it analyzes commits since the last tag:
   - Commits with `!:` (e.g., `feat!:`) → **Major** version bump
   - Commits with `feat:` or `feature:` → **Minor** version bump
   - Other commits → **Patch** version bump

Release notes are automatically generated based on the merged PRs and their labels.

---

## **Automatic PR Labeling**

The `pr-labeler` workflow automatically labels PRs based on commit message prefixes following [Conventional Commits](https://www.conventionalcommits.org/).

### **pr-labeler**

This workflow runs on every PR and:

1. **Creates required labels** if they don't exist in the repository
2. **Scans commit messages and PR title** for conventional commit prefixes
3. **Applies matching labels** to the PR

| Commit Prefix                  | Label Applied     | Release Notes Section   |
| ------------------------------ | ----------------- | ----------------------- |
| `feat:` or `feature:`          | `enhancement`     | Exciting New Features 🎉 |
| `fix:`                         | `bug`             | Bug Fixes 🐛             |
| `docs:`                        | `documentation`   | Documentation 📚         |
| `chore:`                       | `chore`           | Maintenance 🔧           |
| `feat!:` or `fix!:` (with `!`) | `breaking-change` | Breaking Changes 🛠      |

### **Release Notes Configuration**

The `.github/release.yml` file configures how GitHub generates release notes. PRs are categorized into sections based on their labels, which are automatically applied by the `pr-labeler` workflow.

This creates a seamless flow:

```text
Commit with prefix → PR gets labeled → PR merged → Release created with categorized notes
```
