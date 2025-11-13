"""
MCP API Server
Provides API interaction tools following MCP best practices
"""
import requests
import json as json_module
from typing import Dict, Any, Optional
from ..client import MCPServer, MCPTool


class HTTPRequestTool(MCPTool):
    """Make HTTP requests to external APIs"""

    def __init__(self):
        super().__init__(
            "http",
            "Make HTTP requests (GET, POST, PUT, DELETE, PATCH) to external APIs"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to request"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
                    "description": "HTTP method",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers as key-value pairs"
                },
                "body": {
                    "type": "string",
                    "description": "Request body (JSON string or plain text)"
                },
                "params": {
                    "type": "object",
                    "description": "URL query parameters as key-value pairs"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds (default: 30)",
                    "default": 30
                },
                "follow_redirects": {
                    "type": "boolean",
                    "description": "Follow redirects (default: true)",
                    "default": True
                }
            },
            "required": ["url"]
        }

    def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        body: str = None,
        params: Dict[str, str] = None,
        timeout: int = 30,
        follow_redirects: bool = True
    ) -> Dict[str, Any]:
        try:
            kwargs = {
                "timeout": min(timeout, 120),
                "allow_redirects": follow_redirects
            }

            if headers:
                kwargs["headers"] = headers

            if params:
                kwargs["params"] = params

            if body:
                try:
                    kwargs["json"] = json_module.loads(body)
                except:
                    kwargs["data"] = body

            response = requests.request(method, url, **kwargs)

            try:
                response_json = response.json()
            except:
                response_json = None

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
                "json": response_json,
                "success": 200 <= response.status_code < 300,
                "url": response.url,
                "elapsed_ms": response.elapsed.total_seconds() * 1000
            }

        except requests.Timeout:
            return {"error": f"Request timed out after {timeout} seconds"}
        except requests.ConnectionError as e:
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}


class GraphQLTool(MCPTool):
    """Execute GraphQL queries against a GraphQL endpoint"""

    def __init__(self):
        super().__init__(
            "graphql",
            "Execute GraphQL queries against a GraphQL endpoint"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "GraphQL endpoint URL"
                },
                "query": {
                    "type": "string",
                    "description": "GraphQL query or mutation"
                },
                "variables": {
                    "type": "object",
                    "description": "Query variables as key-value pairs"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers (e.g., for authentication)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30
                }
            },
            "required": ["endpoint", "query"]
        }

    def execute(
        self,
        endpoint: str,
        query: str,
        variables: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        try:
            payload = {"query": query}
            if variables:
                payload["variables"] = variables

            response = requests.post(
                endpoint,
                json=payload,
                headers=headers or {},
                timeout=min(timeout, 120)
            )

            result = response.json()

            return {
                "data": result.get("data"),
                "errors": result.get("errors"),
                "success": "errors" not in result or not result["errors"],
                "status_code": response.status_code
            }

        except Exception as e:
            return {"error": str(e)}


class WebhookTool(MCPTool):
    """Send webhook notifications to external services"""

    def __init__(self):
        super().__init__(
            "webhook",
            "Send webhook notifications to external services"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Webhook URL"
                },
                "payload": {
                    "type": "object",
                    "description": "Webhook payload as key-value pairs"
                },
                "headers": {
                    "type": "object",
                    "description": "Additional HTTP headers"
                },
                "method": {
                    "type": "string",
                    "enum": ["POST", "PUT"],
                    "description": "HTTP method (default: POST)",
                    "default": "POST"
                }
            },
            "required": ["url", "payload"]
        }

    def execute(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        try:
            response = requests.request(
                method,
                url,
                json=payload,
                headers=headers or {},
                timeout=30
            )

            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "response": response.text
            }

        except Exception as e:
            return {"error": str(e)}


def create_api_server() -> MCPServer:
    """Create and configure the API MCP server"""
    server = MCPServer(
        "api",
        "HTTP, GraphQL, and webhook interactions with external services"
    )

    # Register all tools
    server.register_tool(HTTPRequestTool())
    server.register_tool(GraphQLTool())
    server.register_tool(WebhookTool())

    return server
