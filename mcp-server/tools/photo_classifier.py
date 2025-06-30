import base64
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from core.config import settings
from utils.validation import validate_image_file
from utils.image_utils import get_image_metadata, resize_image_if_needed
from utils.exceptions import ModelError
from tools.base import BaseTool


class PhotoClassifierTool(BaseTool):
    def __init__(self):
        super().__init__("photo_classifier")
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        
        self.categories = [
            "equipment_photo",
            "before_work",
            "during_work", 
            "after_work",
            "damage_assessment",
            "safety_documentation",
            "material_inventory",
            "environmental_conditions",
            "other"
        ]
    
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        return await self.classify(args[0], kwargs.get('job_context'))
    
    async def classify(self, image_path: str, job_context: Optional[str] = None) -> Dict[str, Any]:
        try:
            validate_image_file(image_path)
            
            resized_path = resize_image_if_needed(image_path)
            
            with open(resized_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()
            
            classification = await self._classify_with_vision_model(image_data, job_context)
            metadata = get_image_metadata(image_path)
            
            result = {
                "image_path": image_path,
                "classification": classification,
                "metadata": metadata,
                "confidence_score": classification.get("confidence", 0.0),
                "job_context": job_context
            }
            
            self.log_execution("classify", {"image_path": image_path, "category": classification.get("category")})
            return result
            
        except Exception as e:
            self.logger.error(f"Classification failed for {image_path}: {e}")
            return {"error": str(e), "image_path": image_path}
    
    async def _classify_with_vision_model(self, image_data: str, job_context: Optional[str] = None) -> Dict[str, Any]:
        if not self.client:
            raise ModelError("OpenAI API key not configured")
        
        context_prompt = f"Job context: {job_context}\n\n" if job_context else ""
        
        prompt = f"""{context_prompt}Analyze this job site photo and classify it into one of these categories:
        
        Categories:
        - equipment_photo: Photos of tools, machinery, or equipment
        - before_work: Photos taken before starting work (initial conditions)
        - during_work: Photos taken while work is in progress
        - after_work: Photos showing completed work or final results
        - damage_assessment: Photos documenting damage or issues
        - safety_documentation: Photos related to safety protocols or hazards
        - material_inventory: Photos of materials, parts, or supplies  
        - environmental_conditions: Photos of weather, site conditions, or surroundings
        - other: Photos that don't fit the above categories
        
        Provide your response as JSON with:
        - category: the most appropriate category
        - confidence: confidence score (0.0-1.0)
        - description: brief description of what you see
        - relevance: how relevant this photo is for job documentation (high/medium/low)
        - quality_flags: any quality issues (blurry, dark, unclear, etc.)
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            import json
            try:
                result = json.loads(content)
                if "category" not in result or result["category"] not in self.categories:
                    result["category"] = "other"
                return result
            except json.JSONDecodeError:
                return {
                    "category": "other",
                    "confidence": 0.5,
                    "description": content,
                    "relevance": "medium",
                    "quality_flags": []
                }
                
        except Exception as e:
            raise ModelError(f"Vision model classification failed: {e}")