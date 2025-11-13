"""
List or find running processes

This tool is part of the system MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def processes(
    action: str,
    pattern: str = None
) -> Dict[str, Any]:
    """
    List or find running processes

    Parameters:
        action: Action to perform
        pattern: Process name pattern (for find action)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="system",
        tool_name="processes",
        **params
    )
