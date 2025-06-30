#!/bin/bash
set -e

echo "Setting up Photo Triage MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment and installing dependencies..."
uv venv
source .venv/bin/activate
uv pip install -e .

# Install development dependencies
echo "Installing development dependencies..."
uv pip install -e .[dev]

# Create directories
echo "Creating required directories..."
mkdir -p logs data/uploads data/cache data/temp

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your API keys and configuration"
fi

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
uv run pre-commit install

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'source .venv/bin/activate' to activate the virtual environment"
echo "3. Run 'uv run python -m src.main' to start the server"
echo "4. Or use Docker: 'docker-compose up --build'"