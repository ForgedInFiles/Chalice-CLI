"""
Base tool class for Chalice tool system
"""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class Tool(ABC):
    """Base class for all Chalice tools"""

    def __init__(self):
        self.name = self.get_name()
        self.description = self.get_description()
        self.parameters = self.get_parameters()

    @abstractmethod
    def get_name(self) -> str:
        """Return the tool name"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Return the tool description"""
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Return the tool parameter schema"""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass

    def to_openai_format(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    def validate_parameters(self, **kwargs) -> bool:
        """Validate parameters against schema"""
        required = self.parameters.get("required", [])
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        return True


class ToolRegistry:
    """Registry for managing tools"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool

    def unregister(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]

    def get(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)

    def get_all(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI format"""
        return [tool.to_openai_format() for tool in self.tools.values()]

    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool = self.get(tool_name)
        if not tool:
            return {"error": f"Tool not found: {tool_name}"}

        try:
            tool.validate_parameters(**kwargs)
            return tool.execute(**kwargs)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
