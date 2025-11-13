"""
Execute Bash commands with safety controls and timeout

This tool is part of the execution MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def bash(
    command: str,
    timeout: int = 30,
    working_dir: str = "."
) -> Dict[str, Any]:
    """
    Execute Bash commands with safety controls and timeout

    Parameters:
        command: Bash command to execute
        timeout: Timeout in seconds (default: 30, max: 300)
        working_dir: Working directory for command execution

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="execution",
        tool_name="bash",
        **params
    )
