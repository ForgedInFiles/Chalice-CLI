"""
Make HTTP requests (GET, POST, PUT, DELETE, PATCH) to external APIs

This tool is part of the api MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def http(
    url: str,
    method: str = "GET",
    headers: Dict[str, Any] = None,
    body: str = None,
    params: Dict[str, Any] = None,
    timeout: int = 30,
    follow_redirects: bool = True
) -> Dict[str, Any]:
    """
    Make HTTP requests (GET, POST, PUT, DELETE, PATCH) to external APIs

    Parameters:
        url: URL to request
        method: HTTP method
        headers: HTTP headers as key-value pairs
        body: Request body (JSON string or plain text)
        params: URL query parameters as key-value pairs
        timeout: Request timeout in seconds (default: 30)
        follow_redirects: Follow redirects (default: true)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="api",
        tool_name="http",
        **params
    )
