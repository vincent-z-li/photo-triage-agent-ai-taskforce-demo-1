from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class QualityGrade(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good" 
    FAIR = "fair"
    POOR = "poor"


class PhotoCategory(str, Enum):
    EQUIPMENT_PHOTO = "equipment_photo"
    BEFORE_WORK = "before_work"
    DURING_WORK = "during_work"
    AFTER_WORK = "after_work"
    DAMAGE_ASSESSMENT = "damage_assessment"
    SAFETY_DOCUMENTATION = "safety_documentation"
    MATERIAL_INVENTORY = "material_inventory"
    ENVIRONMENTAL_CONDITIONS = "environmental_conditions"
    OTHER = "other"


class BaseResponse(BaseModel):
    status: StatusEnum
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    uptime_seconds: float
    services: Dict[str, str]


class PhotoClassificationResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Photo classified successfully",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "category": "equipment_photo",
                    "confidence": 0.85,
                    "description": "HVAC unit close-up showing filters",
                    "relevance": "high",
                    "quality_flags": []
                }
            }
        }


class QualityAnalysisResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Quality analysis completed",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "quality_score": 0.75,
                    "quality_grade": "good",
                    "passes_threshold": True,
                    "analysis": {
                        "sharpness": "good",
                        "brightness": "good",
                        "contrast": "fair",
                        "resolution": "high"
                    },
                    "recommendations": []
                }
            }
        }


class BatchProcessingResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Batch processing completed",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "total_images": 3,
                    "processed_images": 3,
                    "summary": {
                        "quality_pass_rate": 0.67,
                        "average_combined_score": 0.71,
                        "categories": {
                            "equipment_photo": 1,
                            "before_work": 1,
                            "after_work": 1
                        },
                        "recommendations": [
                            "1 image failed quality checks and should be retaken"
                        ]
                    }
                }
            }
        }


class TriageWorkflowResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Triage workflow completed successfully",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "workflow_id": "wf_123456",
                    "success": True,
                    "attempts_made": 2,
                    "quality_issues": [
                        "Image 1: poor quality - retaken successfully"
                    ],
                    "reflection_notes": [
                        "Initial quality pass rate below threshold",
                        "Retry mechanism improved overall quality"
                    ],
                    "final_feedback": "Photo documentation quality improved after retry...",
                    "analysis_results": {
                        "total_images": 3,
                        "quality_pass_rate": 1.0
                    }
                }
            }
        }


class FeedbackResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Feedback generated successfully",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "feedback": "Overall photo quality is good. All images meet documentation standards...",
                    "total_images_analyzed": 3,
                    "actionable_items": [
                        "Consider taking closer shots of equipment details",
                        "Ensure consistent lighting across all photos"
                    ],
                    "priority_level": "low"
                }
            }
        }


class ErrorResponse(BaseResponse):
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Image processing failed",
                "timestamp": "2024-01-01T00:00:00Z",
                "error_code": "IMAGE_PROCESSING_ERROR",
                "error_details": {
                    "image_path": "/path/to/image.jpg",
                    "reason": "Unsupported image format"
                }
            }
        }


