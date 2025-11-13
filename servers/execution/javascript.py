"""
Execute JavaScript code using Node.js with timeout controls

This tool is part of the execution MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def javascript(
    code: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Execute JavaScript code using Node.js with timeout controls

    Parameters:
        code: JavaScript code to execute
        timeout: Timeout in seconds (default: 30, max: 300)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="execution",
        tool_name="javascript",
        **params
    )
