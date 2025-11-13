"""
View git commit history

This tool is part of the git MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def log(
    repo_path: str = ".",
    limit: int = 10,
    oneline: bool = True
) -> Dict[str, Any]:
    """
    View git commit history

    Parameters:
        repo_path: Path to git repository
        limit: Number of commits to show (default: 10)
        oneline: Show one line per commit

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="git",
        tool_name="log",
        **params
    )
