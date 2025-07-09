.PHONY: test
test:
	uv run pytest

.PHONY: run
run:
	uv run python -m src.snipster.main

.PHONY: lint
lint:
	uv run ruff check src

.PHONY: install
install:
	uv sync

.PHONY: install-dev
install-dev:
	uv sync --dev

.PHONY: cov
cov:
	uv run pytest --cov=src --cov-report=term-missing
