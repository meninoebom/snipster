FROM python:3.13-slim

WORKDIR /app

# Copy workspace dependencies
COPY pyproject.toml README.md ./
COPY uv.lock ./

# Install uv and dependencies
RUN pip install uv && uv sync --frozen

# Copy backend code and migrations
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

ENV PYTHONPATH=/app/src

# Expose backend port
EXPOSE 8000

# Run migrations then start FastAPI
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn snipster.api:app --host 0.0.0.0 --port 8000"]
