import re

file_path = "template_source/.agents/engine/core/plugin_manager.py"
with open(file_path, "r") as f:
    content = f.read()

# Add _dynamic_hooks to __init__
init_replacement = """        self.plugins = {}
        self.loaded_plugins = []
        self.allowed_plugins = self._load_allowlist()
        self._dynamic_hooks = {}"""

content = content.replace(
    "        self.plugins = {}\n        self.loaded_plugins = []\n        self.allowed_plugins = self._load_allowlist()",
    init_replacement
)

# Add register and deregister methods
new_methods = """
    def register_hook(self, hook_name, callback):
        \"\"\"Register a dynamic hook callback\"\"\"
        if hook_name not in self._dynamic_hooks:
            self._dynamic_hooks[hook_name] = []
        if callback not in self._dynamic_hooks[hook_name]:
            self._dynamic_hooks[hook_name].append(callback)

    def deregister_hook(self, hook_name, callback):
        \"\"\"Deregister a dynamic hook callback\"\"\"
        if hook_name in self._dynamic_hooks and callback in self._dynamic_hooks[hook_name]:
            self._dynamic_hooks[hook_name].remove(callback)
"""

# Insert before get_plugin
content = content.replace(
    "    def get_plugin(self, plugin_name):",
    new_methods + "\n    def get_plugin(self, plugin_name):"
)

# Update call_plugin_hook
hook_replacement = """    def call_plugin_hook(self, hook_name, *args, **kwargs):
        \"\"\"Call a hook on all loaded plugins and dynamic hooks\"\"\"
        results = {}

        # Call static plugins
        for plugin_name in self.loaded_plugins:
            plugin = self.get_plugin(plugin_name)
            if hasattr(plugin, hook_name):
                try:
                    hook_func = getattr(plugin, hook_name)
                    results[plugin_name] = hook_func(*args, **kwargs)
                except Exception as e:
                    results[plugin_name] = f"Error: {e}"

        # Call dynamic hooks
        if hook_name in self._dynamic_hooks:
            for idx, callback in enumerate(self._dynamic_hooks[hook_name]):
                try:
                    results[f"dynamic_{hook_name}_{idx}"] = callback(*args, **kwargs)
                except Exception as e:
                    results[f"dynamic_{hook_name}_{idx}"] = f"Error: {e}"

        return results"""

# Replace the old call_plugin_hook
content = re.sub(
    r"    def call_plugin_hook.*?return results",
    hook_replacement,
    content,
    flags=re.DOTALL
)

with open(file_path, "w") as f:
    f.write(content)
