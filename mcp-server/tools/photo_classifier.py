import base64
from typing import Any, Dict, Optional
from utils.validation import validate_image_file
from utils.image_utils import get_image_metadata, resize_image_if_needed
from tools.base import BaseTool


class PhotoClassifierTool(BaseTool):
    def __init__(self):
        super().__init__("photo_classifier")
        
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
            
            # Return image data and metadata for LLM processing by agent
            metadata = get_image_metadata(image_path)
            
            result = {
                "image_path": image_path,
                "image_data": image_data,  # Base64 encoded image for LLM
                "metadata": metadata,
                "job_context": job_context,
                "categories": self.categories,  # Available categories
                "ready_for_llm_analysis": True
            }
            
            self.log_execution("classify", {"image_path": image_path})
            return result
            
        except Exception as e:
            self.logger.error(f"Classification failed for {image_path}: {e}")
            return {"error": str(e), "image_path": image_path}
    
