"""
Execute Python code in a sandboxed environment with timeout and resource controls

This tool is part of the execution MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def python(
    code: str,
    timeout: int = 30,
    input_data: str = ""
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed environment with timeout and resource controls

    Parameters:
        code: Python code to execute
        timeout: Timeout in seconds (default: 30, max: 300)
        input_data: Input data to pass to the code via stdin

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="execution",
        tool_name="python",
        **params
    )
