"""
Generate intelligent summaries of text documents

This tool is part of the multimodal MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def summarize_document(
    content: str,
    max_length: int = 200,
    style: str = "paragraph"
) -> Dict[str, Any]:
    """
    Generate intelligent summaries of text documents

    Parameters:
        content: Document content to summarize
        max_length: Maximum summary length in words
        style: Summary style (bullet_points, paragraph, executive)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="multimodal",
        tool_name="summarize_document",
        **params
    )
