"""
Chalice Plugin System
Extensible plugin architecture for Chalice
"""
from .plugin import (
    Plugin,
    PluginMetadata,
    PluginPriority,
    PluginLifecycle,
    PluginHook,
    PluginCommand,
    PluginTool,
    PluginContext,
    AVAILABLE_HOOKS,
    create_plugin_template
)
from .manager import (
    PluginManager,
    get_plugin_manager
)

__all__ = [
    'Plugin',
    'PluginMetadata',
    'PluginPriority',
    'PluginLifecycle',
    'PluginHook',
    'PluginCommand',
    'PluginTool',
    'PluginContext',
    'AVAILABLE_HOOKS',
    'create_plugin_template',
    'PluginManager',
    'get_plugin_manager'
]
