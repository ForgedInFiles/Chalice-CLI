"""
Analyze images using GPT-4 Vision or Claude 3 Opus with vision capabilities

This tool is part of the multimodal MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def analyze_image(
    image_path: str,
    prompt: str,
    model: str = "gpt-4-vision",
    detail_level: str = "high"
) -> Dict[str, Any]:
    """
    Analyze images using GPT-4 Vision or Claude 3 Opus with vision capabilities

    Parameters:
        image_path: Path to the image file
        prompt: Analysis prompt or question about the image
        model: Vision model to use (gpt-4-vision, claude-3-opus, claude-3-sonnet)
        detail_level: Level of detail (low, medium, high)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="multimodal",
        tool_name="analyze_image",
        **params
    )
