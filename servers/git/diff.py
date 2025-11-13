"""
View git diff for staged or unstaged changes

This tool is part of the git MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def diff(
    repo_path: str = ".",
    staged: bool = False,
    file_path: str = None
) -> Dict[str, Any]:
    """
    View git diff for staged or unstaged changes

    Parameters:
        repo_path: Path to git repository
        staged: Show staged changes (default: false shows unstaged)
        file_path: Specific file to diff (optional)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="git",
        tool_name="diff",
        **params
    )
