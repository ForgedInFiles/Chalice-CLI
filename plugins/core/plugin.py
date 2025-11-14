"""
Chalice Plugin System
Extensible plugin architecture with hot-loading and event hooks
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import importlib
import inspect
from pathlib import Path


class PluginPriority(Enum):
    """Plugin execution priority"""
    HIGHEST = 0
    HIGH = 25
    NORMAL = 50
    LOW = 75
    LOWEST = 100


class PluginLifecycle(Enum):
    """Plugin lifecycle states"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADING = "unloading"


class PluginMetadata:
    """Plugin metadata"""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.name = data.get('name', '')
        self.version = data.get('version', '1.0.0')
        self.description = data.get('description', '')
        self.author = data.get('author', '')
        self.license = data.get('license', 'MIT')
        self.homepage = data.get('homepage', '')
        self.dependencies = data.get('dependencies', [])
        self.required_version = data.get('required_version', '>=3.0.0')
        self.tags = data.get('tags', [])
        self.category = data.get('category', 'general')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'license': self.license,
            'homepage': self.homepage,
            'dependencies': self.dependencies,
            'required_version': self.required_version,
            'tags': self.tags,
            'category': self.category
        }


class PluginHook:
    """
    Plugin hook for event-driven extensions

    Hooks allow plugins to respond to events in Chalice
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.handlers: List[tuple[Callable, int]] = []  # (handler, priority)

    def register(self, handler: Callable, priority: int = PluginPriority.NORMAL.value):
        """Register a hook handler"""
        self.handlers.append((handler, priority))
        # Sort by priority
        self.handlers.sort(key=lambda x: x[1])

    def unregister(self, handler: Callable):
        """Unregister a hook handler"""
        self.handlers = [(h, p) for h, p in self.handlers if h != handler]

    def trigger(self, *args, **kwargs) -> List[Any]:
        """Trigger all handlers for this hook"""
        results = []
        for handler, _ in self.handlers:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook handler error: {e}")
        return results

    def trigger_until(self, condition: Callable, *args, **kwargs) -> Any:
        """Trigger handlers until condition is met"""
        for handler, _ in self.handlers:
            try:
                result = handler(*args, **kwargs)
                if condition(result):
                    return result
            except Exception as e:
                print(f"Hook handler error: {e}")
        return None


class Plugin(ABC):
    """
    Base plugin class

    All plugins must inherit from this class and implement the required methods
    """

    def __init__(self):
        self.metadata = self.get_metadata()
        self.state = PluginLifecycle.UNLOADED
        self.config: Dict[str, Any] = {}
        self.hooks: Dict[str, PluginHook] = {}

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def on_load(self) -> bool:
        """
        Called when plugin is loaded

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        pass

    @abstractmethod
    def on_enable(self) -> bool:
        """
        Called when plugin is enabled

        Returns:
            bool: True if enabled successfully, False otherwise
        """
        pass

    @abstractmethod
    def on_disable(self):
        """Called when plugin is disabled"""
        pass

    @abstractmethod
    def on_unload(self):
        """Called when plugin is unloaded"""
        pass

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

    def register_hook(self, hook_name: str, handler: Callable, priority: int = PluginPriority.NORMAL.value):
        """Register a hook handler"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = PluginHook(hook_name)
        self.hooks[hook_name].register(handler, priority)

    def unregister_hook(self, hook_name: str, handler: Callable):
        """Unregister a hook handler"""
        if hook_name in self.hooks:
            self.hooks[hook_name].unregister(handler)


class PluginCommand:
    """Plugin-contributed command"""

    def __init__(self, name: str, description: str, handler: Callable):
        self.name = name
        self.description = description
        self.handler = handler
        self.aliases: List[str] = []
        self.usage = ""

    def execute(self, *args, **kwargs) -> Any:
        """Execute the command"""
        return self.handler(*args, **kwargs)


class PluginTool:
    """Plugin-contributed tool"""

    def __init__(self, name: str, description: str, handler: Callable):
        self.name = name
        self.description = description
        self.handler = handler
        self.parameters: Dict[str, Any] = {}

    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool"""
        return self.handler(*args, **kwargs)


