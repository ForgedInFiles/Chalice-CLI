"""
Install, update, or list packages using pip, npm, yarn, cargo, or go

This tool is part of the system MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def packages(
    manager: str,
    action: str,
    package: str = None,
    global: bool = False
) -> Dict[str, Any]:
    """
    Install, update, or list packages using pip, npm, yarn, cargo, or go

    Parameters:
        manager: Package manager to use
        action: Action to perform
        package: Package name (required for install/uninstall/search)
        global: Install globally (for npm/yarn)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="system",
        tool_name="packages",
        **params
    )
