"""
Write or overwrite content to a file

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def write_file(
    path: str,
    content: str
) -> Dict[str, Any]:
    """
    Write or overwrite content to a file

    Parameters:
        path: Absolute or relative file path to write to
        content: Content to write to the file

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="write_file",
        **params
    )
