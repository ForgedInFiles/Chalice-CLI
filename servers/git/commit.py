"""
Create a git commit with the specified message

This tool is part of the git MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def commit(
    message: str,
    repo_path: str = ".",
    add_all: bool = False
) -> Dict[str, Any]:
    """
    Create a git commit with the specified message

    Parameters:
        message: Commit message
        repo_path: Path to git repository
        add_all: Add all changes before committing

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="git",
        tool_name="commit",
        **params
    )
