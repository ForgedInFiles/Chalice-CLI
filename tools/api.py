"""
API interaction tools for external service communication
"""
import requests
import json
from typing import Dict, Any, Optional
from .base import Tool


class HTTPRequest(Tool):
    """Make HTTP requests to APIs"""

    def get_name(self) -> str:
        return "http_request"

    def get_description(self) -> str:
        return "Make HTTP requests (GET, POST, PUT, DELETE, PATCH) to external APIs"

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
        """Make HTTP request"""
        try:
            # Prepare request
            kwargs = {
                "timeout": min(timeout, 120),  # Max 2 minutes
                "allow_redirects": follow_redirects
            }

            if headers:
                kwargs["headers"] = headers

            if params:
                kwargs["params"] = params

            if body:
                # Try to parse as JSON, otherwise send as text
                try:
                    kwargs["json"] = json.loads(body)
                except:
                    kwargs["data"] = body

            # Make request
            response = requests.request(method, url, **kwargs)

            # Parse response
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


class GraphQLQuery(Tool):
    """Execute GraphQL queries"""

    def get_name(self) -> str:
        return "graphql_query"

    def get_description(self) -> str:
        return "Execute GraphQL queries against a GraphQL endpoint"

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
        """Execute GraphQL query"""
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


class WebhookSender(Tool):
    """Send webhook notifications"""

    def get_name(self) -> str:
        return "send_webhook"

    def get_description(self) -> str:
        return "Send webhook notifications to external services"

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
        """Send webhook"""
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
