import json
import os
from typing import Any, Dict, List, Optional
from resources.base import BaseResource


class JobTemplatesResource(BaseResource):
    def __init__(self):
        super().__init__("job_templates")
        self.templates_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "templates", "job_templates.json"
        )
    
    async def get_templates(self) -> List[Dict[str, Any]]:
        try:
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
            
            self.log_access("get_templates", {"count": len(data.get("templates", []))})
            return data.get("templates", [])
            
        except FileNotFoundError:
            self.logger.error(f"Templates file not found: {self.templates_file}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in templates file: {e}")
            return []
    
    async def get_data(self) -> List[Dict[str, Any]]:
        return await self.get_templates()
    
    async def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        templates = await self.get_templates()
        for template in templates:
            if template.get("id") == template_id:
                self.log_access("get_template_by_id", {"template_id": template_id})
                return template
        return None
    
    async def get_requirements_for_job(self, job_type: str) -> Dict[str, Any]:
        template = await self.get_template_by_id(job_type)
        if template:
            return {
                "required_categories": template.get("required_photo_categories", []),
                "optional_categories": template.get("optional_categories", []),
                "quality_requirements": template.get("quality_requirements", {}),
                "description": template.get("description", "")
            }
        return {
            "required_categories": ["before_work", "after_work"],
            "optional_categories": ["equipment_photo", "during_work"],
            "quality_requirements": {"minimum_photos": 2, "quality_threshold": 0.6},
            "description": "General job requirements"
        }