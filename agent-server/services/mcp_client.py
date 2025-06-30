"""
MCP HTTP Client for connecting to MCP server via streamable HTTP
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
import httpx
from config.settings import settings

logger = logging.getLogger(__name__)


class MCPHttpClient:
    """Streamable HTTP client for MCP server communication following MCP specification"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or f"http://{settings.mcp_server_host}:{settings.mcp_server_port}"
        self.client = httpx.AsyncClient(timeout=120.0)  # Longer timeout for streaming
        self.session_id = None
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP session with capability negotiation"""
        try:
            response = await self.client.post(
                f"{self.base_url}/initialize",
                json={
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "photo-triage-agent",
                        "version": "1.0.0"
                    }
                }
            )
            response.raise_for_status()
            
            init_response = response.json()
            self.session_id = init_response.get("sessionId")
            
            logger.info(f"MCP session initialized: {self.session_id}")
            return init_response
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP session: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from MCP server"""
        try:
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            
            return response.json().get("tools", [])
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            payload = {
                "name": name,
                "arguments": arguments
            }
            
            if self.session_id:
                payload["sessionId"] = self.session_id
            
            response = await self.client.post(
                f"{self.base_url}/tools/call",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Tool '{name}' called successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool '{name}': {e}")
            raise
    
    async def call_tool_stream(self, name: str, arguments: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Call a tool on the MCP server with streaming response using streamable-http"""
        try:
            payload = {
                "name": name,
                "arguments": arguments
            }
            
            if self.session_id:
                payload["sessionId"] = self.session_id
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/tools/call/stream",  # Use streamable-http endpoint
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            yield data
                        except json.JSONDecodeError:
                            continue
                    elif line.strip() == "":
                        continue  # Skip empty lines
                        
        except Exception as e:
            logger.error(f"Failed to stream tool '{name}': {e}")
            raise
    
    async def classify_photo(self, image_path: str, job_context: Optional[str] = None) -> Dict[str, Any]:
        """Classify a photo using MCP server"""
        return await self.call_tool("classify_photo", {
            "image_path": image_path,
            "job_context": job_context
        })
    
    async def analyze_quality(self, image_path: str) -> Dict[str, Any]:
        """Analyze photo quality using MCP server"""
        return await self.call_tool("analyze_quality", {
            "image_path": image_path
        })
    
    async def process_batch(self, image_paths: List[str], job_context: Optional[str] = None) -> Dict[str, Any]:
        """Process a batch of images using MCP server"""
        return await self.call_tool("process_batch", {
            "image_paths": image_paths,
            "job_context": job_context
        })
    
    async def process_batch_stream(self, image_paths: List[str], job_context: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a batch of images using MCP server with streaming"""
        async for chunk in self.call_tool_stream("process_batch", {
            "image_paths": image_paths,
            "job_context": job_context
        }):
            yield chunk
    
    async def generate_feedback(
        self, 
        classification_results: List[Dict[str, Any]], 
        quality_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate feedback using MCP server"""
        return await self.call_tool("generate_feedback", {
            "classification_results": classification_results,
            "quality_results": quality_results
        })
    
    async def triage_with_reflection(
        self, 
        image_paths: List[str], 
        job_context: Optional[str] = None,
        enable_retry: bool = True
    ) -> Dict[str, Any]:
        """Run triage workflow with reflection using MCP server"""
        return await self.call_tool("triage_with_reflection", {
            "image_paths": image_paths,
            "job_context": job_context,
            "enable_retry": enable_retry
        })
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()