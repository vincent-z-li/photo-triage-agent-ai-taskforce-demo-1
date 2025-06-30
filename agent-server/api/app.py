from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from .routers import triage, health
from .middleware.cors import add_cors_middleware
from .exceptions.handlers import register_exception_handlers
from config.settings import settings
from config.logging import setup_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger = get_logger(__name__)
    logger.info("Starting Photo Triage Agent API server")
    
    # Setup LangSmith tracing
    settings.setup_langsmith()
    logger.info("LangSmith tracing configured", 
                enabled=settings.langchain_tracing_v2,
                project=settings.langchain_project)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Photo Triage Agent API server")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    # Configure logging first
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        lifespan=lifespan,
        debug=settings.debug
    )
    
    # Add security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.debug else [
            settings.agent_server_host,
            "localhost",
            "127.0.0.1"
        ]
    )
    
    # Add CORS middleware
    add_cors_middleware(app)
    
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include routers
    app.include_router(
        triage.router,
        prefix=settings.api_v1_prefix,
        tags=["Photo Triage"]
    )
    
    app.include_router(
        health.router,
        prefix=settings.api_v1_prefix,
        tags=["Health & Monitoring"]
    )
    
    # Add root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information"""
        return {
            "name": settings.title,
            "version": settings.version,
            "status": "running",
            "docs_url": settings.docs_url,
            "api_prefix": settings.api_v1_prefix,
            "features": {
                "langsmith_tracing": settings.langchain_tracing_v2,
                "reflection_enabled": settings.reflection_enabled
            }
        }
    
    return app


# Create the app instance
app = create_app()


def run_server():
    """Run the agent server"""
    uvicorn.run(
        "src.api.app:app",
        host=settings.agent_server_host,
        port=settings.agent_server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=settings.debug,
        loop="asyncio"
    )


if __name__ == "__main__":
    run_server()