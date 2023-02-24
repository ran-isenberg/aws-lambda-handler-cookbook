.PHONY: dev lint complex coverage pre-commit yapf sort deploy destroy deps unit infra-tests integration e2e pipeline-tests docs lint-docs build



dev:
	pip install --upgrade pip pre-commit poetry
	make deps
	pre-commit install
	poetry shell

lint:
	@echo "Running flake8"
	flake8 service/* cdk/* tests/* docs/examples/* --exclude patterns='build,cdk.json,cdk.context.json,.yaml'
	@echo "Running mypy"
	make mypy-lint

complex:
	@echo "Running Radon"
	radon cc -e 'tests/*,cdk.out/*' .
	@echo "Running xenon"
	xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*' .

sort:
	isort ${PWD}

pre-commit:
	pre-commit run -a --show-diff-on-failure

mypy-lint:
	mypy --pretty service docs/examples cdk tests

deps:
	poetry export --only=dev --without-hashes --format=requirements.txt > dev_requirements.txt
	poetry export --without=dev --without-hashes --format=requirements.txt > lambda_requirements.txt

unit:
	pytest tests/unit  --cov-config=.coveragerc --cov=service --cov-report xml

build:
	make deps
	mkdir -p .build/lambdas ; cp -r service .build/lambdas
	mkdir -p .build/common_layer ; poetry export --without=dev --without-hashes --format=requirements.txt > .build/common_layer/requirements.txt

infra-tests:
	make build
	pytest tests/infrastructure

integration:
	pytest tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

e2e:
	pytest tests/e2e  --cov-config=.coveragerc --cov=service --cov-report xml

pr: deps yapf sort pre-commit complex lint lint-docs unit deploy integration e2e

yapf:
	yapf -i -vv --style=./.style --exclude=.venv --exclude=.build --exclude=cdk.out --exclude=.git  -r .

pipeline-tests:
	pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

deploy:
	make build
	cdk deploy --app="python3 ${PWD}/app.py" --require-approval=never

destroy:
	cdk destroy --app="python3 ${PWD}/app.py" --force

docs:
	mkdocs serve

lint-docs:
	docker run -v ${PWD}:/markdown 06kellyjac/markdownlint-cli --fix "docs"
