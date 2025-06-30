#!/usr/bin/env python3
"""
Agent Server Entry Point

Runs the FastAPI agent server with REST endpoints for frontend integration.
"""

import asyncio
import sys
import os
import uvicorn

# Add the current directory to Python path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.app import app
from config.settings import settings
from config.logging import setup_logging, get_logger


async def main() -> None:
    """Main entry point for the agent server"""
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("Starting Photo Triage Agent Server")
    logger.info(f"Server configuration: {settings.agent_server_host}:{settings.agent_server_port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"LangSmith tracing: {settings.langchain_tracing_v2}")
    
    # Setup LangSmith
    settings.setup_langsmith()
    
    try:
        config = uvicorn.Config(
            app=app,
            host=settings.agent_server_host,
            port=settings.agent_server_port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
            access_log=settings.debug,
            loop="asyncio",
            server_header=False,
            forwarded_allow_ips="*"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Agent server stopped by user")
    except Exception as e:
        logger.error(f"Agent server failed to start: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())