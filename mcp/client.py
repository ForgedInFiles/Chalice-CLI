"""
MCP Client for Chalice
Provides the core infrastructure for code execution with MCP servers
"""
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import json
import importlib.util
import sys


class MCPClient:
    """
    MCP Client that manages connections to MCP servers and handles tool calls
    Implements the code execution pattern from Anthropic's MCP best practices
    """

    def __init__(self):
        self.servers: Dict[str, 'MCPServer'] = {}
        self.tool_cache: Dict[str, Dict[str, Any]] = {}
        self.execution_context: Dict[str, Any] = {}

    def register_server(self, server: 'MCPServer'):
        """Register an MCP server"""
        self.servers[server.name] = server

    def get_server(self, name: str) -> Optional['MCPServer']:
        """Get a registered server by name"""
        return self.servers.get(name)

    def list_servers(self) -> List[str]:
        """List all registered server names"""
        return list(self.servers.keys())

    def call_tool(self, server_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool on an MCP server
        This is the core callMCPTool function that tools use
        """
        server = self.get_server(server_name)
        if not server:
            return {"error": f"Server not found: {server_name}"}

        tool = server.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name} on server {server_name}"}

        try:
            result = tool.execute(**kwargs)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    def search_tools(
        self,
        query: str,
        server_name: Optional[str] = None,
        detail_level: str = "name_and_description"
    ) -> List[Dict[str, Any]]:
        """
        Search for tools across all servers or a specific server
        Implements progressive disclosure pattern

        Args:
            query: Search term to match against tool names and descriptions
            server_name: Optional server name to limit search scope
            detail_level: "name_only", "name_and_description", or "full"
        """
        results = []
        servers_to_search = [self.servers[server_name]] if server_name else self.servers.values()

        for server in servers_to_search:
            for tool_name, tool in server.tools.items():
                # Simple substring matching
                if query.lower() in tool_name.lower() or query.lower() in tool.description.lower():
                    if detail_level == "name_only":
                        results.append({
                            "server": server.name,
                            "tool": tool_name
                        })
                    elif detail_level == "name_and_description":
                        results.append({
                            "server": server.name,
                            "tool": tool_name,
                            "description": tool.description
                        })
                    else:  # full
                        results.append({
                            "server": server.name,
                            "tool": tool_name,
                            "description": tool.description,
                            "parameters": tool.get_parameters(),
                            "returns": getattr(tool, 'return_type', 'Any')
                        })

        return results

    def get_server_manifest(self, server_name: str) -> Dict[str, Any]:
        """
        Get the manifest for a server (all available tools)
        Used for filesystem-based progressive disclosure
        """
        server = self.get_server(server_name)
        if not server:
            return {"error": f"Server not found: {server_name}"}

        return {
            "name": server.name,
            "description": server.description,
            "tools": [
                {
                    "name": tool_name,
                    "description": tool.description
                }
                for tool_name, tool in server.tools.items()
            ]
        }

    def get_tool_definition(self, server_name: str, tool_name: str) -> Dict[str, Any]:
        """
        Get the full definition for a specific tool
        Used for on-demand loading
        """
        server = self.get_server(server_name)
        if not server:
            return {"error": f"Server not found: {server_name}"}

        tool = server.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}

        return {
            "name": tool_name,
            "description": tool.description,
            "parameters": tool.get_parameters(),
            "returns": getattr(tool, 'return_type', 'Any'),
            "server": server_name
        }


class MCPServer:
    """
    Base class for MCP servers
    Each server groups related tools (filesystem, git, execution, etc.)
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tools: Dict[str, 'MCPTool'] = {}

    def register_tool(self, tool: 'MCPTool'):
        """Register a tool with this server"""
        self.tools[tool.name] = tool
        tool.server = self

    def get_tool(self, name: str) -> Optional['MCPTool']:
        """Get a tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all tool names"""
        return list(self.tools.keys())


class MCPTool:
    """
    Base class for MCP tools
    Each tool represents a single capability
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.server: Optional[MCPServer] = None

    def get_parameters(self) -> Dict[str, Any]:
        """Return the parameter schema for this tool"""
        raise NotImplementedError

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        raise NotImplementedError


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


def call_mcp_tool(server_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Global function for calling MCP tools
    This is what the generated code will use
    """
    client = get_mcp_client()
    return client.call_tool(server_name, tool_name, **kwargs)
