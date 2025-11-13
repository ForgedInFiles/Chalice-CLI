"""
Create a new directory and any necessary parent directories

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def create_directory(
    path: str
) -> Dict[str, Any]:
    """
    Create a new directory and any necessary parent directories

    Parameters:
        path: Absolute or relative directory path to create

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="create_directory",
        **params
    )
