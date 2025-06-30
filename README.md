# Photo Triage Agent System

A photo analysis system using LangGraph workflows and MCP (Model Context Protocol) for field technician photo documentation and quality assessment, featuring a modern Angular frontend demo.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Angular Demo   │    │   Agent Server   │◄──►│   MCP Server    │
│   (Frontend)    │◄──►│   (LangGraph)    │    │  (Pure Tools)   │
│                 │    │                  │    │                 │
│ • Photo Upload  │    │ • OpenAI Client  │    │ • Image Utils   │
│ • Progress UI   │    │ • LangGraph      │    │ • Quality Calc  │
│ • Real-time     │    │ • Orchestration  │    │ • File I/O      │
│ • Visualization │    │ • Reflection     │    │ • Templates     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### One-Command Startup (Recommended)
```bash
# Clone and navigate to the project
git clone <repository-url>
cd a-test-agent

# Start all services with one command
./start-servers.sh
```

This will automatically:
- ✅ Check and free required ports (8001, 8002, 4200)
- ✅ Set up Python virtual environments with `uv`
- ✅ Install all dependencies (Python + Node.js)
- ✅ Start MCP Server, Agent Server, and Angular Frontend
- ✅ Provide health checks and real-time logging

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm**
- **uv** (Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **API Keys** (at least one):
  - OpenAI API key (for vision model classification)
  - Anthropic API key (optional)
  - LangChain API key (optional, for tracing)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required for LLM functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Server Configuration (defaults shown)
AGENT_SERVER_PORT=8001
MCP_SERVER_PORT=8002
```

### Service URLs
- **Angular Frontend**: http://localhost:4200 (Main UI)
- **Agent Server API**: http://localhost:8001
- **MCP Server**: http://localhost:8002
- **API Documentation**: http://localhost:8001/docs

## 🌐 Using the Frontend Demo

1. **Start the system**: Run `./start-servers.sh`
2. **Open the demo**: Navigate to http://localhost:4200
3. **Upload photos**: Drag and drop or click to select up to 10 images
4. **Start analysis**: Click "Start Triage Workflow"
5. **Watch progress**: Real-time workflow visualization with step-by-step updates
6. **View results**: See quality analysis, classification, and feedback

### Frontend Features
- ✨ Drag & drop photo upload
- 📊 Real-time workflow progress visualization
- 🔄 Server-Sent Events (SSE) streaming
- 📱 Responsive design
- ⚡ Built with Angular 18 (standalone components)

## 📡 API Endpoints

### Health & Monitoring
- `GET /api/v1/health` - Application health check
- `GET /health` - Simple health probe

### Photo Analysis
- `POST /api/v1/triage/classify` - Classify single photo
- `POST /api/v1/triage/analyze-quality` - Analyze photo quality
- `POST /api/v1/triage/workflow` - Execute full triage workflow
- `POST /api/v1/triage/workflow-stream` - Real-time workflow with SSE

### Streaming Workflow Example
```bash
curl -X POST "http://localhost:8001/api/v1/triage/workflow-stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "images": [{"image_base64": "base64_data", "filename": "test.jpg"}],
    "job_context": "Equipment inspection",
    "enable_retry": true
  }'
```

## 🏗️ Project Structure

```
a-test-agent/
├── demo/                        # Angular frontend demo
│   ├── src/app/
│   │   ├── components/         # UI components
│   │   │   ├── image-upload/   # Photo upload component
│   │   │   └── workflow-visualizer/ # Progress visualization
│   │   └── services/           # API services
│   │       ├── agent.service.ts    # Workflow management
│   │       └── api.service.ts      # HTTP & SSE client
│   ├── package.json            # Node.js dependencies
│   └── angular.json            # Angular configuration
├── agent-server/               # LangGraph orchestration server
│   ├── models/                # State management
│   ├── llm/                  # LLM services
│   ├── nodes/                # Workflow nodes
│   ├── workflow/             # Workflow construction
│   ├── services/             # Core services
│   └── api/                  # REST API & SSE endpoints
├── mcp-server/                # MCP tools server
│   ├── tools/                # Pure computational tools
│   ├── resources/            # Template resources
│   └── utils/                # Utility functions
├── logs/                     # Service logs
│   ├── mcp-server.log       # MCP server logs
│   ├── agent-server.log     # Agent server logs
│   └── frontend.log         # Angular dev server logs
└── start-servers.sh          # Unified startup script
```

## 🔍 Workflow Overview

The system processes photos through a 5-step workflow:

1. **Initialize Processing**: Setup and validation
2. **Quality Analysis**: Computer vision analysis of technical quality
3. **Photo Classification**: OpenAI vision model categorizes photos
4. **ReAct Reflection**: Analyzes results quality and determines if retry needed
5. **Generate Feedback**: Creates actionable feedback for technicians

Each step provides real-time updates through the Angular frontend via Server-Sent Events.

## 🛠️ Development

### Manual Development Setup
```bash
# Terminal 1 - MCP Server
cd mcp-server
uv sync
uv run python main.py

# Terminal 2 - Agent Server  
cd agent-server
uv sync
uv run python main.py

# Terminal 3 - Angular Frontend
cd demo
npm install
npm start
```

### Adding New Features

**Frontend Components:**
1. Create component in `demo/src/app/components/`
2. Add to Angular routing if needed
3. Update services for new API endpoints

**Backend Workflow Nodes:**
1. Create node in `agent-server/nodes/`
2. Add to workflow in `agent-server/workflow/builder.py`
3. Update state if needed in `agent-server/models/state.py`

**MCP Tools:**
1. Create tool in `mcp-server/tools/`
2. Register in MCP server main
3. Add client method in `agent-server/services/mcp_client.py`


## 📊 Monitoring

### Logs
- **MCP Server**: `logs/mcp-server.log`
- **Agent Server**: `logs/agent-server.log` 
- **Angular Frontend**: `logs/frontend.log`
- **Unified logging**: The startup script provides combined log streaming
