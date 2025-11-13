"""
Get the status of the current git repository

This tool is part of the git MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def status(
    repo_path: str = "."
) -> Dict[str, Any]:
    """
    Get the status of the current git repository

    Parameters:
        repo_path: Path to git repository (default: current directory)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="git",
        tool_name="status",
        **params
    )
