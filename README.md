# Photo Triage System - Clean Architecture

An intelligent agent system for triaging and analyzing photos using computer vision and AI models with separated MCP and Agent servers.

## Architecture

```
├── mcp-server/           # MCP Server (HTTP transport)
│   ├── main.py          # MCP server entry point
│   ├── mcp/             # MCP server implementation
│   ├── tools/           # Photo processing tools
│   ├── resources/       # MCP resources
│   └── core/            # Configuration and logging
│
├── agent-server/        # Agent Server (FastAPI)
│   ├── main.py          # Agent server entry point  
│   ├── api/             # REST API endpoints
│   ├── services/        # LangGraph agent & MCP client
│   └── config/          # Configuration and logging
│
└── scripts/
    └── run_servers.sh   # Start both servers
```

## Features

- **Photo Classification**: Automatically categorize photos into predefined categories
- **Quality Analysis**: Analyze technical photo quality (blur, exposure, composition)
- **Batch Processing**: Process multiple photos concurrently for efficiency
- **Intelligent Feedback**: Generate actionable feedback based on analysis results
- **ReAct Agent Workflow**: Advanced workflow with reflection and retry mechanisms
- **REST API**: FastAPI-based REST endpoints for easy integration
- **Proper MCP Server**: Lightweight MCP server with streamable-http transport (no FastAPI dependency)

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Anthropic API key (optional)
- LangChain API key (optional, for tracing)

### Installation

1. Clone and setup:
```bash
git clone <repository>
cd a-test-agent
./scripts/setup.sh
```

2. Configure environment:
```bash
cp .env.dist .env
# Edit .env with your API keys
```

3. Start both servers:
```bash
./scripts/run_servers.sh
```

### Alternative: Docker
```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start with Docker
docker-compose up
```

## Usage

### REST API Endpoints

The agent server provides REST endpoints at `http://localhost:8001`:

- `POST /api/v1/triage/classify` - Classify a single photo
- `POST /api/v1/triage/analyze-quality` - Analyze photo quality  
- `POST /api/v1/triage/process-batch` - Process multiple photos
- `POST /api/v1/triage/process-batch-stream` - Process multiple photos with real-time streaming 🔥
- `POST /api/v1/triage/workflow` - Execute full ReAct triage workflow
- `POST /api/v1/triage/feedback` - Generate feedback from results

### Streaming Support

The system now supports **real-time streaming** for long-running operations:

- **Server-Sent Events (SSE)**: Frontend can receive real-time progress updates
- **Streamable HTTP**: MCP server uses `streamable-http` transport
- **Progress Tracking**: Live updates on batch processing status
- **Error Streaming**: Real-time error reporting during processing

### API Documentation

Visit `http://localhost:8001/docs` for interactive API documentation.

### Quick Demo

```bash
./quick_demo.sh
```

## MCP Communication

- Agent Server: http://localhost:8001
- MCP Server: http://localhost:8002  
- Protocol: Proper MCP with **streamable-http** transport (aiohttp-based)
- Features: MCP 2025-06-18, capability negotiation, session management, real-time streaming

## Benefits of Separated Architecture

1. **Scalability**: Servers can be scaled independently
2. **Deployment Flexibility**: Deploy on different hosts/containers  
3. **Protocol Compliance**: Proper MCP implementation with streamable-http
4. **Lightweight**: No unnecessary FastAPI dependency in MCP server
5. **Docker Ready**: Full containerization support
6. **Network Communication**: Can communicate across network boundaries

## Development

### Running Tests
```bash
./scripts/test.sh
```

### Development Mode
```bash
./scripts/run_dev.sh
```

## License

MIT License