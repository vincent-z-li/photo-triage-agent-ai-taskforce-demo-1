"""
Refactored Triage Agent using modular LangGraph components
"""

from typing import Any, Dict, List, Optional, AsyncGenerator
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
    
    # TODO: Double check on the streaming workflow
    @traceable(name="triage_workflow_stream")
    async def run_triage_workflow_stream(
        self, 
        image_paths: List[str], 
        job_context: Optional[str] = None,
        enable_retry: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run the complete triage workflow for a set of images with streaming updates
        
        Args:
            image_paths: List of paths to images to analyze
            job_context: Optional context about the job for better analysis
            enable_retry: Whether to enable retry logic for poor quality results
            
        Yields:
            Dict containing streaming workflow updates and results
        """
        max_attempts = settings.max_retry_attempts if enable_retry else 1
        initial_state = create_initial_state(image_paths, job_context, max_attempts)
        
        try:
            yield {
                "status": "started",
                "tool": "triage_with_reflection",
                "step": "initialize",
                "message": "Starting photo triage workflow"
            }
            
            current_state = initial_state
            
            yield {
                "status": "processing",
                "step": "quality_analysis", 
                "message": "Analyzing photo quality"
            }
            
            from nodes.analysis import analyze_photos
            current_state = await analyze_photos(current_state)
            
            yield {
                "status": "step_completed",
                "step": "quality_analysis",
                "result": current_state.get("analysis_results"),
                "message": "Photo quality analysis completed"
            }
            
            yield {
                "status": "processing", 
                "step": "classification",
                "message": "Classifying photos with AI"
            }
            
            from nodes.classification import classify_photos_with_llm
            current_state = await classify_photos_with_llm(current_state, self.llm_service)
            
            yield {
                "status": "step_completed",
                "step": "classification", 
                "result": current_state.get("classification_results"),
                "message": "Photo classification completed"
            }
            
            from workflow.conditions import should_reflect
            reflection_needed = should_reflect(current_state)
            
            if reflection_needed == "reflect":
                yield {
                    "status": "processing",
                    "step": "reflection",
                    "message": "Reflecting on results and analyzing quality"
                }
                
                from nodes.reflection import reflect_on_results
                current_state = await reflect_on_results(current_state)
                
                yield {
                    "status": "step_completed",
                    "step": "reflection",
                    "result": current_state.get("reflection_notes"),
                    "message": "Reflection completed"
                }
                
                from workflow.conditions import should_retry
                retry_needed = should_retry(current_state)
                
                if retry_needed == "retry" and current_state["current_attempt"] < current_state["max_attempts"]:
                    yield {
                        "status": "processing",
                        "step": "retry_preparation", 
                        "message": f"Preparing retry attempt {current_state['current_attempt'] + 1}"
                    }
                    
                    from nodes.reflection import prepare_retry
                    current_state = await prepare_retry(current_state)
                    
                    yield {
                        "status": "processing",
                        "step": "retry_analysis",
                        "message": "Re-analyzing photos with improved parameters"
                    }
                    
                    current_state = await analyze_photos(current_state)
                    current_state = await classify_photos_with_llm(current_state, self.llm_service)
                    
                    yield {
                        "status": "step_completed",
                        "step": "retry_analysis",
                        "message": "Retry analysis completed"
                    }
            
            yield {
                "status": "processing",
                "step": "feedback",
                "message": "Generating final feedback and recommendations"
            }
            
            from nodes.feedback import generate_final_feedback
            final_state = await generate_final_feedback(current_state, self.llm_service)
            
            yield {
                "status": "step_completed", 
                "step": "feedback",
                "result": final_state.get("final_feedback"),
                "message": "Final feedback generated"
            }
            
            yield {
                "status": "result",
                "success": True,
                "analysis_results": final_state["analysis_results"],
                "classification_results": final_state["classification_results"], 
                "final_feedback": final_state["final_feedback"],
                "attempts_made": final_state["current_attempt"],
                "quality_issues": final_state["quality_issues"],
                "reflection_notes": final_state["reflection_notes"],
                "message": "Triage workflow completed successfully"
            }
                    
        except Exception as e:
            logger.error(f"Streaming triage workflow failed: {e}")
            yield {
                "status": "error",
                "error": str(e),
                "success": False,
                "message": f"Workflow failed: {str(e)}"
            }