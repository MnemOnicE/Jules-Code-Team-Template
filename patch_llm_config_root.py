file_path = 'template_source/.agents/engine/core/llm_config.py'
with open(file_path, 'r') as f:
    content = f.read()

search = """class LLMConfigManager:
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        else:
            self.root_dir = root_dir"""

replace = """class LLMConfigManager:
    def __init__(self, root_dir=None):
        if root_dir is None:
            # Dynamically resolve root dir (find .git or .agents)
            current_dir = os.path.abspath(os.path.dirname(__file__))
            found_root = None

            while current_dir != os.path.dirname(current_dir):
                if os.path.exists(os.path.join(current_dir, '.agents')) or os.path.exists(os.path.join(current_dir, '.git')):
                    found_root = current_dir
                    break
                current_dir = os.path.dirname(current_dir)

            if found_root:
                self.root_dir = found_root
            else:
                # Fallback to relative path if not found
                self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        else:
            self.root_dir = root_dir"""

new_content = content.replace(search, replace)
if new_content == content:
    print("Failed to replace!")
else:
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("Replaced successfully!")
