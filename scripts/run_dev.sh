#!/bin/bash
set -e

echo "Starting Photo Triage MCP Server in development mode..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default configuration."
    echo "Create .env from .env.example and add your API keys for full functionality."
fi

# Export development environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG
export TESTING=false

# Start the server
echo "Starting server..."
uv run python -m src.main