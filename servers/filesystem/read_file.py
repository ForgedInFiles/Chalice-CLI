"""
Read content from a file with optional line range limits

This tool is part of the filesystem MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def read_file(
    path: str,
    offset: int = 0,
    limit: int = 2000
) -> Dict[str, Any]:
    """
    Read content from a file with optional line range limits

    Parameters:
        path: Absolute or relative file path to read
        offset: Starting line number (0-based)
        limit: Maximum number of lines to read

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="filesystem",
        tool_name="read_file",
        **params
    )
