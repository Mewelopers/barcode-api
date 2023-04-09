.PHONY: gen_requirements

gen_requirements:
	@echo "Generating requirements.txt"
	python -m piptools compile -o requirements.txt pyproject.toml

	@echo "Generating requirements-dev.txt"
	python -m piptools compile --extra dev -o requirements-dev.txt pyproject.toml

install:
	pip install -r requirements.txt .

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt --editable .

hooks:
	pre-commit install

format:
	black .

lint:
	ruff .
	mypy .
