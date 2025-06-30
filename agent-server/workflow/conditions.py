"""
Conditional logic for LangGraph workflow
"""

from models.state import TriageState
from config.settings import settings


def should_reflect(state: TriageState) -> str:
    """Determine if reflection is needed based on analysis results"""
    if not settings.reflection_enabled:
        return "generate_feedback"
    
    if not state["analysis_results"]:
        return "generate_feedback"
    
    quality_issues_exist = len(state["quality_issues"]) > 0
    low_quality_rate = (
        state["analysis_results"].get("summary", {}).get("quality_pass_rate", 1.0) < 0.7
    )
    
    if quality_issues_exist or low_quality_rate:
        return "reflect"
    
    return "generate_feedback"


def should_retry(state: TriageState) -> str:
    """Determine if retry is needed based on reflection results"""
    if not state["retry_needed"]:
        return "generate_feedback"
    
    if state["current_attempt"] >= state["max_attempts"]:
        return "generate_feedback"
    
    return "retry"