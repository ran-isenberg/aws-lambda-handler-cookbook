.PHONY: dev lint mypy-lint complex coverage pre-commit sort deploy destroy deps unit infra-tests integration e2e coverage-tests docs lint-docs build format format-fix compare-openapi openapi pr watch update-deps
PYTHON := ".venv/bin/python3"
.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env

OPENAPI_DIR := ./docs/swagger
CURRENT_OPENAPI := $(OPENAPI_DIR)/openapi.json
LATEST_OPENAPI := openapi_latest.json


dev:
	pip install --upgrade pip pre-commit uv
	pre-commit install
	uv sync
	npm ci

format:
	uv run ruff check . --fix

format-fix:
	uv run ruff format .

lint: format
	@echo "Running mypy"
	$(MAKE) mypy-lint

complex:
	@echo "Running Radon"
	uv run radon cc -e 'tests/*,cdk.out/*,node_modules/*' .
	@echo "Running xenon"
	uv run xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*,node_modules/*' .

pre-commit:
	uv run pre-commit run -a --show-diff-on-failure

mypy-lint:
	uv run mypy --pretty service cdk tests

deps:
	uv export --no-dev --no-editable --no-emit-project --no-color --format=requirements-txt > lambda_requirements.txt
	uv export --no-editable --no-emit-project --no-color --format=requirements-txt > dev_requirements.txt

unit:
	uv run pytest tests/unit  --cov-config=.coveragerc --cov=service --cov-report xml

build: deps
	mkdir -p .build/lambdas ; cp -r service .build/lambdas
	mkdir -p .build/common_layer ; uv export --no-dev --no-editable --no-emit-project --no-color --format=requirements-txt > .build/common_layer/requirements.txt

infra-tests: build
	uv run pytest tests/infrastructure

integration:
	uv run pytest tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

e2e:
	uv run pytest tests/e2e  --cov-config=.coveragerc --cov=service --cov-report xml

pr: deps format pre-commit complex lint lint-docs unit deploy coverage-tests e2e openapi

coverage-tests:
	uv run pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

deploy: build
	npx cdk deploy --app="${PYTHON} ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="${PYTHON} ${PWD}/app.py" --force

docs:
	uv run mkdocs serve

lint-docs:
	npx markdownlint-cli --fix "docs"

watch:
	npx cdk watch

update-deps:
	@echo "Updating uv dependencies..."
	uv lock --upgrade
	uv sync
	@echo "Updating pre-commit hooks..."
	pre-commit autoupdate
	@echo "Fetching latest CDK version from npm..."
	$(eval LATEST_CDK_VERSION := $(shell npm view aws-cdk version))
	@echo "Found CDK version: $(LATEST_CDK_VERSION)"
	@echo "Updating package.json with latest CDK version..."
	node -e "const fs = require('fs'); const pkg = JSON.parse(fs.readFileSync('package.json')); pkg.dependencies['aws-cdk'] = '$(LATEST_CDK_VERSION)'; fs.writeFileSync('package.json', JSON.stringify(pkg, null, 4));"
	npm i --package-lock-only
	@echo "Installing npm dependencies..."
	npm install
	@echo "All dependencies updated successfully!"

openapi:
	uv run python generate_openapi.py

compare-openapi:
	uv run python generate_openapi.py --out-destination '.' --out-filename 'openapi_latest.json'
	@if cmp --silent $(CURRENT_OPENAPI) $(LATEST_OPENAPI); then \
		rm $(LATEST_OPENAPI); \
		echo "Swagger file is up to date"; \
	else \
		echo "Swagger files are not equal, did you run 'make pr' or 'make openapi'?"; \
		rm $(LATEST_OPENAPI); \
		exit 1; \
	fi
