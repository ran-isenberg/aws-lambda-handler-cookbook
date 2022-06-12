.PHONY: dev lint complex coverage pre-commit yapf sort deploy destroy deps unit integration e2e pipeline-tests docs



dev:
	pipenv install --dev
	make deps

lint:
	@echo "Running flake8"
	flake8 service/* tests/* docs/examples/*

complex:
	@echo "Running Radon"
	radon cc -e 'tests/*,cdk.out/*' .
	@echo "Running xenon"
	xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*' .

sort:
	isort ${PWD}

pre-commit:
	pre-commit run -a

deps:
	pipenv lock -r -d > dev_requirements.txt
	pipenv lock -r  > lambda_requirements.txt

unit:
	pytest tests/unit  --cov-config=.coveragerc --cov=service --cov-report xml

integration:
	pytest tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

e2e:
	pytest tests/e2e  --cov-config=.coveragerc --cov=service --cov-report xml

pr: deps yapf sort pre-commit complex lint unit integration e2e

yapf:
	yapf -i -vv --style=./.style --exclude=.venv --exclude=.build --exclude=cdk.out --exclude=.git  -r .

pipeline-tests:
	pytest tests/unit tests/integration  --cov-config=.coveragerc --cov=service --cov-report xml

deploy:
	make deps
	mkdir -p .build/lambdas ; cp -r service .build/lambdas
	mkdir -p .build/common_layer ; pipenv lock -r > .build/common_layer/requirements.txt
	cdk deploy --app="python3 ${PWD}/cdk/aws_lambda_handler_cookbook/app.py" -require-approval=True

destroy:
	cdk destroy --app="python3 ${PWD}/cdk/aws_lambda_handler_cookbook/app.py" -require-approval=True

docs:
	mkdocs serve
