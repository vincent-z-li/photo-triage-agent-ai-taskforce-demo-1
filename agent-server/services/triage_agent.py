"""
Refactored Triage Agent using modular LangGraph components
"""

from typing import Any, Dict, List, Optional
from langsmith import traceable
from openai import AsyncOpenAI

from config.settings import settings
from config.logging import get_logger
from models.state import create_initial_state
from llm.services import LLMService
from workflow.builder import WorkflowBuilder

logger = get_logger(__name__)


class TriageAgent:
    """
    Main triage agent orchestrating photo analysis workflow using LangGraph
    
    This agent coordinates between MCP server (for image processing/quality analysis)
    and LLM services (for classification and feedback generation) through a 
    structured workflow.
    """
    
    def __init__(self):
        """Initialize the triage agent with LLM service and workflow"""
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.llm_service = LLMService(self.openai_client)
        
        # Build the workflow graph
        workflow_builder = WorkflowBuilder(self.llm_service)
        self.graph = workflow_builder.build_workflow()
    
    @traceable(name="triage_workflow")
    async def run_triage_workflow(
        self, 
        image_paths: List[str], 
        job_context: Optional[str] = None,
        enable_retry: bool = True
    ) -> Dict[str, Any]:
        """
        Run the complete triage workflow for a set of images
        
        Args:
            image_paths: List of paths to images to analyze
            job_context: Optional context about the job for better analysis
            enable_retry: Whether to enable retry logic for poor quality results
            
        Returns:
            Dict containing workflow results including analysis, feedback, and metadata
        """
        max_attempts = settings.max_retry_attempts if enable_retry else 1
        initial_state = create_initial_state(image_paths, job_context, max_attempts)
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            return {
                "success": True,
                "analysis_results": final_state["analysis_results"],
                "final_feedback": final_state["final_feedback"],
                "attempts_made": final_state["current_attempt"],
                "quality_issues": final_state["quality_issues"],
                "reflection_notes": final_state["reflection_notes"]
            }
            
        except Exception as e:
            logger.error(f"Triage workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_results": None,
                "final_feedback": None
            }