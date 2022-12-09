.PHONY: dev lint complex coverage pre-commit yapf sort deploy destroy deps unit integration e2e pipeline-tests docs lint-docs



dev:
	pipenv install -d
	make deps

lint:
	@echo "Running flake8"
	flake8 service/* cdk/* tests/* docs/examples/* --exclude patterns='build,cdk.json,cdk.context.json,.yaml'

complex:
	@echo "Running Radon"
	radon cc -e 'tests/*,cdk.out/*' .
	@echo "Running xenon"
	xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*' .

sort:
	isort ${PWD}

pre-commit:
	pre-commit run -a --show-diff-on-failure

deps:
	pipenv requirements --dev > dev_requirements.txt
	pipenv requirements  > lambda_requirements.txt

unit:
	pytest tests/unit  --cov-config=.coveragerc --cov=service --cov-report xml

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
	make deps
	mkdir -p .build/lambdas ; cp -r service .build/lambdas
	mkdir -p .build/common_layer ; pipenv requirements > .build/common_layer/requirements.txt
	cdk deploy --app="python3 ${PWD}/cdk/my_service/app.py" --require-approval=never

destroy:
	cdk destroy --app="python3 ${PWD}/cdk/my_service/app.py" --force

docs:
	mkdocs serve

lint-docs:
	docker run -v ${PWD}:/markdown 06kellyjac/markdownlint-cli --fix "docs"
