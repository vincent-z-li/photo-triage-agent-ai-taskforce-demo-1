"""
LLM classification node for LangGraph workflow
"""

import logging
from langsmith import traceable
from langchain_core.messages import AIMessage

from models.state import TriageState
from llm.services import LLMService, create_summary

logger = logging.getLogger(__name__)


@traceable(name="classify_photos_with_llm")
async def classify_photos_with_llm(
    state: TriageState, 
    llm_service: LLMService
) -> TriageState:
    """Classify photos using LLM vision model"""
    logger.info("Classifying photos with LLM")
    
    try:
        classifications = []
        for photo_data in state.get("raw_photo_data", []):
            if "error" in photo_data:
                classifications.append({
                    "category": "other",
                    "confidence": 0.0,
                    "description": f"Error: {photo_data['error']}",
                    "relevance": "low",
                    "quality_flags": ["processing_error"]
                })
                continue
            
            classification = await llm_service.classify_photo(
                photo_data["image_data"], 
                photo_data["job_context"],
                photo_data["categories"]
            )
            classifications.append(classification)
        
        # Combine with quality results
        state["analysis_results"] = {
            "results": [
                {
                    "image_path": photo["image_path"],
                    "classification": classifications[i],
                    "quality_analysis": state["quality_results"][i]
                }
                for i, photo in enumerate(state.get("raw_photo_data", []))
            ],
            "summary": create_summary(classifications, state.get("quality_results", []))
        }
        
        state["messages"].append(
            AIMessage(content=f"LLM classification completed for {len(classifications)} photos")
        )
        
    except Exception as e:
        logger.error(f"LLM classification failed: {e}")
        state["messages"].append(AIMessage(content=f"LLM classification failed: {str(e)}"))
        # Fallback to basic results
        state["analysis_results"] = {"error": str(e)}
    
    return state