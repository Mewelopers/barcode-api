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
	@echo "Formatting code"
	@black . || true

lint:
	@echo "Linting code"
	@ruff . || true

typecheck:
	@echo "Type checking code"
	@mypy . || true

sort:
	@echo "Sorting imports"
	@isort . || true

check: lint typecheck

dev:
	@echo "Starting ASGI server in watch mode"
	@uvicorn barcode_api.app:app --reload

start:
	@echo "Starting ASGI server"
	@python -m barcode_api

migrate:
	@echo "Running migrations"
	alembic upgrade head

make-migrations:
	@echo "Generating migrations"
	alembic revision --autogenerate -m "$(message)"
