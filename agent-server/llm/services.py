"""
LLM services for photo classification and feedback generation
"""

import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based operations"""
    
    def __init__(self, openai_client: Optional[AsyncOpenAI] = None):
        self.openai_client = openai_client
    
    async def classify_photo(
        self, 
        image_data: str, 
        job_context: Optional[str], 
        categories: List[str]
    ) -> Dict[str, Any]:
        """Classify image using OpenAI vision model"""
        if not self.openai_client:
            return self._fallback_classification()
        
        context_prompt = f"Job context: {job_context}\n\n" if job_context else ""
        
        prompt = f"""{context_prompt}Analyze this job site photo and classify it into one of these categories:
        
        Categories:
        {chr(10).join(f"- {cat}: {cat.replace('_', ' ').title()}" for cat in categories)}
        
        Provide your response as JSON with:
        - category: the most appropriate category
        - confidence: confidence score (0.0-1.0)
        - description: brief description of what you see
        - relevance: how relevant this photo is for job documentation (high/medium/low)
        - quality_flags: any quality issues (blurry, dark, unclear, etc.)
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
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
            
            try:
                result = json.loads(content)
                if "category" not in result or result["category"] not in categories:
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
            logger.error(f"LLM classification failed: {e}")
            return self._fallback_classification()
    
    async def generate_feedback(
        self, 
        analysis_summary: str, 
        reflection_notes: List[str]
    ) -> str:
        """Generate personalized feedback using LLM"""
        if not self.openai_client:
            return "Unable to generate personalized feedback. Please review the analysis summary."
        
        reflection_context = "\n".join(reflection_notes) if reflection_notes else "No specific issues identified."
        
        prompt = f"""Based on the following photo analysis results, provide personalized feedback for a field technician:

        Analysis Summary:
        {analysis_summary}

        Additional Context:
        {reflection_context}

        Please provide:
        1. Overall assessment of the photo documentation quality
        2. Specific issues found and their impact on job documentation
        3. Concrete recommendations for improvement
        4. Any photos that should be retaken and why
        5. Positive feedback on good quality photos

        Keep the tone professional but supportive. Focus on actionable advice.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.warning(f"LLM feedback generation failed: {e}")
            return "Unable to generate personalized feedback. Please review the analysis summary above."
    
    def _fallback_classification(self) -> Dict[str, Any]:
        """Fallback classification when LLM is unavailable"""
        return {
            "category": "other",
            "confidence": 0.5,
            "description": "Classification unavailable",
            "relevance": "medium",
            "quality_flags": []
        }


def create_summary(classifications: List[Dict], quality_results: List[Dict]) -> Dict[str, Any]:
    """Create summary of classification and quality results"""
    total = len(classifications)
    if total == 0:
        return {}
    
    quality_passes = sum(1 for qa in quality_results if qa.get("passes_threshold", False))
    
    categories = {}
    for classification in classifications:
        category = classification.get("category", "other")
        categories[category] = categories.get(category, 0) + 1
    
    avg_confidence = sum(c.get("confidence", 0) for c in classifications) / total
    avg_quality_score = sum(qa.get("combined_score", 0) for qa in quality_results) / total
    
    return {
        "total_images": total,
        "quality_pass_rate": quality_passes / total,
        "categories": categories,
        "average_confidence": avg_confidence,
        "average_combined_score": avg_quality_score
    }