class PluginContext:
    """
    Context provided to plugins

    Gives plugins access to Chalice internals safely
    """

    def __init__(self, chalice_instance=None):
        self.chalice = chalice_instance
        self.data: Dict[str, Any] = {}

    def get_mcp_client(self):
        """Get MCP client instance"""
        from mcp import get_mcp_client
        return get_mcp_client()

    def get_marketplace(self):
        """Get agent marketplace instance"""
        from agents.marketplace import get_marketplace
        return get_marketplace()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get shared data"""
        return self.data.get(key, default)

    def set_data(self, key: str, value: Any):
        """Set shared data"""
        self.data[key] = value

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        print(f"[{level}] {message}")


# Available hooks in Chalice
AVAILABLE_HOOKS = {
    # Lifecycle hooks
    "chalice.startup": "Called when Chalice starts",
    "chalice.shutdown": "Called when Chalice shuts down",

    # Chat hooks
    "chat.message.received": "Called when a message is received",
    "chat.message.sending": "Called before a message is sent",
    "chat.message.sent": "Called after a message is sent",

    # Agent hooks
    "agent.loading": "Called when an agent is being loaded",
    "agent.loaded": "Called when an agent is loaded",
    "agent.executing": "Called before agent execution",
    "agent.executed": "Called after agent execution",

    # Tool hooks
    "tool.calling": "Called before a tool is called",
    "tool.called": "Called after a tool is called",

    # Model hooks
    "model.switching": "Called before model switch",
    "model.switched": "Called after model switch",

    # Command hooks
    "command.executing": "Called before command execution",
    "command.executed": "Called after command execution",

    # Error hooks
    "error.occurred": "Called when an error occurs",

    # Custom hooks (plugins can define their own)
    "plugin.loaded": "Called when a plugin is loaded",
    "plugin.enabled": "Called when a plugin is enabled",
    "plugin.disabled": "Called when a plugin is disabled",
}


def create_plugin_template(plugin_name: str, author: str) -> str:
    """Generate a plugin template"""
    template = f'''"""
{plugin_name} Plugin for Chalice
"""
from plugins.core.plugin import Plugin, PluginMetadata, PluginPriority


class {plugin_name.replace(" ", "")}Plugin(Plugin):
    """
    {plugin_name} plugin

    Description: What your plugin does
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata({{
            'id': '{plugin_name.lower().replace(" ", "_")}',
            'name': '{plugin_name}',
            'version': '1.0.0',
            'description': 'Description of your plugin',
            'author': '{author}',
            'license': 'MIT',
            'dependencies': [],
            'required_version': '>=3.0.0',
            'tags': ['example'],
            'category': 'general'
        }})

    def on_load(self) -> bool:
        """Load plugin resources"""
        print(f"Loading {{self.metadata.name}}...")

        # Register hooks
        self.register_hook('chat.message.received', self.on_message_received)

        return True

    def on_enable(self) -> bool:
        """Enable plugin functionality"""
        print(f"Enabling {{self.metadata.name}}...")
        return True

    def on_disable(self):
        """Disable plugin functionality"""
        print(f"Disabling {{self.metadata.name}}...")

    def on_unload(self):
        """Cleanup plugin resources"""
        print(f"Unloading {{self.metadata.name}}...")

    # Hook handlers
    def on_message_received(self, message: str, **kwargs):
        """Handle incoming messages"""
        print(f"Plugin received message: {{message}}")
        # Process message here
        return message


# Plugin entry point
def create_plugin():
    """Factory function to create plugin instance"""
    return {plugin_name.replace(" ", "")}Plugin()
'''
    return template
