.PHONY: dev lint complex coverage pre-commit sort deploy destroy deps unit infra-tests integration e2e coverage-tests docs lint-docs build format compare-openapi openapi
PYTHON := ".venv/bin/python3"
.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env

OPENAPI_DIR := ./docs/swagger
CURRENT_OPENAPI := $(OPENAPI_DIR)/openapi.json
LATEST_OPENAPI := openapi_latest.json


dev:
	pip install --upgrade pip pre-commit poetry
	pre-commit install
# ensures poetry creates a local virtualenv (.venv)
	poetry config --local virtualenvs.in-project true
	poetry install --no-root
	npm ci

format:
	poetry run ruff check . --fix

format-fix:
	poetry run ruff format .

lint: format
	@echo "Running mypy"
	$(MAKE) mypy-lint

complex:
	@echo "Running Radon"
	poetry run radon cc -e 'tests/*,cdk.out/*,node_modules/*' .
	@echo "Running xenon"
	poetry run xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*,node_modules/*' .

pre-commit:
	poetry run pre-commit run -a --show-diff-on-failure

mypy-lint:
	poetry run mypy --pretty service cdk tests

deps:
	poetry export --only=dev --format=requirements.txt > dev_requirements.txt
	poetry export --without=dev --format=requirements.txt > lambda_requirements.txt

unit:
	poetry run pytest tests/unit  --cov-config=.coveragerc --cov=service --cov-report xml

build: deps
	mkdir -p .build/lambdas ; cp -r service .build/lambdas
	mkdir -p .build/common_layer ; poetry export --without=dev --format=requirements.txt > .build/common_layer/requirements.txt

infra-tests: build
	poetry run pytest tests/infrastructure

integration:
	poetry run pytest tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

e2e:
	poetry run pytest tests/e2e  --cov-config=.coveragerc --cov=service --cov-report xml

pr: deps format pre-commit complex lint lint-docs unit deploy coverage-tests e2e openapi

coverage-tests:
	poetry run pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

deploy: build
	npx cdk deploy --app="${PYTHON} ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="${PYTHON} ${PWD}/app.py" --force

docs:
	poetry run mkdocs serve

lint-docs:
	docker run -v ${PWD}:/markdown 06kellyjac/markdownlint-cli --fix "docs"

watch:
	npx cdk watch

update-deps:
	poetry update
	pre-commit autoupdate
	npm i --package-lock-only

openapi:
	poetry run python generate_openapi.py

compare-openapi:
	poetry run python generate_openapi.py --out-destination '.' --out-filename 'openapi_latest.json'
	@if cmp --silent $(CURRENT_OPENAPI) $(LATEST_OPENAPI); then \
		rm $(LATEST_OPENAPI); \
		echo "Swagger file is up to date"; \
	else \
		echo "Swagger files are not equal, did you run 'make pr' or 'make openapi'?"; \
		rm $(LATEST_OPENAPI); \
		exit 1; \
	fi
