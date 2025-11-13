"""
Execute GraphQL queries against a GraphQL endpoint

This tool is part of the api MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def graphql(
    endpoint: str,
    query: str,
    variables: Dict[str, Any] = None,
    headers: Dict[str, Any] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Execute GraphQL queries against a GraphQL endpoint

    Parameters:
        endpoint: GraphQL endpoint URL
        query: GraphQL query or mutation
        variables: Query variables as key-value pairs
        headers: HTTP headers (e.g., for authentication)
        timeout: Request timeout in seconds

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="api",
        tool_name="graphql",
        **params
    )
