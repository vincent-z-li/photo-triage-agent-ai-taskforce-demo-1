from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uuid
from datetime import datetime
from typing import Any, Dict
from config.logging import get_logger
from utils.exceptions import (
    PhotoTriageError,
    ImageProcessingError,
    QualityAnalysisError,
    ValidationError,
    ModelError,
    MCPServerError
)

logger = get_logger(__name__)


async def photo_triage_error_handler(request: Request, exc: PhotoTriageError) -> JSONResponse:
    """Handle custom PhotoTriageError exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        "PhotoTriageError occurred",
        error_type=type(exc).__name__,
        error_message=str(exc),
        request_id=request_id,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal processing error",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": type(exc).__name__.upper(),
            "error_details": {"message": str(exc)}
        }
    )


async def image_processing_error_handler(request: Request, exc: ImageProcessingError) -> JSONResponse:
    """Handle image processing errors"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        "Image processing error",
        error_message=str(exc),
        request_id=request_id,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Image processing failed",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": "IMAGE_PROCESSING_ERROR",
            "error_details": {"message": str(exc)}
        }
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors"""
    request_id = str(uuid.uuid4())
    
    logger.warning(
        "Validation error",
        error_message=str(exc),
        request_id=request_id,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "Validation failed",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": "VALIDATION_ERROR",
            "error_details": {"message": str(exc)}
        }
    )


async def model_error_handler(request: Request, exc: ModelError) -> JSONResponse:
    """Handle AI model errors"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        "Model error",
        error_message=str(exc),
        request_id=request_id,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "message": "AI model service unavailable",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": "MODEL_ERROR",
            "error_details": {"message": str(exc)}
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        request_id=request_id,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": f"HTTP_{exc.status_code}"
        }
    )


async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    request_id = str(uuid.uuid4())
    
    logger.warning(
        "Request validation error",
        errors=exc.errors(),
        request_id=request_id,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Request validation failed",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": "REQUEST_VALIDATION_ERROR",
            "error_details": {"validation_errors": exc.errors()}
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        "Unexpected error",
        error_type=type(exc).__name__,
        error_message=str(exc),
        request_id=request_id,
        path=request.url.path,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI app"""
    app.add_exception_handler(PhotoTriageError, photo_triage_error_handler)
    app.add_exception_handler(ImageProcessingError, image_processing_error_handler)
    app.add_exception_handler(QualityAnalysisError, image_processing_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(ModelError, model_error_handler)
    app.add_exception_handler(MCPServerError, photo_triage_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)