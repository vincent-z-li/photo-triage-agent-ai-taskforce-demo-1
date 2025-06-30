# Photo Triage Agent API Documentation

## Overview

The Photo Triage Agent API is a FastAPI-based REST service that provides photo classification, quality analysis, and intelligent triage workflows using ReAct agents with LangGraph.

## Architecture

The system consists of two main services:

1. **Agent Server** (Port 8001) - FastAPI REST API for frontend integration
2. **MCP Server** (Port 8002) - Model Context Protocol server for tool/resource exposure

## Features

- 🤖 **ReAct Agent Workflows** - Reasoning + Acting with reflection and retry
- 📸 **Photo Classification** - AI-powered categorization using OpenAI vision models
- 📊 **Quality Analysis** - Computer vision-based quality scoring
- 🔄 **Batch Processing** - Concurrent processing of multiple images
- 📝 **Feedback Generation** - Actionable recommendations for field technicians
- 📈 **LangSmith Tracing** - Complete workflow observability
- 🎯 **Health Monitoring** - Comprehensive health checks and metrics
- 📋 **OpenAPI Documentation** - Auto-generated API docs

## Base URLs

- **Development**: `http://localhost:8001`
- **Production**: Configure via environment variables

## Authentication

Currently, no authentication is required. In production, implement API keys or OAuth.

## API Endpoints

### Health & Monitoring

#### GET `/api/v1/health`
Health check endpoint with service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "services": {
    "photo_classifier": "healthy",
    "quality_analyzer": "healthy",
    "system": "healthy"
  }
}
```

#### GET `/api/v1/metrics`
Prometheus metrics endpoint for monitoring.

#### GET `/api/v1/info`
Application information and configuration.

### Photo Triage

#### POST `/api/v1/triage/classify`
Classify a single photo into predefined categories.

**Request Body:**
```json
{
  "image_base64": "base64_encoded_image_data",
  "job_context": "Electrical panel inspection",
  "job_type": "electrical_inspection"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Photo classified successfully",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456",
  "data": {
    "category": "equipment_photo",
    "confidence": 0.85,
    "description": "Electrical panel with visible circuits",
    "relevance": "high",
    "quality_flags": []
  }
}
```

#### POST `/api/v1/triage/analyze-quality`
Analyze the technical quality of a photo.

**Request Body:**
```json
{
  "image_base64": "base64_encoded_image_data"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Quality analysis completed",
  "data": {
    "quality_score": 0.75,
    "quality_grade": "good",
    "passes_threshold": true,
    "analysis": {
      "sharpness": "good",
      "brightness": "good",
      "contrast": "fair",
      "resolution": "high"
    },
    "recommendations": []
  }
}
```

#### POST `/api/v1/triage/process-batch`
Process multiple photos concurrently.

**Request Body:**
```json
{
  "images": [
    {"image_base64": "base64_data_1"},
    {"image_base64": "base64_data_2"}
  ],
  "job_context": "HVAC maintenance",
  "job_type": "hvac_maintenance",
  "enable_retry": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Batch processing completed",
  "data": {
    "total_images": 2,
    "processed_images": 2,
    "summary": {
      "quality_pass_rate": 0.5,
      "average_combined_score": 0.65,
      "categories": {
        "equipment_photo": 1,
        "before_work": 1
      },
      "recommendations": [
        "1 image failed quality checks and should be retaken"
      ]
    }
  }
}
```

#### POST `/api/v1/triage/workflow`
Execute the complete ReAct triage workflow with reflection and retry.

**Request Body:**
```json
{
  "images": [
    {"image_base64": "base64_data_1"},
    {"image_base64": "base64_data_2"},
    {"image_base64": "base64_data_3"}
  ],
  "job_context": "Electrical panel upgrade",
  "job_type": "electrical_inspection",
  "enable_retry": true,
  "max_attempts": 3
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Triage workflow completed successfully",
  "data": {
    "workflow_id": "wf_abc12345",
    "success": true,
    "attempts_made": 2,
    "quality_issues": [
      "Image 1: poor quality - retaken successfully"
    ],
    "reflection_notes": [
      "Initial quality pass rate below threshold",
      "Retry mechanism improved overall quality"
    ],
    "final_feedback": "Photo documentation quality improved...",
    "analysis_results": {
      "total_images": 3,
      "quality_pass_rate": 1.0
    }
  }
}
```

#### POST `/api/v1/triage/feedback`
Generate actionable feedback based on analysis results.

**Request Body:**
```json
{
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
      "passes_threshold": true
    }
  ],
  "job_context": "HVAC maintenance"
}
```

## Job Types

Supported job types for contextual analysis:

- `electrical_inspection` - Electrical system inspection
- `plumbing_repair` - Plumbing system repair
- `hvac_maintenance` - HVAC system maintenance
- `general_maintenance` - General facility maintenance

## Photo Categories

The system classifies photos into these categories:

- `equipment_photo` - Tools, machinery, or equipment
- `before_work` - Initial conditions before work
- `during_work` - Work in progress
- `after_work` - Completed work results
- `damage_assessment` - Damage or issues documentation
- `safety_documentation` - Safety protocols or hazards
- `material_inventory` - Materials, parts, or supplies
- `environmental_conditions` - Weather, site conditions
- `other` - Photos that don't fit other categories

## Quality Grades

Quality analysis returns these grades:

- `excellent` - Quality score ≥ 0.8
- `good` - Quality score ≥ 0.6
- `fair` - Quality score ≥ 0.4
- `poor` - Quality score < 0.4

## Error Handling

All endpoints return standardized error responses:

```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456",
  "error_code": "ERROR_TYPE",
  "error_details": {
    "additional": "context"
  }
}
```

Common error codes:

- `VALIDATION_ERROR` (400) - Invalid request data
- `IMAGE_PROCESSING_ERROR` (422) - Image processing failed
- `MODEL_ERROR` (503) - AI model service unavailable
- `INTERNAL_SERVER_ERROR` (500) - Unexpected server error

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing rate limiting for production use.

## LangSmith Tracing

When LangSmith is configured, all workflow executions are traced with:

- Individual step execution times
- Input/output parameters
- Error traces
- Retry attempts and reflections

Access traces at: [LangSmith Dashboard](https://smith.langchain.com)

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/api/v1/openapi.json`

## SDKs and Integration

### Python SDK Example

```python
import httpx
import base64

class PhotoTriageClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def classify_photo(self, image_path: str, job_context: str = None):
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/triage/classify",
            json={
                "image_base64": image_data,
                "job_context": job_context
            }
        )
        return response.json()

# Usage
client = PhotoTriageClient()
result = await client.classify_photo("equipment.jpg", "Electrical inspection")
```

### JavaScript/TypeScript SDK Example

```typescript
class PhotoTriageClient {
  constructor(private baseUrl: string = 'http://localhost:8001') {}

  async classifyPhoto(imageFile: File, jobContext?: string) {
    const base64 = await this.fileToBase64(imageFile);
    
    const response = await fetch(`${this.baseUrl}/api/v1/triage/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: base64,
        job_context: jobContext
      })
    });
    
    return response.json();
  }

  private fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}
```

## Production Considerations

1. **Authentication**: Implement API keys or OAuth
2. **Rate Limiting**: Add rate limiting middleware
3. **Monitoring**: Set up Prometheus + Grafana
4. **Caching**: Add Redis for caching frequent requests
5. **Load Balancing**: Use nginx or cloud load balancer
6. **Database**: Replace in-memory storage with PostgreSQL
7. **File Storage**: Use S3 or similar for image storage
8. **Security**: Add security headers and input validation