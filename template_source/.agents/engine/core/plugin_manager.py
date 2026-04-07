#!/usr/bin/env python3

# Jules Code Team Template - Plugin System
# Copyright (C) 2026  MnemOnicE

import os
import sys
import importlib.util
from pathlib import Path

class PluginManager:
    """Simple plugin system for extending agent capabilities"""

    def __init__(self, plugins_dir=None):
        if plugins_dir is None:
            # Find plugins directory relative to this file
            current_dir = Path(__file__).parent
            self.plugins_dir = current_dir / "plugins"
        else:
            self.plugins_dir = Path(plugins_dir)

        self.plugins = {}
        self.loaded_plugins = []

    def discover_plugins(self):
        """Discover available plugins"""
        if not self.plugins_dir.exists():
            return []

        plugins = []
        for item in self.plugins_dir.iterdir():
            if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                plugins.append(item.stem)
        return plugins

    def load_plugin(self, plugin_name):
        """Load a specific plugin"""
        plugin_file = self.plugins_dir / f"{plugin_name}.py"
        if not plugin_file.exists():
            raise FileNotFoundError(f"Plugin {plugin_name} not found")

        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load plugin {plugin_name}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if plugin has required interface
            if not hasattr(module, 'PLUGIN_INFO'):
                raise AttributeError(f"Plugin {plugin_name} missing PLUGIN_INFO")

            plugin_info = module.PLUGIN_INFO
            self.plugins[plugin_name] = {
                'module': module,
                'info': plugin_info
            }
            self.loaded_plugins.append(plugin_name)

            return module

        except Exception as e:
            raise ImportError(f"Failed to load plugin {plugin_name}: {e}")

    def load_all_plugins(self):
        """Load all available plugins"""
        plugins = self.discover_plugins()
        loaded = []
        failed = []

        for plugin_name in plugins:
            try:
                self.load_plugin(plugin_name)
                loaded.append(plugin_name)
            except Exception as e:
                failed.append((plugin_name, str(e)))

        return loaded, failed

    def get_plugin(self, plugin_name):
        """Get a loaded plugin module"""
        if plugin_name not in self.plugins:
            raise KeyError(f"Plugin {plugin_name} not loaded")
        return self.plugins[plugin_name]['module']

    def call_plugin_hook(self, hook_name, *args, **kwargs):
        """Call a hook on all loaded plugins"""
        results = {}
        for plugin_name in self.loaded_plugins:
            plugin = self.get_plugin(plugin_name)
            if hasattr(plugin, hook_name):
                try:
                    hook_func = getattr(plugin, hook_name)
                    results[plugin_name] = hook_func(*args, **kwargs)
                except Exception as e:
                    results[plugin_name] = f"Error: {e}"
        return results

# Global plugin manager instance
plugin_manager = PluginManager()

def initialize_plugins():
    """Initialize the plugin system"""
    loaded, failed = plugin_manager.load_all_plugins()

    if loaded:
        print(f"🔌 Loaded plugins: {', '.join(loaded)}")

    if failed:
        print("⚠️  Failed to load plugins:")
        for name, error in failed:
            print(f"   {name}: {error}")

# Example plugin template
PLUGIN_TEMPLATE = '''
# Example Plugin for Jules Code Team
# Save this as plugins/example.py

PLUGIN_INFO = {
    'name': 'Example Plugin',
    'version': '1.0.0',
    'description': 'An example plugin demonstrating the plugin system',
    'author': 'Your Name'
}

def on_session_start(task):
    """Called when a session starts"""
    print(f"Example plugin: Session started for task: {task}")
    return True

def on_graph_generated(graph_id):
    """Called when a graph is generated"""
    print(f"Example plugin: Graph generated: {graph_id}")
    return True

def on_session_complete(graph_id):
    """Called when a session completes"""
    print(f"Example plugin: Session completed for graph: {graph_id}")
    return True
'''