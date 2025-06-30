"""
Photo analysis node for LangGraph workflow
"""

import logging
from langsmith import traceable
from langchain_core.messages import AIMessage

from models.state import TriageState
from services.mcp_client import MCPHttpClient

logger = logging.getLogger(__name__)


@traceable(name="analyze_photos")
async def analyze_photos(state: TriageState) -> TriageState:
    """Analyze photos using MCP for preprocessing and quality analysis"""
    logger.info(f"Analyzing photos - attempt {state['current_attempt']}")
    
    try:
        # Use MCP for image preprocessing and quality analysis only
        mcp_client = MCPHttpClient()
        async with mcp_client as client:
            # Get quality analysis first
            quality_results = []
            photo_data = []
            
            for image_path in state["image_paths"]:
                # Get quality analysis
                quality_result = await client.analyze_quality(image_path)
                quality_results.append(quality_result)
                
                # Get image data for LLM analysis
                photo_result = await client.classify_photo(image_path, state["job_context"])
                photo_data.append(photo_result)
            
            state["raw_photo_data"] = photo_data
            state["quality_results"] = quality_results
        
        state["messages"].append(
            AIMessage(content=f"Photo preprocessing completed for {len(state['image_paths'])} photos")
        )
        
        quality_issues = []
        for i, quality_result in enumerate(quality_results):
            if not quality_result.get("passes_threshold", False):
                quality_issues.append(f"Image {state['image_paths'][i]}: {quality_result.get('quality_grade', 'poor')} quality")
        
        state["quality_issues"] = quality_issues
        
    except Exception as e:
        logger.error(f"Photo analysis failed: {e}")
        state["messages"].append(AIMessage(content=f"Analysis failed: {str(e)}"))
        state["quality_issues"] = [f"Analysis error: {str(e)}"]
    
    return state