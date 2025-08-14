# Snipster

A code snippet management application built with FastAPI backend and Reflex frontend.

## Development Setup

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) package manager

### Backend (FastAPI)

The FastAPI backend provides the REST API for managing code snippets.

1. **Navigate to the project root:**
   ```bash
   cd snipster
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Start the FastAPI development server:**
   ```bash
   uv run fastapi dev src/snipster/api.py
   ```

   The API will be available at `http://localhost:8000`

4. **Optional: Run tests:**
   ```bash
   uv run pytest
   ```

### Frontend (Reflex)

The Reflex frontend provides a modern web interface for managing snippets.

1. **Navigate to the frontend directory:**
   ```bash
   cd ui
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Start the Reflex development server:**
   ```bash
   uv run reflex run
   ```

   The frontend will be available at `http://localhost:3000`

4. **Optional: Build for production:**
   ```bash
   uv run reflex export
   ```

## Project Structure

### Backend (`src/snipster/`)
- **`api.py`**: FastAPI application with REST endpoints
- **`models.py`**: Pydantic models for request/response validation
- **`repo.py`**: Data access layer for snippets
- **`db.py`**: Database connection and session management
- **`cli.py`**: Command-line interface for snippet management

### Frontend (`ui/`)
- **`ui/ui.py`**: Main Reflex application with UI components
- **`rxconfig.py`**: Reflex configuration (ports, app name)

### Database
- **`alembic/`**: Database schema migrations
- **`snipster.sqlite`**: SQLite database file

### Development Tools
- **`pyproject.toml`**: Project configuration and dependencies
- **`Makefile`**: Common development commands
- **`.pre-commit-config.yaml`**: Code quality hooks
- **`tests/`**: Comprehensive test suite
