import time
import psutil
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter
from fastapi.responses import Response

from ..models.responses import HealthResponse
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["Health & Monitoring"])

# Track application start time
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the application and its dependencies"
)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    uptime = time.time() - _start_time
    
    # Check service dependencies
    services = {
        "photo_classifier": "healthy",
        "quality_analyzer": "healthy",
        "batch_processor": "healthy",
        "feedback_generator": "healthy",
        "triage_agent": "healthy"
    }
    
    # In a real implementation, you would check actual service health
    # For example, test AI model availability, database connections, etc.
    
    try:
        # Basic health checks
        if not settings.openai_api_key:
            services["photo_classifier"] = "degraded - no API key"
        
        # Check memory usage
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > 90:
            services["system"] = f"warning - high memory usage: {memory_usage}%"
        else:
            services["system"] = "healthy"
            
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        services["system"] = f"error - {str(e)}"
    
    return HealthResponse(
        status="healthy",
        version=settings.version,
        uptime_seconds=uptime,
        services=services
    )


@router.get(
    "/health/ready",
    summary="Readiness check",
    description="Check if the application is ready to serve requests"
)
async def readiness_check() -> Dict[str, str]:
    """Readiness check for Kubernetes"""
    # Check if critical dependencies are available
    ready = True
    checks = {}
    
    try:
        # Check if we can import critical modules
        from ...tools.photo_classifier import PhotoClassifierTool
        from ...tools.quality_analyzer import QualityAnalyzerTool
        from ...services.langgraph_agent import TriageAgent
        
        checks["tools"] = "ready"
        checks["agent"] = "ready"
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        checks["modules"] = f"not ready - {str(e)}"
        ready = False
    
    status_code = 200 if ready else 503
    return Response(
        content=f"Ready: {ready}",
        status_code=status_code,
        media_type="text/plain"
    )


@router.get(
    "/health/live",
    summary="Liveness check",
    description="Check if the application is alive"
)
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}






@router.get(
    "/info",
    summary="Application information",
    description="Get application information and configuration"
)
async def get_app_info() -> Dict[str, Any]:
    """Get application information"""
    return {
        "name": settings.title,
        "version": settings.version,
        "description": settings.description,
        "environment": settings.environment,
        "debug": settings.debug,
        "agent_server_port": settings.agent_server_port,
        "mcp_server_port": settings.mcp_server_port,
        "api_docs": {
            "swagger": settings.docs_url,
            "redoc": settings.redoc_url
        },
        "features": {
            "langsmith_tracing": settings.langchain_tracing_v2,
            "reflection_enabled": settings.reflection_enabled
        },
        "limits": {
            "max_image_size_mb": settings.max_image_size_mb,
            "max_retry_attempts": settings.max_retry_attempts,
            "supported_formats": settings.supported_formats_list
        }
    }