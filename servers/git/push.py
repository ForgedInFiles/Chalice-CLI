"""
Push commits to remote repository

This tool is part of the git MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def push(
    repo_path: str = ".",
    remote: str = "origin",
    branch: str = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Push commits to remote repository

    Parameters:
        repo_path: Path to git repository
        remote: Remote name (default: origin)
        branch: Branch to push (optional, defaults to current)
        force: Force push (use with caution)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="git",
        tool_name="push",
        **params
    )
