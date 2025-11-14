"""
Chalice MCP (Model Context Protocol) Implementation
Following Anthropic's MCP best practices with code execution patterns
"""
from .client import (
    MCPClient,
    MCPServer,
    MCPTool,
    get_mcp_client,
    call_mcp_tool
)
from .servers import filesystem, git, execution, api, system, multimodal


def initialize_mcp_servers() -> MCPClient:
    """
    Initialize all MCP servers and register them with the client
    Following the progressive disclosure pattern from Anthropic's blog
    """
    client = get_mcp_client()

    # Register all servers
    client.register_server(filesystem.create_filesystem_server())
    client.register_server(git.create_git_server())
    client.register_server(execution.create_execution_server())
    client.register_server(api.create_api_server())
    client.register_server(system.create_system_server())
    client.register_server(multimodal.get_multimodal_server())

    return client


__all__ = [
    'MCPClient',
    'MCPServer',
    'MCPTool',
    'get_mcp_client',
    'call_mcp_tool',
    'initialize_mcp_servers'
]
