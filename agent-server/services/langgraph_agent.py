import asyncio
import time
from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langsmith import traceable
import logging


from config.settings import settings
from config.logging import get_logger
from .mcp_client import MCPHttpClient

logger = get_logger(__name__)


class TriageState(TypedDict):
    messages: List[BaseMessage]
    image_paths: List[str]
    job_context: Optional[str]
    current_attempt: int
    max_attempts: int
    analysis_results: Optional[Dict[str, Any]]
    quality_issues: List[str]
    reflection_notes: List[str]
    final_feedback: Optional[str]
    retry_needed: bool
    completed: bool


class TriageAgent:
    def __init__(self):
        self.mcp_client = MCPHttpClient()
        self.graph = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(TriageState)
        
        workflow.add_node("analyze", self.analyze_photos)
        workflow.add_node("reflect", self.reflect_on_results)
        workflow.add_node("retry", self.prepare_retry)
        workflow.add_node("generate_feedback", self.generate_final_feedback)
        
        workflow.add_edge(START, "analyze")
        
        workflow.add_conditional_edges(
            "analyze",
            self.should_reflect,
            {
                "reflect": "reflect",
                "generate_feedback": "generate_feedback"
            }
        )
        
        workflow.add_conditional_edges(
            "reflect",
            self.should_retry,
            {
                "retry": "retry",
                "generate_feedback": "generate_feedback"
            }
        )
        
        workflow.add_edge("retry", "analyze")
        workflow.add_edge("generate_feedback", END)
        
        return workflow.compile()
    
    @traceable(name="triage_workflow")
    async def run_triage_workflow(
        self, 
        image_paths: List[str], 
        job_context: Optional[str] = None,
        enable_retry: bool = True
    ) -> Dict[str, Any]:
        initial_state: TriageState = {
            "messages": [HumanMessage(content=f"Analyze {len(image_paths)} photos for job triage")],
            "image_paths": image_paths,
            "job_context": job_context,
            "current_attempt": 1,
            "max_attempts": settings.max_retry_attempts if enable_retry else 1,
            "analysis_results": None,
            "quality_issues": [],
            "reflection_notes": [],
            "final_feedback": None,
            "retry_needed": False,
            "completed": False
        }
        
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
    
    @traceable(name="analyze_photos")
    async def analyze_photos(self, state: TriageState) -> TriageState:
        logger.info(f"Analyzing photos - attempt {state['current_attempt']}")
        
        try:
            async with self.mcp_client as client:
                analysis_results = await client.process_batch(
                    state["image_paths"], 
                    state["job_context"]
                )
            
            state["analysis_results"] = analysis_results
            state["messages"].append(
                AIMessage(content=f"Analysis completed for {len(state['image_paths'])} photos")
            )
            
            quality_issues = []
            if "results" in analysis_results:
                for result in analysis_results["results"]:
                    if not result["quality_analysis"].get("passes_threshold", False):
                        quality_issues.append(f"Image {result['image_path']}: {result['quality_analysis'].get('quality_grade', 'poor')} quality")
            
            state["quality_issues"] = quality_issues
            
        except Exception as e:
            logger.error(f"Photo analysis failed: {e}")
            state["messages"].append(AIMessage(content=f"Analysis failed: {str(e)}"))
            state["quality_issues"] = [f"Analysis error: {str(e)}"]
        
        return state
    
    @traceable(name="reflect_on_results")
    async def reflect_on_results(self, state: TriageState) -> TriageState:
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
    async def prepare_retry(self, state: TriageState) -> TriageState:
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
    
    @traceable(name="generate_final_feedback")
    async def generate_final_feedback(self, state: TriageState) -> TriageState:
        logger.info("Generating final feedback")
        
        try:
            if state["analysis_results"] and "results" in state["analysis_results"]:
                results = state["analysis_results"]["results"]
                
                classifications = [r["classification"] for r in results]
                quality_analyses = [r["quality_analysis"] for r in results]
                
                async with self.mcp_client as client:
                    feedback_result = await client.generate_feedback(
                        classifications, quality_analyses
                    )
                
                enhanced_feedback = self._enhance_feedback_with_reflection(
                    feedback_result.get("feedback", ""), 
                    state["reflection_notes"]
                )
                
                state["final_feedback"] = enhanced_feedback
                
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
    
    def should_reflect(self, state: TriageState) -> str:
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
    
    def should_retry(self, state: TriageState) -> str:
        if not state["retry_needed"]:
            return "generate_feedback"
        
        if state["current_attempt"] >= state["max_attempts"]:
            return "generate_feedback"
        
        return "retry"
    
    def _enhance_feedback_with_reflection(
        self, 
        base_feedback: str, 
        reflection_notes: List[str]
    ) -> str:
        if not reflection_notes:
            return base_feedback
        
        enhanced = base_feedback + "\n\nAdditional Insights:\n"
        for note in reflection_notes[-3:]:  # Show last 3 reflection notes
            enhanced += f"• {note}\n"
        
        return enhanced