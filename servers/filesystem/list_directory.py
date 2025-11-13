"""
List all files and subdirectories in a given path with their types and sizes

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def list_directory(
    path: str
) -> Dict[str, Any]:
    """
    List all files and subdirectories in a given path with their types and sizes

    Parameters:
        path: Absolute or relative directory path to list

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="list_directory",
        **params
    )
