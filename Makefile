.PHONY: dev lint mypy-lint complex coverage pre-commit sort deploy destroy deps unit infra-tests integration e2e coverage-tests docs lint-docs build format format-fix compare-openapi openapi pr watch update-deps emulator-install emulator-start emulator-run emulator-stop emulator-check publish-docs
PYTHON := ".venv/bin/python3"

EMULATOR_PORT ?= 9297
EMULATOR_IMAGE := aws-emulator
EMULATOR_CONTAINER := aws-emulator-$(EMULATOR_PORT)
EMULATOR_DIR := $(HOME)/.aws/emulator/$(EMULATOR_PORT)
EMULATOR_LOG := $(HOME)/.aws/emulator/$(EMULATOR_PORT).log
EMULATOR_CONFIG := $(CURDIR)/emulator/config.toml
# Linux (CI): the Debian package installs here and doesn't add itself to PATH. Only an LTS/latest URL is published.
EMULATOR_BIN := /opt/aws-emulator/bin/aws-emulator
EMULATOR_DEB_URL := https://downloads.aws.com/aws-emulator/packages/aws-emulator/LTS/latest/aws-emulator
EMULATOR_LOGS := if [ "$$(uname)" = "Darwin" ]; then docker logs $(EMULATOR_CONTAINER) 2>&1; else cat $(EMULATOR_LOG); fi
EMULATOR_HEALTH := curl -sf --cacert $(EMULATOR_DIR)/ca.pem https://127.0.0.1:$(EMULATOR_PORT)/__admin/health
# Test runs against the emulator: its endpoint, per-run credentials and CA. Real AWS credentials are removed,
# so a misconfigured run can't reach a real account. pydynox (AWS SDK for Rust) reads SSL_CERT_FILE, not AWS_CA_BUNDLE.
EMULATOR_ENV := env -u AWS_PROFILE -u AWS_DEFAULT_PROFILE -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY -u AWS_SESSION_TOKEN \
	AWS_ENDPOINT_URL=https://127.0.0.1:$(EMULATOR_PORT) \
	AWS_CA_BUNDLE=$(EMULATOR_DIR)/ca.pem \
	SSL_CERT_FILE=$(EMULATOR_DIR)/ca.pem \
	AWS_SHARED_CREDENTIALS_FILE=$(EMULATOR_DIR)/emulator_credentials \
	AWS_CONFIG_FILE=$(EMULATOR_DIR)/config \
	AWS_EC2_METADATA_DISABLED=true \
	AWS_DISABLE_HOST_PREFIX_INJECTION=true \
	AWS_REGION=us-east-1 \
	AWS_DEFAULT_REGION=us-east-1
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
	$(EMULATOR_ENV) uv run pytest tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

e2e:
	uv run pytest tests/e2e  --cov-config=.coveragerc --cov=service --cov-report xml

pr: deps format pre-commit complex lint lint-docs unit infra-tests emulator-start coverage-tests emulator-stop deploy e2e openapi

coverage-tests:
	$(EMULATOR_ENV) uv run pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

deploy: build
	npx cdk deploy --app="${PYTHON} ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="${PYTHON} ${PWD}/app.py" --force

docs:
	uv run zensical serve

publish-docs:
	uv run zensical build --clean

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

# --- AWS Emulator (local AWS APIs over HTTPS on 127.0.0.1) ---
# Darwin: build the Docker image (no native package). Linux (CI): install the latest Debian package with sudo.
# sha256sum only logs which build was installed: there is no published checksum to verify against.
emulator-install:
	if [ "$$(uname)" = "Darwin" ]; then \
		docker build --pull --no-cache -t $(EMULATOR_IMAGE) emulator; \
	else \
		deb="$$(mktemp -d)/aws-emulator.deb" && \
		curl -fsSLo "$$deb" "$(EMULATOR_DEB_URL)_$$(dpkg --print-architecture).deb" && \
		sha256sum "$$deb" && \
		sudo apt-get install -y "$$deb" && \
		$(EMULATOR_BIN) -v; \
	fi

# Darwin: in Docker (no native package). Linux: the installed aws-emulator package (CI). No-op when already up.
# Each step is one shell command: macOS ships GNU Make 3.81, which ignores .ONESHELL.
emulator-start:
	@if $(EMULATOR_HEALTH) >/dev/null 2>&1; then echo "AWS Emulator already running on port $(EMULATOR_PORT)"; else $(MAKE) emulator-run; fi

emulator-run:
	mkdir -p $(EMULATOR_DIR)
	if [ "$$(uname)" = "Darwin" ]; then \
		docker network create aws-emulator 2>/dev/null || true; \
		docker run -d --rm --name $(EMULATOR_CONTAINER) \
			--network aws-emulator \
			--cap-drop ALL --security-opt no-new-privileges --read-only \
			-e EMULATOR_TELEMETRY=off \
			-e EMULATOR_CONFIG=/etc/aws-emulator/config.toml \
			-v "$(EMULATOR_CONFIG):/etc/aws-emulator/config.toml:ro" \
			-p 127.0.0.1:$(EMULATOR_PORT):$(EMULATOR_PORT) \
			-v "$(EMULATOR_DIR):/home/emulator/.aws/emulator/$(EMULATOR_PORT)" \
			$(EMULATOR_IMAGE) -p $(EMULATOR_PORT) --idle-timeout 3600 || exit 1; \
	else \
		EMULATOR_CONFIG=$(EMULATOR_CONFIG) nohup $(EMULATOR_BIN) -p $(EMULATOR_PORT) --idle-timeout 3600 > $(EMULATOR_LOG) 2>&1 & \
	fi
	for i in $$(seq 60); do $(EMULATOR_HEALTH) >/dev/null 2>&1 && break; sleep 1; done
	$(MAKE) emulator-check

# Fails unless the emulator is healthy and its startup notice reports telemetry disabled.
emulator-check:
	$(EMULATOR_HEALTH) || { $(EMULATOR_LOGS); exit 1; }
	@echo
	($(EMULATOR_LOGS)) | grep -i "telemetry: disabled" || { echo "AWS Emulator telemetry is not disabled"; $(EMULATOR_LOGS); exit 1; }

emulator-stop:
	if [ "$$(uname)" = "Darwin" ]; then docker stop $(EMULATOR_CONTAINER) || true; else pkill -x aws-emulator || true; fi

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
