"""
Move or rename a file or directory

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def move_path(
    src: str,
    dst: str
) -> Dict[str, Any]:
    """
    Move or rename a file or directory

    Parameters:
        src: Source path to move
        dst: Destination path

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="move_path",
        **params
    )
