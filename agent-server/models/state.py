"""
State management for LangGraph triage workflow
"""

from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage


class TriageState(TypedDict):
    """State for the photo triage workflow"""
    messages: List[BaseMessage]
    image_paths: List[str]
    job_context: Optional[str]
    current_attempt: int
    max_attempts: int
    raw_photo_data: Optional[List[Dict[str, Any]]]
    quality_results: Optional[List[Dict[str, Any]]]
    analysis_results: Optional[Dict[str, Any]]
    quality_issues: List[str]
    reflection_notes: List[str]
    final_feedback: Optional[str]
    retry_needed: bool
    completed: bool


def create_initial_state(
    image_paths: List[str], 
    job_context: Optional[str] = None,
    max_attempts: int = 3
) -> TriageState:
    """Create initial state for triage workflow"""
    from langchain_core.messages import HumanMessage
    
    return {
        "messages": [HumanMessage(content=f"Analyze {len(image_paths)} photos for job triage")],
        "image_paths": image_paths,
        "job_context": job_context,
        "current_attempt": 1,
        "max_attempts": max_attempts,
        "raw_photo_data": None,
        "quality_results": None,
        "analysis_results": None,
        "quality_issues": [],
        "reflection_notes": [],
        "final_feedback": None,
        "retry_needed": False,
        "completed": False
    }