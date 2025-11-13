"""
List, create, switch, or delete git branches

This tool is part of the git MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def branch(
    action: str,
    branch_name: str = None,
    repo_path: str = "."
) -> Dict[str, Any]:
    """
    List, create, switch, or delete git branches

    Parameters:
        action: Action to perform
        branch_name: Branch name (required for create/switch/delete)
        repo_path: Path to git repository

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="git",
        tool_name="branch",
        **params
    )
