"""
Execute whitelisted system commands safely with output capture

This tool is part of the system MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def command(
    command: str,
    args: List[Any] = None,
    timeout: int = 30,
    working_dir: str = "."
) -> Dict[str, Any]:
    """
    Execute whitelisted system commands safely with output capture

    Parameters:
        command: Command to execute
        args: Command arguments
        timeout: Timeout in seconds (default: 30)
        working_dir: Working directory

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="system",
        tool_name="command",
        **params
    )
