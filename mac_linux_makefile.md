# Mac/Linux Makefile Contents

```makefile
.PHONY: init dev lint deploy deploy-watch deploy-version version test coverage
.DEFAULT_GOAL := help

## @init: Target for initial setup
init: ## Init the project, install dependencies
	echo ${PYTHONPATH}
	pip install -U pip
	pip install pipenv
	pip install poetry
	poetry shell
	poetry install --no-root


## @test: Target for running tests
test:  ## Run tests
	python -m pytest tests/unit/ -v


## @dev: Target for development
dev:  ## Run dev server
	npm run dev

## @lint: Target for linting
lint:  ## Run linting
	pre-commit run --all-files
	npm run lint


## @deploy: Target for deployment
deploy:  ## Deploy service
	npx cdk deploy --all


## @deploy-watch: Target for deployment with watch
deploy-watch:  ## Deploy service with watch
	npx cdk watch --all


## @deploy-version: Target for deployment with version
deploy-version:  ## Deploy with version
	npx cdk deploy --all --parameters ServiceVersion=${version}


## @version: Target for versioning
version:  ## Version service
	@if [ -z ${version} ]; then\
		echo "Please provide a version";\
		exit 1;\
	fi
	echo "Version: ${version}"
	sed -i'.orig' -e 's/"service_version": "[0-9]*\.[0-9]*\.[0-9]*"/"service_version": "${version}"/g' cdk.json


## @help: Target for help
help:  ## Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^##\s+@(.+):' $(MAKEFILE_LIST) | sed -e 's/##\s\+\(@.+\): \([^:]*\):/\1|\2/' -E -e 's/^@(.*)/(\\033[36m\1\\033[0m)/' | column -t -s "|"
	@echo ""
	@echo "Detailed help:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-30s\\033[0m %s\n", $$1, $$2}'
```