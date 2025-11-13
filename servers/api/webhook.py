"""
Send webhook notifications to external services

This tool is part of the api MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def webhook(
    url: str,
    payload: Dict[str, Any],
    headers: Dict[str, Any] = None,
    method: str = "POST"
) -> Dict[str, Any]:
    """
    Send webhook notifications to external services

    Parameters:
        url: Webhook URL
        payload: Webhook payload as key-value pairs
        headers: Additional HTTP headers
        method: HTTP method (default: POST)

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="api",
        tool_name="webhook",
        **params
    )
