from typing import Any, Dict, List
from core.config import settings
from utils.validation import validate_image_file
from utils.image_utils import calculate_image_quality_score, get_image_metadata
from utils.exceptions import QualityAnalysisError
from tools.base import BaseTool


class QualityAnalyzerTool(BaseTool):
    def __init__(self):
        super().__init__("quality_analyzer")
        self.quality_threshold = settings.image_quality_threshold
    
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        return await self.analyze(args[0])
    
    async def analyze(self, image_path: str) -> Dict[str, Any]:
        try:
            validate_image_file(image_path)
            
            quality_score = calculate_image_quality_score(image_path)
            metadata = get_image_metadata(image_path)
            
            analysis = self._analyze_quality_factors(quality_score, metadata)
            
            result = {
                "image_path": image_path,
                "quality_score": quality_score,
                "quality_grade": self._get_quality_grade(quality_score),
                "passes_threshold": bool(quality_score >= self.quality_threshold),
                "analysis": analysis,
                "metadata": metadata,
                "recommendations": self._get_recommendations(quality_score, analysis)
            }
            
            self.log_execution("analyze", {
                "image_path": image_path, 
                "quality_score": quality_score,
                "passes_threshold": result["passes_threshold"]
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed for {image_path}: {e}")
            return {"error": str(e), "image_path": image_path}
    
    def _analyze_quality_factors(self, quality_score: float, metadata: Dict[str, Any]) -> Dict[str, Any]:
        analysis = {
            "sharpness": "good" if quality_score > 0.7 else "poor" if quality_score < 0.4 else "fair",
            "brightness": "unknown",
            "contrast": "unknown",
            "noise_level": "unknown"
        }
        
        size = metadata.get("size", (0, 0))
        if size[0] > 0 and size[1] > 0:
            total_pixels = size[0] * size[1]
            if total_pixels < 480000:  # Less than 800x600
                analysis["resolution"] = "low"
            elif total_pixels < 2073600:  # Less than 1920x1080
                analysis["resolution"] = "medium"
            else:
                analysis["resolution"] = "high"
        else:
            analysis["resolution"] = "unknown"
        
        return analysis
    
    def _get_quality_grade(self, quality_score: float) -> str:
        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "good"
        elif quality_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _get_recommendations(self, quality_score: float, analysis: Dict[str, Any]) -> List[str]:
        recommendations = []
        
        if quality_score < self.quality_threshold:
            recommendations.append("Image quality is below acceptable threshold")
            
            if analysis.get("sharpness") == "poor":
                recommendations.append("Image appears blurry - ensure camera is steady and focused")
            
            if analysis.get("resolution") == "low":
                recommendations.append("Consider using higher resolution camera settings")
            
            recommendations.append("Retake photo with better lighting and stability")
        
        elif quality_score < 0.8:
            recommendations.append("Image quality is acceptable but could be improved")
            
            if analysis.get("resolution") == "low":
                recommendations.append("Consider using higher resolution for better detail")
        
        return recommendations