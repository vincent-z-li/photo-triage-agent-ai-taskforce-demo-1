import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import tempfile
import os
import base64
import json
from datetime import datetime, timezone

from ..models.requests import (
    PhotoClassificationRequest,
    QualityAnalysisRequest,
    BatchProcessingRequest,
    TriageWorkflowRequest,
    FeedbackGenerationRequest
)
from ..models.responses import (
    PhotoClassificationResponse,
    QualityAnalysisResponse,
    BatchProcessingResponse,
    TriageWorkflowResponse,
    FeedbackResponse,
    StatusEnum
)
from services.mcp_client import MCPHttpClient
from services.langgraph_agent import TriageAgent
from config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/triage", tags=["Photo Triage"])


async def get_mcp_client() -> MCPHttpClient:
    """Dependency to get MCP HTTP client"""
    return MCPHttpClient()


async def get_triage_agent() -> TriageAgent:
    """Dependency to get triage agent"""
    return TriageAgent()


def save_temp_image(image_data: str, is_base64: bool = False) -> str:
    """Save image data to temporary file and return path"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
        if is_base64:
            # Decode base64 data
            try:
                image_bytes = base64.b64decode(image_data)
                temp_file.write(image_bytes)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {e}")
        else:
            # Assume URL - would need to download in real implementation
            raise HTTPException(status_code=400, detail="URL image processing not implemented in demo")
        
        return temp_file.name


@router.post(
    "/classify",
    response_model=PhotoClassificationResponse,
    summary="Classify a single photo",
    description="Classify a photo into predefined categories using AI vision models"
)
async def classify_photo(
    request: PhotoClassificationRequest,
    mcp_client: MCPHttpClient = Depends(get_mcp_client)
) -> PhotoClassificationResponse:
    """Classify a single photo into predefined categories"""
    request_id = str(uuid.uuid4())
    
    logger.info("Photo classification request received", request_id=request_id)
    
    try:
        # Prepare image path
        image_path = None
        if request.image_base64:
            image_path = save_temp_image(request.image_base64, is_base64=True)
        elif request.image_url:
            # In a real implementation, download the image from URL
            raise HTTPException(status_code=400, detail="URL image processing not implemented in demo")
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 must be provided")
        
        # Classify the image via MCP
        async with mcp_client as client:
            result = await client.classify_photo(image_path, request.job_context)
        
        
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        
        if "error" in result:
            return PhotoClassificationResponse(
                status=StatusEnum.ERROR,
                message=f"Classification failed: {result['error']}",
                request_id=request_id
            )
        
        return PhotoClassificationResponse(
            status=StatusEnum.SUCCESS,
            message="Photo classified successfully",
            request_id=request_id,
            data=result
        )
        
    except Exception as e:
        logger.error("Photo classification failed", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/analyze-quality",
    response_model=QualityAnalysisResponse,
    summary="Analyze photo quality",
    description="Analyze the technical quality of a photo using computer vision"
)
async def analyze_quality(
    request: QualityAnalysisRequest,
    mcp_client: MCPHttpClient = Depends(get_mcp_client)
) -> QualityAnalysisResponse:
    """Analyze the quality of a photo"""
    request_id = str(uuid.uuid4())
    
    logger.info("Quality analysis request received", request_id=request_id)
    
    try:
        # Prepare image path
        image_path = None
        if request.image_base64:
            image_path = save_temp_image(request.image_base64, is_base64=True)
        elif request.image_url:
            raise HTTPException(status_code=400, detail="URL image processing not implemented in demo")
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 must be provided")
        
        # Analyze quality via MCP
        async with mcp_client as client:
            result = await client.analyze_quality(image_path)
        
        
        # Clean up temp file
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        
        if "error" in result:
            return QualityAnalysisResponse(
                status=StatusEnum.ERROR,
                message=f"Quality analysis failed: {result['error']}",
                request_id=request_id
            )
        
        return QualityAnalysisResponse(
            status=StatusEnum.SUCCESS,
            message="Quality analysis completed",
            request_id=request_id,
            data=result
        )
        
    except Exception as e:
        logger.error("Quality analysis failed", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/process-batch",
    response_model=BatchProcessingResponse,
    summary="Process multiple photos",
    description="Process multiple photos concurrently for classification and quality analysis"
)
async def process_batch(
    request: BatchProcessingRequest,
    mcp_client: MCPHttpClient = Depends(get_mcp_client)
) -> BatchProcessingResponse:
    """Process multiple photos in batch"""
    request_id = str(uuid.uuid4())
    
    logger.info("Batch processing request received", 
                request_id=request_id, 
                image_count=len(request.images))
    
    try:
        # For demo purposes, create temporary test images
        # In real implementation, handle image URLs and base64 data
        image_paths = []
        for i, image_data in enumerate(request.images):
            if "image_base64" in image_data:
                path = save_temp_image(image_data["image_base64"], is_base64=True)
                image_paths.append(path)
            else:
                # Use existing test images for demo
                test_paths = ["test_images/1000000772.png", "test_images/1000000773.png", "test_images/1000000774.png", "test_images/1000000775.png"]
                if i < len(test_paths) and os.path.exists(test_paths[i]):
                    image_paths.append(test_paths[i])
        
        if not image_paths:
            raise HTTPException(status_code=400, detail="No valid images provided")
        
        # Process batch via MCP
        async with mcp_client as client:
            result = await client.process_batch(image_paths, request.job_context)
        
        
        # Clean up temp files
        for path in image_paths:
            if path.startswith("/tmp") and os.path.exists(path):
                os.unlink(path)
        
        if "error" in result:
            return BatchProcessingResponse(
                status=StatusEnum.ERROR,
                message=f"Batch processing failed: {result['error']}",
                request_id=request_id
            )
        
        return BatchProcessingResponse(
            status=StatusEnum.SUCCESS,
            message="Batch processing completed",
            request_id=request_id,
            data=result
        )
        
    except Exception as e:
        logger.error("Batch processing failed", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/workflow",
    response_model=TriageWorkflowResponse,
    summary="Execute full triage workflow",
    description="Execute the complete ReAct triage workflow with reflection and retry"
)
async def execute_triage_workflow(
    request: TriageWorkflowRequest,
    background_tasks: BackgroundTasks,
    agent: TriageAgent = Depends(get_triage_agent)
) -> TriageWorkflowResponse:
    """Execute the full triage workflow with ReAct agent"""
    request_id = str(uuid.uuid4())
    workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
    
    logger.info("Triage workflow request received",
                request_id=request_id,
                workflow_id=workflow_id,
                image_count=len(request.images))
    
    try:
        # Prepare image paths (similar to batch processing)
        image_paths = []
        for i, image_data in enumerate(request.images):
            if "image_base64" in image_data:
                path = save_temp_image(image_data["image_base64"], is_base64=True)
                image_paths.append(path)
            else:
                # Use existing test images for demo
                test_paths = ["test_images/1000000772.png", "test_images/1000000773.png", "test_images/1000000774.png", "test_images/1000000775.png"]
                if i < len(test_paths) and os.path.exists(test_paths[i]):
                    image_paths.append(test_paths[i])
        
        if not image_paths:
            raise HTTPException(status_code=400, detail="No valid images provided")
        
        # Execute workflow
        result = await agent.run_triage_workflow(
            image_paths, 
            request.job_context, 
            request.enable_retry
        )
        
        
        # Schedule cleanup of temp files
        background_tasks.add_task(cleanup_temp_files, 
                                 [p for p in image_paths if p.startswith("/tmp")])
        
        # Prepare response data
        response_data = {
            "workflow_id": workflow_id,
            **result
        }
        
        return TriageWorkflowResponse(
            status=StatusEnum.SUCCESS if result.get("success") else StatusEnum.ERROR,
            message="Triage workflow completed successfully" if result.get("success") 
                   else "Triage workflow completed with errors",
            request_id=request_id,
            data=response_data
        )
        
    except Exception as e:
        logger.error("Triage workflow failed", 
                    request_id=request_id, 
                    workflow_id=workflow_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Generate feedback",
    description="Generate actionable feedback based on classification and quality results"
)
async def generate_feedback(
    request: FeedbackGenerationRequest,
    mcp_client: MCPHttpClient = Depends(get_mcp_client)
) -> FeedbackResponse:
    """Generate feedback based on analysis results"""
    request_id = str(uuid.uuid4())
    
    logger.info("Feedback generation request received", request_id=request_id)
    
    try:
        async with mcp_client as client:
            result = await client.generate_feedback(
                request.classification_results,
                request.quality_results
            )
        
        
        if "error" in result:
            return FeedbackResponse(
                status=StatusEnum.ERROR,
                message=f"Feedback generation failed: {result['error']}",
                request_id=request_id
            )
        
        return FeedbackResponse(
            status=StatusEnum.SUCCESS,
            message="Feedback generated successfully",
            request_id=request_id,
            data=result
        )
        
    except Exception as e:
        logger.error("Feedback generation failed", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/process-batch-stream",
    summary="Process multiple photos with streaming",
    description="Process multiple photos concurrently with real-time streaming progress updates"
)
async def process_batch_stream(
    request: BatchProcessingRequest,
    mcp_client: MCPHttpClient = Depends(get_mcp_client)
) -> StreamingResponse:
    """Process multiple photos in batch with streaming updates"""
    request_id = str(uuid.uuid4())
    
    logger.info("Streaming batch processing request received", 
                request_id=request_id, 
                image_count=len(request.images))
    
    async def generate_stream():
        try:
            # Prepare image paths (similar to batch processing)
            image_paths = []
            for i, image_data in enumerate(request.images):
                if "image_base64" in image_data:
                    path = save_temp_image(image_data["image_base64"], is_base64=True)
                    image_paths.append(path)
                else:
                    # Use existing test images for demo
                    test_paths = ["test_images/1000000772.png", "test_images/1000000773.png", "test_images/1000000774.png", "test_images/1000000775.png"]
                    if i < len(test_paths) and os.path.exists(test_paths[i]):
                        image_paths.append(test_paths[i])
            
            if not image_paths:
                error_data = {"error": "No valid images provided", "request_id": request_id}
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # Send initial status
            start_data = {
                "status": "started",
                "request_id": request_id,
                "total_images": len(image_paths),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            yield f"data: {json.dumps(start_data)}\n\n"
            
            # Stream processing results
            async with mcp_client as client:
                async for chunk in client.process_batch_stream(image_paths, request.job_context):
                    chunk["request_id"] = request_id
                    chunk["timestamp"] = datetime.now(timezone.utc).isoformat()
                    yield f"data: {json.dumps(chunk)}\n\n"
            
            # Clean up temp files
            for path in image_paths:
                if path.startswith("/tmp") and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except Exception as e:
                        logger.warning(f"Failed to cleanup temp file {path}: {e}")
            
            # Send completion status
            complete_data = {
                "status": "completed",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            yield f"data: {json.dumps(complete_data)}\n\n"
            
        except Exception as e:
            error_data = {
                "status": "error",
                "error": str(e),
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


async def cleanup_temp_files(file_paths: list) -> None:
    """Background task to cleanup temporary files"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {path}: {e}")