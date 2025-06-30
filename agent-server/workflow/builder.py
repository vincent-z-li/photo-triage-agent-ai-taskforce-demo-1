"""
Workflow builder for LangGraph triage workflow
"""

from functools import partial
from langgraph.graph import StateGraph, END, START

from models.state import TriageState
from nodes.analysis import analyze_photos
from nodes.classification import classify_photos_with_llm
from nodes.reflection import reflect_on_results, prepare_retry
from nodes.feedback import generate_final_feedback
from llm.services import LLMService
from .conditions import should_reflect, should_retry


class WorkflowBuilder:
    """Builder for creating the triage workflow graph"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def build_workflow(self) -> StateGraph:
        """Build and compile the complete triage workflow"""
        workflow = StateGraph(TriageState)
        
        # Add nodes with partial functions to inject dependencies
        workflow.add_node("analyze", analyze_photos)
        workflow.add_node(
            "classify_with_llm", 
            partial(classify_photos_with_llm, llm_service=self.llm_service)
        )
        workflow.add_node("reflect", reflect_on_results)
        workflow.add_node("retry", prepare_retry)
        workflow.add_node(
            "generate_feedback", 
            partial(generate_final_feedback, llm_service=self.llm_service)
        )
        
        # Define workflow edges
        workflow.add_edge(START, "analyze")
        workflow.add_edge("analyze", "classify_with_llm")
        
        workflow.add_conditional_edges(
            "classify_with_llm",
            should_reflect,
            {
                "reflect": "reflect",
                "generate_feedback": "generate_feedback"
            }
        )
        
        workflow.add_conditional_edges(
            "reflect",
            should_retry,
            {
                "retry": "retry",
                "generate_feedback": "generate_feedback"
            }
        )
        
        workflow.add_edge("retry", "analyze")
        workflow.add_edge("generate_feedback", END)
        
        return workflow.compile()