"""
Check if a path exists and return its type and metadata

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def file_exists(
    path: str
) -> Dict[str, Any]:
    """
    Check if a path exists and return its type and metadata

    Parameters:
        path: Path to check for existence

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="file_exists",
        **params
    )
