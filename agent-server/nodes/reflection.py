"""
Reflection and retry nodes for LangGraph workflow
"""

import logging
from langsmith import traceable
from langchain_core.messages import AIMessage

from models.state import TriageState
from config.settings import settings

logger = logging.getLogger(__name__)


@traceable(name="reflect_on_results")
async def reflect_on_results(state: TriageState) -> TriageState:
    """Reflect on analysis results and determine if retry is needed"""
    logger.info("Reflecting on analysis results")
    
    if not state["analysis_results"]:
        state["reflection_notes"].append("No analysis results to reflect on")
        return state
    
    results = state["analysis_results"]
    
    reflection_notes = []
    
    quality_pass_rate = results.get("summary", {}).get("quality_pass_rate", 0)
    if quality_pass_rate < settings.image_quality_threshold:
        reflection_notes.append(f"Low quality pass rate: {quality_pass_rate:.2%}")
        reflection_notes.append("Many images may need to be retaken")
    
    categories = results.get("summary", {}).get("categories", {})
    if "other" in categories and categories["other"] > len(state["image_paths"]) * 0.3:
        reflection_notes.append("Many images are uncategorized - may indicate unclear photo subjects")
    
    avg_score = results.get("summary", {}).get("average_combined_score", 0)
    if avg_score < 0.5:
        reflection_notes.append(f"Low average combined score: {avg_score:.3f}")
        reflection_notes.append("Overall photo documentation quality needs improvement")
    
    if not reflection_notes:
        reflection_notes.append("Analysis results look good overall")
    
    state["reflection_notes"].extend(reflection_notes)
    state["messages"].append(
        AIMessage(content=f"Reflection completed with {len(reflection_notes)} observations")
    )
    
    state["retry_needed"] = (
        quality_pass_rate < 0.5 and 
        state["current_attempt"] < state["max_attempts"] and
        settings.reflection_enabled
    )
    
    return state


@traceable(name="prepare_retry")
async def prepare_retry(state: TriageState) -> TriageState:
    """Prepare for retry attempt"""
    logger.info(f"Preparing retry - attempt {state['current_attempt'] + 1}")
    
    state["current_attempt"] += 1
    
    retry_notes = [
        f"Retry attempt {state['current_attempt']} due to quality issues:",
        *state["quality_issues"][:3]  # Show top 3 issues
    ]
    
    state["reflection_notes"].extend(retry_notes)
    state["messages"].append(
        AIMessage(content=f"Preparing retry attempt {state['current_attempt']}")
    )
    
    return state