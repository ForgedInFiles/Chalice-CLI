"""
Delete a file or directory (recursive for directories)

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def delete_path(
    path: str
) -> Dict[str, Any]:
    """
    Delete a file or directory (recursive for directories)

    Parameters:
        path: Absolute or relative path to delete

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="delete_path",
        **params
    )
