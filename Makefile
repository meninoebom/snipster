.PHONY: install
install:
	uv sync

.PHONY: install-dev
install-dev:
	uv sync --dev

.PHONY: init
init: install-dev
	uv run alembic upgrade head

.PHONY: dev
dev: install-dev init
	uv run fastapi dev src/snipster/api.py

.PHONY: cli
cli:
	uv run python -m src.snipster

.PHONY: render-run
render-run: install init
	uv run --active uvicorn snipster.api:app --host 0.0.0.0 --port $PORT

.PHONY: ui
ui:
	cd ui && uv run reflex run

.PHONY: lint
lint:
	uv run ruff check src

.PHONY: lint-fix
lint-fix:
	uv run ruff check src --fix

.PHONY: format
format:
	uv run ruff format src

.PHONY: test
test:
	uv run pytest

.PHONY: cov
cov:
	uv run pytest --cov=src --cov-report=term-missing

.PHONY: clean
clean:
	rm -rf **/__pycache__ .pytest_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
