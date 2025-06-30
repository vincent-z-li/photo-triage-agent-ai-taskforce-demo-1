# Setup Guide

## Prerequisites

- Python 3.11+
- uv (Python package manager)
- Docker and Docker Compose (optional)
- OpenAI API key (for photo classification)
- Anthropic API key (optional, for enhanced feedback)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd photo-triage-mcp
```

### 2. Automated Setup

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Install uv if not present
- Create virtual environment
- Install dependencies
- Set up directory structure
- Create .env file template

### 3. Configure Environment

Edit `.env` file with your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required variables:
- `OPENAI_API_KEY`: For photo classification
- `ANTHROPIC_API_KEY`: For enhanced feedback (optional)

### 4. Run the Server

#### Option A: Direct Python
```bash
source .venv/bin/activate
./scripts/run_dev.sh
```

#### Option B: Docker
```bash
docker-compose up --build
```

## Development Setup

### Install Development Dependencies

```bash
uv pip install -e .[dev]
```

### Pre-commit Hooks

```bash
uv run pre-commit install
```

### Run Tests

```bash
./scripts/test.sh
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for vision models | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key for feedback | Optional |
| `MCP_SERVER_HOST` | Server host | localhost |
| `MCP_SERVER_PORT` | Server port | 8000 |
| `IMAGE_QUALITY_THRESHOLD` | Quality threshold (0-1) | 0.7 |
| `MAX_RETRY_ATTEMPTS` | Max retry attempts | 3 |
| `REFLECTION_ENABLED` | Enable reflection step | true |
| `LOG_LEVEL` | Logging level | INFO |

### Docker Configuration

The Docker setup includes:
- Multi-stage build for optimization
- Volume mounts for data persistence
- Health checks
- Automatic restart

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **API Key Issues**: Check .env file configuration
3. **Permission Errors**: Run `chmod +x scripts/*.sh`
4. **Docker Issues**: Ensure Docker daemon is running

### Logging

Logs are available in:
- Console output (structured JSON)
- Docker logs: `docker-compose logs -f`
- Application logs: `logs/` directory

## Testing

The project includes comprehensive tests:

```bash
# Run all tests
./scripts/test.sh

# Run specific test categories
uv run pytest tests/test_tools/ -v
uv run pytest tests/test_resources/ -v
uv run pytest tests/test_integration/ -v
```

## Performance Considerations

- **Batch Processing**: Process multiple images concurrently
- **Image Resizing**: Large images are automatically resized
- **Caching**: LangGraph checkpoints are persisted
- **Memory Management**: OpenCV operations are optimized

## Next Steps

1. **Integration**: Connect to your MCP client
2. **Customization**: Modify job templates and quality standards
3. **Extensions**: Add new classification categories
4. **Monitoring**: Set up application monitoring
5. **Scaling**: Deploy with load balancing if needed