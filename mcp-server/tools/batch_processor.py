import asyncio
from typing import Any, Dict, List, Optional
from utils.validation import validate_batch_images
from tools.photo_classifier import PhotoClassifierTool
from tools.quality_analyzer import QualityAnalyzerTool
from tools.base import BaseTool


class BatchProcessorTool(BaseTool):
    def __init__(self):
        super().__init__("batch_processor")
        self.classifier = PhotoClassifierTool()
        self.quality_analyzer = QualityAnalyzerTool()
    
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        return await self.process(args[0], kwargs.get('job_context'))
    
    async def process(self, image_paths: List[str], job_context: Optional[str] = None) -> Dict[str, Any]:
        try:
            validated_paths = validate_batch_images(image_paths)
            
            classification_tasks = [
                self.classifier.classify(path, job_context) 
                for path in validated_paths
            ]
            quality_tasks = [
                self.quality_analyzer.analyze(path) 
                for path in validated_paths
            ]
            
            classifications = await asyncio.gather(*classification_tasks, return_exceptions=True)
            quality_analyses = await asyncio.gather(*quality_tasks, return_exceptions=True)
            
            results = []
            for i, path in enumerate(validated_paths):
                classification = classifications[i] if not isinstance(classifications[i], Exception) else {"error": str(classifications[i])}
                quality = quality_analyses[i] if not isinstance(quality_analyses[i], Exception) else {"error": str(quality_analyses[i])}
                
                results.append({
                    "image_path": path,
                    "classification": classification,
                    "quality_analysis": quality,
                    "combined_score": self._calculate_combined_score(classification, quality)
                })
            
            summary = self._generate_batch_summary(results)
            
            result = {
                "total_images": len(validated_paths),
                "processed_images": len(results),
                "results": results,
                "summary": summary,
                "job_context": job_context
            }
            
            self.log_execution("process_batch", {
                "total_images": len(validated_paths),
                "job_context": job_context
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return {"error": str(e), "image_paths": image_paths}
    
    def _calculate_combined_score(self, classification: Dict[str, Any], quality: Dict[str, Any]) -> float:
        if "error" in classification or "error" in quality:
            return 0.0
        
        confidence = classification.get("classification", {}).get("confidence", 0.5)
        quality_score = quality.get("quality_score", 0.5)
        
        relevance_weight = {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.3
        }
        
        relevance = classification.get("classification", {}).get("relevance", "medium")
        relevance_multiplier = relevance_weight.get(relevance, 0.7)
        
        combined_score = (confidence * 0.4 + quality_score * 0.6) * relevance_multiplier
        return round(combined_score, 3)
    
    def _generate_batch_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        if total == 0:
            return {"total": 0}
        
        successful = sum(1 for r in results if "error" not in r["classification"] and "error" not in r["quality_analysis"])
        
        quality_passes = sum(1 for r in results 
                           if r["quality_analysis"].get("passes_threshold", False))
        
        categories = {}
        quality_grades = {}
        
        for result in results:
            if "error" not in result["classification"]:
                category = result["classification"]["classification"].get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
            
            if "error" not in result["quality_analysis"]:
                grade = result["quality_analysis"].get("quality_grade", "unknown")
                quality_grades[grade] = quality_grades.get(grade, 0) + 1
        
        avg_combined_score = sum(r["combined_score"] for r in results) / total if total > 0 else 0
        
        return {
            "total": total,
            "successful": successful,
            "quality_passes": quality_passes,
            "quality_pass_rate": quality_passes / total if total > 0 else 0,
            "categories": categories,
            "quality_grades": quality_grades,
            "average_combined_score": round(avg_combined_score, 3),
            "recommendations": self._get_batch_recommendations(results)
        }
    
    def _get_batch_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        recommendations = []
        
        quality_fails = [r for r in results 
                        if not r["quality_analysis"].get("passes_threshold", False)]
        
        if quality_fails:
            recommendations.append(f"{len(quality_fails)} images failed quality checks and should be retaken")
        
        low_relevance = [r for r in results 
                        if r["classification"]["classification"].get("relevance") == "low"]
        
        if low_relevance:
            recommendations.append(f"{len(low_relevance)} images have low job relevance")
        
        uncategorized = [r for r in results 
                        if r["classification"]["classification"].get("category") == "other"]
        
        if uncategorized:
            recommendations.append(f"{len(uncategorized)} images could not be properly categorized")
        
        return recommendations