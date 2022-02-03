.PHONY: dev lint complex pre-commit yapf



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


pre-commit:
	pre-commit run -a

pr: yapf pre-commit complex lint coverage

yapf:
	yapf -i -vv --style=./.style --exclude=.venv --exclude=.build --exclude=cdk.out --exclude=.git  -r .
