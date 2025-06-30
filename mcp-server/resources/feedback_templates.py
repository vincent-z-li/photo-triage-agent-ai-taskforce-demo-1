import json
import os
from typing import Any, Dict, List
from resources.base import BaseResource


class FeedbackTemplatesResource(BaseResource):
    def __init__(self):
        super().__init__("feedback_templates")
        self.templates_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "templates", "feedback_templates.json"
        )
    
    async def get_templates(self) -> Dict[str, Any]:
        try:
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
            
            self.log_access("get_templates")
            return data.get("feedback_templates", {})
            
        except FileNotFoundError:
            self.logger.error(f"Templates file not found: {self.templates_file}")
            return self._get_default_templates()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in templates file: {e}")
            return self._get_default_templates()
    
    async def get_data(self) -> Dict[str, Any]:
        return await self.get_templates()
    
    async def get_quality_feedback_template(self, quality_grade: str) -> Dict[str, Any]:
        templates = await self.get_templates()
        quality_templates = templates.get("quality_assessment", {})
        
        template = quality_templates.get(quality_grade.lower(), 
                                       quality_templates.get("fair", {}))
        
        self.log_access("get_quality_feedback", {"grade": quality_grade})
        return template
    
    async def get_actionable_item_template(self, item_type: str) -> Dict[str, Any]:
        templates = await self.get_templates()
        actionable_templates = templates.get("actionable_items", {})
        
        template = actionable_templates.get(item_type, {})
        self.log_access("get_actionable_template", {"type": item_type})
        return template
    
    async def get_encouragement_messages(self) -> List[str]:
        templates = await self.get_templates()
        messages = templates.get("encouragement", [])
        self.log_access("get_encouragement", {"count": len(messages)})
        return messages
    
    def _get_default_templates(self) -> Dict[str, Any]:
        return {
            "quality_assessment": {
                "excellent": {
                    "message": "Excellent photo quality!",
                    "tone": "positive",
                    "recommendations": ["Continue this high standard"]
                },
                "good": {
                    "message": "Good photo quality overall.",
                    "tone": "encouraging", 
                    "recommendations": ["Minor improvements possible"]
                },
                "fair": {
                    "message": "Photos are acceptable but could be improved.",
                    "tone": "constructive",
                    "recommendations": ["Focus on image sharpness", "Ensure proper lighting"]
                },
                "poor": {
                    "message": "Photo quality needs improvement.",
                    "tone": "helpful",
                    "recommendations": ["Several photos should be retaken"]   
                }
            },
            "encouragement": [
                "Good documentation helps create valuable job records"
            ]
        }