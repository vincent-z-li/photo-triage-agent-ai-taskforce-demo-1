#!/bin/bash

# Run MCP and Agent servers
set -e

echo "Starting MCP and Agent servers..."

# Start MCP server in background
echo "Starting MCP server..."
cd mcp-server
python main.py &
MCP_PID=$!

# Wait for MCP server to start
sleep 5

# Start Agent server
echo "Starting Agent server..."
cd ../agent-server
python main.py &
AGENT_PID=$!

echo "Both servers started!"
echo "MCP Server PID: $MCP_PID"
echo "Agent Server PID: $AGENT_PID"
echo "Agent Server: http://localhost:8001"
echo "MCP Server: http://localhost:8002"

# Wait for both processes
wait $MCP_PID $AGENT_PID