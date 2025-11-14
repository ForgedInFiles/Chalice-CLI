"""
Plugin Manager
Handles plugin loading, lifecycle, and dependency management
"""
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from .plugin import (
    Plugin,
    PluginMetadata,
    PluginLifecycle,
    PluginHook,
    PluginContext,
    AVAILABLE_HOOKS
)


class PluginManager:
    """
    Plugin Manager

    Manages plugin lifecycle, dependencies, and hooks
    """

    def __init__(self, plugin_dir: Optional[Path] = None):
        """
        Initialize plugin manager

        Args:
            plugin_dir: Directory containing plugins
        """
        if plugin_dir is None:
            plugin_dir = Path(__file__).parent.parent / "installed"

        self.plugin_dir = Path(plugin_dir)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, PluginHook] = {}
        self.context = PluginContext()

        # Initialize available hooks
        for hook_name, description in AVAILABLE_HOOKS.items():
            self.hooks[hook_name] = PluginHook(hook_name, description)

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins

        Returns:
            List of plugin IDs
        """
        discovered = []

        for plugin_path in self.plugin_dir.glob("*/plugin.py"):
            try:
                plugin_id = plugin_path.parent.name
                discovered.append(plugin_id)
            except Exception as e:
                print(f"Error discovering plugin: {e}")

        return discovered

    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load a plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            bool: True if loaded successfully
        """
        if plugin_id in self.plugins:
            print(f"Plugin {plugin_id} already loaded")
            return True

        plugin_path = self.plugin_dir / plugin_id / "plugin.py"
        if not plugin_path.exists():
            print(f"Plugin file not found: {plugin_path}")
            return False

        try:
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_id}",
                plugin_path
            )
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugins.{plugin_id}"] = module
            spec.loader.exec_module(module)

            # Create plugin instance
            if hasattr(module, 'create_plugin'):
                plugin = module.create_plugin()
            elif hasattr(module, 'Plugin'):
                plugin = module.Plugin()
            else:
                print(f"Plugin {plugin_id} has no entry point")
                return False

            # Set plugin state
            plugin.state = PluginLifecycle.LOADING

            # Load plugin
            if not plugin.on_load():
                print(f"Plugin {plugin_id} failed to load")
                plugin.state = PluginLifecycle.ERROR
                return False

            plugin.state = PluginLifecycle.LOADED

            # Register plugin hooks with global hooks
            for hook_name, hook in plugin.hooks.items():
                if hook_name in self.hooks:
                    for handler, priority in hook.handlers:
                        self.hooks[hook_name].register(handler, priority)

            # Store plugin
            self.plugins[plugin_id] = plugin

            # Trigger plugin loaded hook
            self.trigger_hook('plugin.loaded', plugin=plugin)

            print(f"✓ Loaded plugin: {plugin.metadata.name} v{plugin.metadata.version}")
            return True

        except Exception as e:
            print(f"Error loading plugin {plugin_id}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            bool: True if unloaded successfully
        """
        if plugin_id not in self.plugins:
            print(f"Plugin {plugin_id} not loaded")
            return False

        plugin = self.plugins[plugin_id]

        try:
            # Disable if active
            if plugin.state == PluginLifecycle.ACTIVE:
                self.disable_plugin(plugin_id)

            # Set unloading state
            plugin.state = PluginLifecycle.UNLOADING

            # Unregister hooks
            for hook_name in plugin.hooks:
                if hook_name in self.hooks:
                    for handler, _ in plugin.hooks[hook_name].handlers:
                        self.hooks[hook_name].unregister(handler)

            # Unload plugin
            plugin.on_unload()

            # Remove from registry
            del self.plugins[plugin_id]

            # Remove from sys.modules
            module_name = f"plugins.{plugin_id}"
            if module_name in sys.modules:
                del sys.modules[module_name]

            print(f"✓ Unloaded plugin: {plugin.metadata.name}")
            return True

        except Exception as e:
            print(f"Error unloading plugin {plugin_id}: {e}")
            return False

    def enable_plugin(self, plugin_id: str) -> bool:
        """
        Enable a plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            bool: True if enabled successfully
        """
        if plugin_id not in self.plugins:
            print(f"Plugin {plugin_id} not loaded")
            return False

        plugin = self.plugins[plugin_id]

        if plugin.state == PluginLifecycle.ACTIVE:
            print(f"Plugin {plugin_id} already active")
            return True

        try:
            if plugin.on_enable():
                plugin.state = PluginLifecycle.ACTIVE
                self.trigger_hook('plugin.enabled', plugin=plugin)
                print(f"✓ Enabled plugin: {plugin.metadata.name}")
                return True
            else:
                print(f"Plugin {plugin_id} failed to enable")
                return False

        except Exception as e:
            print(f"Error enabling plugin {plugin_id}: {e}")
            return False

    def disable_plugin(self, plugin_id: str) -> bool:
        """
        Disable a plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            bool: True if disabled successfully
        """
        if plugin_id not in self.plugins:
            print(f"Plugin {plugin_id} not loaded")
            return False

        plugin = self.plugins[plugin_id]

        if plugin.state != PluginLifecycle.ACTIVE:
            print(f"Plugin {plugin_id} not active")
            return True

        try:
            plugin.on_disable()
            plugin.state = PluginLifecycle.INACTIVE
            self.trigger_hook('plugin.disabled', plugin=plugin)
            print(f"✓ Disabled plugin: {plugin.metadata.name}")
            return True

        except Exception as e:
            print(f"Error disabling plugin {plugin_id}: {e}")
            return False

    def reload_plugin(self, plugin_id: str) -> bool:
        """
        Reload a plugin (hot-reload)

        Args:
            plugin_id: Plugin identifier

        Returns:
            bool: True if reloaded successfully
        """
        was_active = (
            plugin_id in self.plugins and
            self.plugins[plugin_id].state == PluginLifecycle.ACTIVE
        )

        if not self.unload_plugin(plugin_id):
            return False

        if not self.load_plugin(plugin_id):
            return False

        if was_active:
            return self.enable_plugin(plugin_id)

        return True

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin by ID"""
        return self.plugins.get(plugin_id)

    def list_plugins(self, state: Optional[PluginLifecycle] = None) -> List[Plugin]:
        """
        List plugins

        Args:
            state: Filter by state

        Returns:
            List of plugins
        """
        if state is None:
            return list(self.plugins.values())
        return [p for p in self.plugins.values() if p.state == state]

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Trigger a hook

        Args:
            hook_name: Hook name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            List of results from all handlers
        """
        if hook_name not in self.hooks:
            return []

        return self.hooks[hook_name].trigger(*args, **kwargs)

    def trigger_hook_until(
        self,
        hook_name: str,
        condition: callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Trigger hook until condition is met

        Args:
            hook_name: Hook name
            condition: Condition function
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            First result that meets condition, or None
        """
        if hook_name not in self.hooks:
            return None

        return self.hooks[hook_name].trigger_until(condition, *args, **kwargs)

    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin information

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin information dictionary
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return None

        return {
            'metadata': plugin.metadata.to_dict(),
            'state': plugin.state.value,
            'config': plugin.config,
            'hooks': list(plugin.hooks.keys())
        }

    def check_dependencies(self, plugin_id: str) -> tuple[bool, List[str]]:
        """
        Check if plugin dependencies are satisfied

        Args:
            plugin_id: Plugin identifier

        Returns:
            Tuple of (satisfied, missing_dependencies)
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return False, []

        missing = []
        for dep in plugin.metadata.dependencies:
            if dep not in self.plugins:
                missing.append(dep)

        return len(missing) == 0, missing

    def load_all_plugins(self, auto_enable: bool = True) -> Dict[str, bool]:
        """
        Load all discovered plugins

        Args:
            auto_enable: Automatically enable plugins after loading

        Returns:
            Dictionary of plugin_id -> success
        """
        discovered = self.discover_plugins()
        results = {}

        for plugin_id in discovered:
            success = self.load_plugin(plugin_id)
            results[plugin_id] = success

            if success and auto_enable:
                self.enable_plugin(plugin_id)

        return results

    def save_plugin_state(self, file_path: Optional[Path] = None):
        """Save plugin states to file"""
        if file_path is None:
            file_path = self.plugin_dir / "plugin_state.json"

        state = {
            'plugins': {
                plugin_id: {
                    'state': plugin.state.value,
                    'config': plugin.config
                }
                for plugin_id, plugin in self.plugins.items()
            }
        }

        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)

    def load_plugin_state(self, file_path: Optional[Path] = None):
        """Load plugin states from file"""
        if file_path is None:
            file_path = self.plugin_dir / "plugin_state.json"

        if not file_path.exists():
            return

        with open(file_path, 'r') as f:
            state = json.load(f)

        for plugin_id, plugin_state in state['plugins'].items():
            if plugin_id in self.plugins:
                self.plugins[plugin_id].config = plugin_state.get('config', {})
                target_state = PluginLifecycle(plugin_state['state'])

                if target_state == PluginLifecycle.ACTIVE:
                    self.enable_plugin(plugin_id)
                elif target_state == PluginLifecycle.INACTIVE:
                    self.disable_plugin(plugin_id)


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
