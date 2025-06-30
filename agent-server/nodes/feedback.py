"""
Feedback generation node for LangGraph workflow
"""

import logging
from langsmith import traceable
from langchain_core.messages import AIMessage

from models.state import TriageState
from services.mcp_client import MCPHttpClient
from llm.services import LLMService

logger = logging.getLogger(__name__)


@traceable(name="generate_final_feedback")
async def generate_final_feedback(
    state: TriageState, 
    llm_service: LLMService
) -> TriageState:
    """Generate final feedback using both MCP templates and LLM enhancement"""
    logger.info("Generating final feedback")
    
    try:
        if state["analysis_results"] and "results" in state["analysis_results"]:
            results = state["analysis_results"]["results"]
            
            classifications = [r["classification"] for r in results]
            quality_analyses = [r["quality_analysis"] for r in results]
            
            # Get template-based feedback structure from MCP
            mcp_client = MCPHttpClient()
            async with mcp_client as client:
                template_result = await client.generate_feedback(
                    classifications, quality_analyses
                )
            
            # Use LLM to enhance the feedback if available
            enhanced_feedback = await llm_service.generate_feedback(
                template_result.get("analysis_summary", ""),
                state["reflection_notes"]
            )
            
            final_feedback = _enhance_feedback_with_reflection(
                enhanced_feedback, 
                state["reflection_notes"]
            )
            
            state["final_feedback"] = final_feedback
            
        else:
            state["final_feedback"] = "Analysis could not be completed successfully."
        
        state["completed"] = True
        state["messages"].append(
            AIMessage(content="Final feedback generated successfully")
        )
        
    except Exception as e:
        logger.error(f"Feedback generation failed: {e}")
        state["final_feedback"] = f"Feedback generation failed: {str(e)}"
    
    return state


def _enhance_feedback_with_reflection(
    base_feedback: str, 
    reflection_notes: list[str]
) -> str:
    """Enhance feedback with reflection notes"""
    if not reflection_notes:
        return base_feedback
    
    enhanced = base_feedback + "\n\nAdditional Insights:\n"
    for note in reflection_notes[-3:]:  # Show last 3 reflection notes
        enhanced += f"• {note}\n"
    
    return enhanced