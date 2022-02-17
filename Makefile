.PHONY: dev lint complex coverage pre-commit yapf sort



dev:
	pipenv install --dev

lint:
	@echo "Running flake8"
	flake8 service/* tests/*

coverage:
	pytest --cov

complex:
	@echo "Running Radon"
	radon cc -e 'tests/*,cdk.out/*' .
	@echo "Running xenon"
	xenon --max-absolute B --max-modules A --max-average A -e 'tests/*,.venv/*,cdk.out/*' .

sort:
	isort ${PWD}

pre-commit:
	pre-commit run -a

pr: yapf sort pre-commit complex lint coverage

yapf:
	yapf -i -vv --style=./.style --exclude=.venv --exclude=.build --exclude=cdk.out --exclude=.git  -r .
