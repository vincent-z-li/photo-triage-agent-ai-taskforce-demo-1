# Photo Triage Agent System

A sophisticated photo analysis system using LangGraph workflows and MCP (Model Context Protocol) for field technician photo documentation and quality assessment.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Agent Server  │◄──►│   MCP Server     │
│   (LangGraph)   │    │   (Pure Tools)   │
│                 │    │                  │
│ • OpenAI Client │    │ • Image Utils    │
│ • LangGraph     │    │ • Quality Calc   │
│ • Orchestration │    │ • File I/O       │
│ • Reflection    │    │ • Templates      │
└─────────────────┘    └──────────────────┘
```

## 🚀 Quick Start

### Method 1: Startup Script (Recommended)
```bash
# Clone and navigate to the project
git clone <repository-url>
cd a-test-agent

# Run the startup script
./start-servers.sh
```

### Method 2: Docker Compose (Production Ready)
```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Method 3: Manual Setup (Development)
```bash
# Terminal 1 - MCP Server
cd mcp-server
pip install -e .
python main.py

# Terminal 2 - Agent Server  
cd agent-server
pip install -e .
python main.py
```

## 📋 Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (for containerized deployment)
- **API Keys** (at least one):
  - OpenAI API key (for vision model classification)
  - Anthropic API key (optional)
  - LangChain API key (optional, for tracing)

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required for LLM functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server Configuration
AGENT_SERVER_PORT=8001
MCP_SERVER_PORT=8002
```

### Server Ports
- **Agent Server**: http://localhost:8001
- **MCP Server**: http://localhost:8002
- **API Documentation**: http://localhost:8001/docs

## 📡 API Endpoints

### Health & Monitoring
- `GET /health` - Application health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /info` - Application information

### Photo Analysis
- `POST /triage/classify` - Classify single photo
- `POST /triage/analyze-quality` - Analyze photo quality
- `POST /triage/process-batch` - Process multiple photos
- `POST /triage/workflow` - Execute full triage workflow
- `POST /triage/feedback` - Generate feedback

### Streaming
- `POST /triage/process-batch-stream` - Real-time batch processing

## 🧪 Testing the API

### Using curl:
```bash
# Health check
curl http://localhost:8001/health

# Classify a photo (base64 encoded)
curl -X POST "http://localhost:8001/triage/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQ...",
    "job_context": "Equipment inspection"
  }'

# Full workflow
curl -X POST "http://localhost:8001/triage/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "images": [{"image_path": "test_images/sample.jpg"}],
    "job_context": "Routine maintenance check",
    "enable_retry": true
  }'
```

### Using the interactive API docs:
Visit http://localhost:8001/docs for the Swagger UI interface.

## 🏗️ Project Structure

```
a-test-agent/
├── agent-server/              # LangGraph orchestration server
│   ├── models/               # State management
│   ├── llm/                 # LLM services
│   ├── nodes/               # Workflow nodes
│   ├── workflow/            # Workflow construction
│   ├── services/            # Core services
│   └── api/                 # REST API
├── mcp-server/               # MCP tools server
│   ├── tools/               # Pure computational tools
│   ├── resources/           # Template resources
│   └── utils/               # Utility functions
├── data/                    # Configuration templates
├── test_images/             # Sample images
├── docker-compose.yml       # Container orchestration
└── start-servers.sh         # Development startup script
```

## 🔍 Workflow Overview

1. **Photo Preprocessing**: MCP server handles image validation, resizing, metadata extraction
2. **Quality Analysis**: Computer vision analysis of technical quality
3. **LLM Classification**: OpenAI vision model categorizes photos
4. **Reflection**: Analyzes results quality and determines if retry needed
5. **Feedback Generation**: Creates actionable feedback for technicians

## 🛠️ Development

### Adding New Workflow Nodes
1. Create node in `agent-server/nodes/`
2. Add to workflow in `agent-server/workflow/builder.py`
3. Update state if needed in `agent-server/models/state.py`

### Adding New MCP Tools
1. Create tool in `mcp-server/tools/`
2. Register in MCP server main
3. Add client method in `agent-server/services/mcp_client.py`

## 🐳 Docker Deployment

### Build and Run
```bash
# Build images
docker-compose build

# Run in background
docker-compose up -d

# Scale services
docker-compose up -d --scale agent-server=2

# View logs
docker-compose logs -f agent-server
docker-compose logs -f mcp-server
```

### Production Deployment
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security

- **Non-root containers**: Both servers run as non-root users
- **API key management**: Use environment variables, never commit keys
- **Health checks**: Built-in health monitoring
- **Input validation**: Comprehensive request validation

## 📊 Monitoring

### Health Endpoints
- Application health status
- Service dependency checks
- Memory usage monitoring
- Uptime tracking

### Logging
- Structured JSON logging
- Per-service log files in `logs/` directory
- Docker logs available via `docker-compose logs`

## 🚨 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8001
lsof -i :8002

# Kill processes if needed
kill $(lsof -t -i:8001)
```

**MCP server not ready:**
- Check logs: `tail -f logs/mcp-server.log`
- Verify dependencies are installed
- Check port 8002 is available

**Agent server connection issues:**
- Ensure MCP server is running first
- Check network connectivity between containers
- Verify environment variables

**API key issues:**
- Verify OpenAI API key is valid
- Check .env file is properly loaded
- Test API key with simple OpenAI call

### Debugging
```bash
# View live logs
tail -f logs/*.log

# Docker debugging
docker-compose logs -f
docker exec -it photo-triage-agent bash
docker exec -it photo-triage-mcp bash

# Health checks
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Open an issue on GitHub