import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.config import settings
from tools.photo_classifier import PhotoClassifierTool
from tools.quality_analyzer import QualityAnalyzerTool
from tools.batch_processor import BatchProcessorTool
from tools.feedback_generator import FeedbackGeneratorTool

logger = logging.getLogger(__name__)


class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]
    sessionId: Optional[str] = None


class PhotoTriageMCPServer:
    """MCP server with FastAPI for proper streamable-http support"""
    
    def __init__(self):
        self.photo_classifier = PhotoClassifierTool()
        self.quality_analyzer = QualityAnalyzerTool()
        self.batch_processor = BatchProcessorTool()
        self.feedback_generator = FeedbackGeneratorTool()
        
        self.tools = [
            {
                "name": "classify_photo",
                "description": "Classify a photo into predefined categories using AI vision models",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string"},
                        "job_context": {"type": "string"}
                    },
                    "required": ["image_path"]
                }
            },
            {
                "name": "analyze_quality", 
                "description": "Analyze photo quality metrics using computer vision",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string"}
                    },
                    "required": ["image_path"]
                }
            },
            {
                "name": "process_batch",
                "description": "Process multiple photos concurrently for classification and quality analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_paths": {"type": "array", "items": {"type": "string"}},
                        "job_context": {"type": "string"}
                    },
                    "required": ["image_paths"]
                }
            },
            {
                "name": "generate_feedback",
                "description": "Generate actionable feedback based on classification and quality results",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "classification_results": {"type": "array"},
                        "quality_results": {"type": "array"}
                    },
                    "required": ["classification_results", "quality_results"]
                }
            }
        ]
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Photo Triage MCP Server",
            description="MCP server with streamable-http transport for photo triage tools",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments"""
        try:
            if name == "classify_photo":
                return await self.photo_classifier.classify(
                    arguments["image_path"],
                    arguments.get("job_context")
                )
            elif name == "analyze_quality":
                return await self.quality_analyzer.analyze(arguments["image_path"])
            elif name == "process_batch":
                return await self.batch_processor.process(
                    arguments["image_paths"],
                    arguments.get("job_context")
                )
            elif name == "generate_feedback":
                return await self.feedback_generator.generate(
                    arguments["classification_results"],
                    arguments["quality_results"]
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Tool '{name}' execution failed: {e}")
            return {"error": str(e)}
    
    async def stream_tool_execution(self, name: str, arguments: Dict[str, Any]):
        """Stream tool execution for streamable-http transport"""
        try:
            # Send start event
            yield f"data: {json.dumps({'status': 'started', 'tool': name, 'arguments': arguments})}\n\n"
            
            # For batch processing, provide progress updates
            if name == "process_batch":
                image_paths = arguments.get("image_paths", [])
                total_images = len(image_paths)
                
                # Send progress event
                yield f"data: {json.dumps({'status': 'progress', 'message': f'Processing {total_images} images', 'total': total_images})}\n\n"
                
                # Execute tool
                result = await self.call_tool(name, arguments)
                
                # Send result event
                yield f"data: {json.dumps({'status': 'result', 'data': result})}\n\n"
            else:
                # Execute tool normally
                result = await self.call_tool(name, arguments)
                
                # Send result event
                yield f"data: {json.dumps({'status': 'result', 'data': result})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'status': 'completed', 'tool': name})}\n\n"
            
        except Exception as e:
            # Send error event
            error_data = {'status': 'error', 'error': str(e), 'tool': name}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    def _setup_routes(self):
        """Setup FastAPI routes for MCP endpoints"""
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {"status": "healthy", "server": "Photo Triage MCP Server", "transport": "streamable-http"}
        
        @self.app.post("/initialize")
        async def initialize(request: Dict[str, Any]):
            """MCP initialization endpoint"""
            return {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {},
                    "streaming": True,  # Indicates streamable-http support
                    "experimental": {
                        "streamable-http": True
                    }
                },
                "serverInfo": {
                    "name": "photo-triage-mcp-server",
                    "version": "1.0.0",
                    "transport": "streamable-http"
                },
                "sessionId": "mcp-session-001"
            }
        
        @self.app.get("/tools")
        async def list_tools():
            """List available MCP tools"""
            return {"tools": self.tools}
        
        @self.app.post("/tools/call")
        async def call_tool_endpoint(request: ToolRequest):
            """Standard MCP tool call endpoint"""
            result = await self.call_tool(request.name, request.arguments)
            return result
        
        @self.app.post("/tools/call/stream")
        async def call_tool_stream_endpoint(request: ToolRequest):
            """Streamable-http MCP tool call endpoint"""
            return StreamingResponse(
                self.stream_tool_execution(request.name, request.arguments),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "X-MCP-Transport": "streamable-http"
                }
            )
        
        @self.app.get("/")
        async def root():
            """Root endpoint with MCP server information"""
            return {
                "server": "Photo Triage MCP Server",
                "version": "1.0.0",
                "transport": "streamable-http",
                "protocol": "MCP 2025-06-18",
                "endpoints": {
                    "health": "/health",
                    "initialize": "/initialize", 
                    "tools": "/tools",
                    "tool_call": "/tools/call",
                    "tool_stream": "/tools/call/stream",
                    "docs": "/docs"
                }
            }
    
    async def run(self) -> None:
        """Start the MCP server with FastAPI and streamable-http support"""
        logger.info(f"Starting MCP server with FastAPI streamable-http on {settings.mcp_server_host}:{settings.mcp_server_port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=settings.mcp_server_host,
            port=settings.mcp_server_port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()