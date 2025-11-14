"""
Extract and format code from screenshot images

This tool is part of the multimodal MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def extract_code_from_screenshot(
    image_path: str,
    language: str = "auto",
    clean_format: bool = True
) -> Dict[str, Any]:
    """
    Extract and format code from screenshot images

    Parameters:
        image_path: Path to screenshot containing code
        language: Programming language (auto-detect if not specified)
        clean_format: Clean and format extracted code

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="multimodal",
        tool_name="extract_code_from_screenshot",
        **params
    )
