.PHONY: dev mcp test lint format install

# Run v-shell voice CLI in development mode
dev:
	poetry run python -m app.main || python -m app.main

# Run MCP server
mcp:
	poetry run python -m app.mcp.server || python -m app.mcp.server

# Run the full test suite
test:
	poetry run pytest || python -m pytest

# Lint (if ruff or flake8 is available)
lint:
	poetry run ruff check app tests || python -m ruff check app tests || echo "ruff not installed"

# Format code (optional)
format:
	poetry run ruff format app tests || python -m ruff format app tests || echo "ruff not installed"

# Install dependencies (optional helper)
install:
	poetry install || pip install -r requirements.txt
