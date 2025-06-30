from typing import Any, Dict, List
from tools.base import BaseTool


class FeedbackGeneratorTool(BaseTool):
    def __init__(self):
        super().__init__("feedback_generator")
    
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        return await self.generate(args[0], args[1])
    
    async def generate(
        self, 
        classification_results: List[Dict[str, Any]], 
        quality_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        try:
            # Generate template-based feedback and analysis data
            feedback = self._generate_template_feedback(classification_results, quality_results)
            analysis_summary = self._create_analysis_summary(classification_results, quality_results)
            
            result = {
                "feedback": feedback,
                "analysis_summary": analysis_summary,
                "total_images_analyzed": len(classification_results),
                "actionable_items": self._extract_actionable_items(feedback),
                "priority_level": self._determine_priority_level(classification_results, quality_results)
            }
            
            self.log_execution("generate_feedback", {
                "total_images": len(classification_results),
                "priority": result["priority_level"]
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Feedback generation failed: {e}")
            return {"error": str(e)}
    
    
    def _create_analysis_summary(
        self, 
        classifications: List[Dict[str, Any]], 
        quality_analyses: List[Dict[str, Any]]
    ) -> str:
        total = len(classifications)
        
        quality_passes = sum(1 for qa in quality_analyses 
                           if qa.get("passes_threshold", False))
        
        categories = {}
        quality_issues = []
        
        for i, classification in enumerate(classifications):
            if "classification" in classification:
                category = classification["classification"].get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
                
                if i < len(quality_analyses):
                    qa = quality_analyses[i]
                    if not qa.get("passes_threshold", False):
                        quality_issues.append(f"Image {i+1}: {qa.get('quality_grade', 'poor')} quality")
        
        summary = f"""
        Total Images: {total}
        Quality Pass Rate: {quality_passes}/{total} ({quality_passes/total*100:.1f}%)
        
        Categories Distribution:
        {chr(10).join(f"- {cat}: {count}" for cat, count in categories.items())}
        
        Quality Issues:
        {chr(10).join(quality_issues) if quality_issues else "No major quality issues"}
        """
        
        return summary
    
    def _generate_template_feedback(
        self, 
        classifications: List[Dict[str, Any]], 
        quality_analyses: List[Dict[str, Any]]
    ) -> str:
        total = len(classifications)
        quality_passes = sum(1 for qa in quality_analyses 
                           if qa.get("passes_threshold", False))
        
        quality_fails = total - quality_passes
        
        feedback_parts = []
        
        feedback_parts.append(f"Photo Documentation Analysis Complete")
        feedback_parts.append(f"Total photos analyzed: {total}")
        
        if quality_passes == total:
            feedback_parts.append("✅ All photos meet quality standards - excellent work!")
        elif quality_passes > total * 0.7:
            feedback_parts.append(f"✅ Most photos meet quality standards ({quality_passes}/{total})")
            feedback_parts.append(f"⚠️  {quality_fails} photos need attention")
        else:
            feedback_parts.append(f"⚠️  {quality_fails} photos failed quality checks")
            feedback_parts.append("📸 Consider retaking photos with better lighting and focus")
        
        categories = {}
        for classification in classifications:
            if "classification" in classification:
                category = classification["classification"].get("category", "unknown")
                categories[category] = categories.get(category, 0) + 1
        
        if categories:
            feedback_parts.append("\nPhoto Categories:")
            for category, count in categories.items():
                feedback_parts.append(f"- {category.replace('_', ' ').title()}: {count}")
        
        if quality_fails > 0:
            feedback_parts.append("\nRecommendations:")
            feedback_parts.append("- Ensure proper lighting when taking photos")
            feedback_parts.append("- Hold camera steady to avoid blur")
            feedback_parts.append("- Take multiple shots of important areas")
            feedback_parts.append("- Review photos before leaving the site")
        
        return "\n".join(feedback_parts)
    
    def _extract_actionable_items(self, feedback: str) -> List[str]:
        actionable_items = []
        
        lines = feedback.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['retake', 'improve', 'consider', 'ensure', 'review']):
                if line and not line.startswith(('✅', '⚠️', '📸', '#', '-')):
                    actionable_items.append(line)
                elif line.startswith('- '):
                    actionable_items.append(line[2:])
        
        return actionable_items[:5]  # Limit to top 5 items
    
    def _determine_priority_level(
        self, 
        classifications: List[Dict[str, Any]], 
        quality_analyses: List[Dict[str, Any]]
    ) -> str:
        if not classifications or not quality_analyses:
            return "medium"
        
        quality_fails = sum(1 for qa in quality_analyses 
                          if not qa.get("passes_threshold", False))
        
        fail_rate = quality_fails / len(quality_analyses)
        
        if fail_rate > 0.5:
            return "high"
        elif fail_rate > 0.2:
            return "medium"
        else:
            return "low"