# Windows Makefile Contents

```makefile
.PHONY: init dev lint deploy deploy-version version test coverage
.DEFAULT_GOAL := help

init: ## Init the project, install dependencies
	python3 -m pip install --upgrade pip
	pip3 install poetry
	poetry install
	poetry shell

test: ## Run tests
	python -m pytest tests/unit/ -v

lint: ## Run lint
	pre-commit run --all-files
	npm run lint

deploy: ## Deploy service
	npx cdk deploy --all

deploy-version: ## Deploy with version
	@if [ -z ${version} ]; then\
		echo "Please provide a version";\
		exit 1;\
	fi
	npx cdk deploy --all --parameters ServiceVersion=${version}

version: ## Version service
	echo "Version: ${version}"
	sed -i'.orig' -e 's/"service_version": "[0-9]*\.[0-9]*\.[0-9]*"/"service_version": "${version}"/g' cdk.json

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  init:    Init the project, install dependencies"
	@echo "  test:    Run tests"
	@echo "  lint:    Run lint"
	@echo "  deploy:  Deploy service"
	@echo "  deploy-version: Deploy with version"
	@echo "  version: Version service"
```