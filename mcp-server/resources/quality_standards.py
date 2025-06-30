import json
import os
from typing import Any, Dict
from resources.base import BaseResource


class QualityStandardsResource(BaseResource):
    def __init__(self):
        super().__init__("quality_standards")
        self.standards_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "templates", "quality_standards.json"
        )
    
    async def get_standards(self) -> Dict[str, Any]:
        try:
            with open(self.standards_file, 'r') as f:
                data = json.load(f)
            
            self.log_access("get_standards")
            return data.get("quality_standards", {})
            
        except FileNotFoundError:
            self.logger.error(f"Standards file not found: {self.standards_file}")
            return self._get_default_standards()
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in standards file: {e}")
            return self._get_default_standards()
    
    async def get_data(self) -> Dict[str, Any]:
        return await self.get_standards()
    
    async def get_quality_threshold(self) -> float:
        standards = await self.get_standards()
        return standards.get("image_quality", {}).get("minimum_score", 0.7)
    
    async def get_retry_conditions(self) -> Dict[str, Any]:
        standards = await self.get_standards()
        return standards.get("retry_conditions", {})
    
    async def should_retry_based_on_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        retry_conditions = await self.get_retry_conditions()
        retry_recommendations = []
        
        for result in analysis_results.get("results", []):
            quality_score = result.get("quality_analysis", {}).get("quality_score", 0.0)
            category = result.get("classification", {}).get("classification", {}).get("category", "other")
            confidence = result.get("classification", {}).get("classification", {}).get("confidence", 0.0)
            
            for condition_name, condition_data in retry_conditions.items():
                condition = condition_data.get("condition", "")
                
                should_retry = False
                if "quality_score < 0.5" in condition and quality_score < 0.5:
                    should_retry = True
                elif "category == 'other'" in condition and category == "other" and confidence < 0.6:
                    should_retry = True
                
                if should_retry:
                    retry_recommendations.append({
                        "image_path": result.get("image_path", ""),
                        "condition": condition_name,
                        "action": condition_data.get("action", ""),
                        "priority": condition_data.get("priority", "medium"),
                        "details": {
                            "quality_score": quality_score,
                            "category": category,
                            "confidence": confidence
                        }
                    })
        
        return {
            "should_retry": len(retry_recommendations) > 0,
            "recommendations": retry_recommendations,
            "high_priority_count": sum(1 for r in retry_recommendations if r["priority"] == "high")
        }
    
    def _get_default_standards(self) -> Dict[str, Any]:
        return {
            "image_quality": {
                "minimum_score": 0.7,
                "excellent_threshold": 0.8
            },
            "content_relevance": {
                "high": {"score_multiplier": 1.0},
                "medium": {"score_multiplier": 0.7},
                "low": {"score_multiplier": 0.3}
            },
            "retry_conditions": {
                "quality_threshold_failure": {
                    "condition": "quality_score < 0.5",
                    "action": "Recommend retaking photo",
                    "priority": "high"
                }
            }
        }