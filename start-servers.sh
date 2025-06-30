#!/bin/bash
set -e

echo "🚀 Starting Photo Triage Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}Warning: Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to kill processes using a specific port
kill_port_processes() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}🔫 Killing processes using port $port: $pids${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
        
        # Verify the port is now free
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${RED}❌ Failed to free port $port${NC}"
            return 1
        else
            echo -e "${GREEN}✅ Port $port is now free${NC}"
        fi
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $name failed to start within timeout${NC}"
    return 1
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    if [ ! -z "$MCP_PID" ]; then
        echo "Stopping MCP server (PID: $MCP_PID)"
        kill $MCP_PID 2>/dev/null || true
    fi
    if [ ! -z "$AGENT_PID" ]; then
        echo "Stopping Agent server (PID: $AGENT_PID)"
        kill $AGENT_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping Angular frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Deactivate any active virtual environment to avoid conflicts
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🔄 Deactivating current virtual environment..."
    deactivate 2>/dev/null || true
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is required but not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Check if required directories exist
if [ ! -d "mcp-server" ]; then
    echo -e "${RED}❌ mcp-server directory not found${NC}"
    exit 1
fi

if [ ! -d "agent-server" ]; then
    echo -e "${RED}❌ agent-server directory not found${NC}"
    exit 1
fi

if [ ! -d "demo-front-end" ]; then
    echo -e "${RED}❌ demo-front-end directory not found${NC}"
    exit 1
fi

# Check ports
echo "🔍 Checking ports..."

# Check and free port 8002 (MCP server)
if ! check_port 8002; then
    echo "🔫 Freeing port 8002..."
    kill_port_processes 8002
fi

# Check and free port 8001 (Agent server)
if ! check_port 8001; then
    echo "🔫 Freeing port 8001..."
    kill_port_processes 8001
fi

# Check and free port 4200 (Angular frontend)
if ! check_port 4200; then
    echo "🔫 Freeing port 4200..."
    kill_port_processes 4200
fi

echo -e "${GREEN}✅ Ports are ready${NC}"

# Create logs directory
mkdir -p logs

echo "📦 Setting up virtual environments and installing dependencies..."

# Setup MCP server environment
echo "Setting up MCP server environment..."
cd mcp-server
uv sync
cd ..

# Setup Agent server environment  
echo "Setting up Agent server environment..."
cd agent-server
uv sync
cd ..

# Setup Angular frontend dependencies
echo "Setting up Angular frontend dependencies..."
cd demo-front-end
npm install
cd ..

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Start MCP server
echo "🔧 Starting MCP server on port 8002..."
cd mcp-server
uv run python main.py > ../logs/mcp-server.log 2>&1 &
MCP_PID=$!
cd ..

echo "MCP server started with PID: $MCP_PID"

# Wait for MCP server to be ready
if ! wait_for_service "http://localhost:8002/health" "MCP server"; then
    echo -e "${RED}❌ Failed to start MCP server${NC}"
    exit 1
fi

# Start Agent server
echo "🤖 Starting Agent server on port 8001..."
cd agent-server
uv run python main.py > ../logs/agent-server.log 2>&1 &
AGENT_PID=$!
cd ..

echo "Agent server started with PID: $AGENT_PID"

# Wait for Agent server to be ready
if ! wait_for_service "http://localhost:8001/api/v1/health" "Agent server"; then
    echo -e "${RED}❌ Failed to start Agent server${NC}"
    exit 1
fi

# Start Angular frontend
echo "🌐 Starting Angular frontend on port 4200..."
cd demo-front-end
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Angular frontend started with PID: $FRONTEND_PID"

# Wait for Angular frontend to be ready
if ! wait_for_service "http://localhost:4200" "Angular frontend"; then
    echo -e "${RED}❌ Failed to start Angular frontend${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 All servers are running successfully!${NC}"
echo ""
echo "📋 Service Information:"
echo "  📡 MCP Server:     http://localhost:8002"
echo "  🤖 Agent Server:   http://localhost:8001"
echo "  🌐 Frontend Demo:  http://localhost:4200"
echo "  📖 API Docs:       http://localhost:8001/docs"
echo "  📊 Health Check:   http://localhost:8001/api/v1/health"
echo ""
echo "📝 Logs:"
echo "  MCP Server:     logs/mcp-server.log"
echo "  Agent Server:   logs/agent-server.log"
echo "  Frontend:       logs/frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Keep the script running and show logs
echo "📜 Streaming logs (Ctrl+C to stop)..."
echo "----------------------------------------"

# Stream logs from all servers
tail -f logs/mcp-server.log logs/agent-server.log logs/frontend.log