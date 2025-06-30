from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class JobType(str, Enum):
    ELECTRICAL_INSPECTION = "electrical_inspection"
    PLUMBING_REPAIR = "plumbing_repair"
    HVAC_MAINTENANCE = "hvac_maintenance"
    GENERAL_MAINTENANCE = "general_maintenance"


class PhotoClassificationRequest(BaseModel):
    image_url: Optional[HttpUrl] = Field(None, description="URL to the image file")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")
    job_context: Optional[str] = Field(None, description="Context about the job/task")
    job_type: Optional[JobType] = Field(None, description="Type of job being performed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg",
                "job_context": "Electrical panel inspection",
                "job_type": "electrical_inspection"
            }
        }


class QualityAnalysisRequest(BaseModel):
    image_url: Optional[HttpUrl] = Field(None, description="URL to the image file")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://example.com/image.jpg"
            }
        }


class BatchProcessingRequest(BaseModel):
    images: List[Dict[str, str]] = Field(..., description="List of images with URLs or base64 data")
    job_context: Optional[str] = Field(None, description="Context about the job/task")
    job_type: Optional[JobType] = Field(None, description="Type of job being performed")
    enable_retry: bool = Field(True, description="Enable retry mechanism for failed images")
    
    class Config:
        json_schema_extra = {
            "example": {
                "images": [
                    {"image_url": "https://example.com/image1.jpg"},
                    {"image_url": "https://example.com/image2.jpg"}
                ],
                "job_context": "Electrical panel inspection",
                "job_type": "electrical_inspection",
                "enable_retry": True
            }
        }


class TriageWorkflowRequest(BaseModel):
    images: List[Dict[str, str]] = Field(..., description="List of images with URLs or base64 data")
    job_context: Optional[str] = Field(None, description="Context about the job/task")
    job_type: Optional[JobType] = Field(None, description="Type of job being performed")
    enable_retry: bool = Field(True, description="Enable retry mechanism")
    max_attempts: Optional[int] = Field(None, description="Maximum retry attempts (overrides config)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "images": [
                    {"image_url": "https://example.com/before.jpg"},
                    {"image_url": "https://example.com/during.jpg"},
                    {"image_url": "https://example.com/after.jpg"}
                ],
                "job_context": "HVAC maintenance and filter replacement",
                "job_type": "hvac_maintenance",
                "enable_retry": True,
                "max_attempts": 3
            }
        }


class FeedbackGenerationRequest(BaseModel):
    classification_results: List[Dict[str, Any]] = Field(..., description="Photo classification results")
    quality_results: List[Dict[str, Any]] = Field(..., description="Quality analysis results")
    job_context: Optional[str] = Field(None, description="Context about the job/task")
    
    class Config:
        json_schema_extra = {
            "example": {
                "classification_results": [
                    {
                        "category": "equipment_photo",
                        "confidence": 0.85,
                        "description": "HVAC unit close-up"
                    }
                ],
                "quality_results": [
                    {
                        "quality_score": 0.75,
                        "quality_grade": "good",
                        "passes_threshold": True
                    }
                ],
                "job_context": "HVAC maintenance"
            }
        }