#!/bin/bash
set -e

echo "Running tests for Photo Triage MCP Server..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set test environment
export TESTING=true
export LOG_LEVEL=WARNING

# Run linting
echo "Running code quality checks..."
uv run black --check src/ tests/
uv run ruff check src/ tests/
uv run mypy src/

# Run tests
echo "Running unit tests..."
uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term

echo "All tests completed!"
echo "Coverage report available at htmlcov/index.html"