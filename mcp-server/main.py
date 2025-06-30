#!/usr/bin/env python3
"""
MCP Server Entry Point

Runs the MCP (Model Context Protocol) server with HTTP transport.
"""

import asyncio
import sys
from mcp.photo_server import PhotoTriageMCPServer
from core.config import settings
from core.logging import configure_logging, get_logger


async def main() -> None:
    """Main entry point for the MCP server"""
    configure_logging()
    logger = get_logger(__name__)
    
    logger.info("Starting Photo Triage MCP Server")
    logger.info(f"Server configuration: {settings.mcp_server_host}:{settings.mcp_server_port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    try:
        server = PhotoTriageMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())