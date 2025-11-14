"""
Analyze and interpret diagrams, charts, flowcharts, and visual data

This tool is part of the multimodal MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def interpret_diagram(
    image_path: str,
    diagram_type: str = "auto",
    extract_text: bool = True
) -> Dict[str, Any]:
    """
    Analyze and interpret diagrams, charts, flowcharts, and visual data

    Parameters:
        image_path: Path to diagram image
        diagram_type: Type of diagram (flowchart, uml, erd, chart, architecture)
        extract_text: Extract text from diagram

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="multimodal",
        tool_name="interpret_diagram",
        **params
    )
