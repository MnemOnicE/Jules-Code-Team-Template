import os
import yaml
from dotenv import load_dotenv, set_key

class LLMConfigManager:
    def __init__(self, root_dir=None):
        if root_dir is None:
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        else:
            self.root_dir = root_dir

        self.env_path = os.path.join(self.root_dir, '.env')
        self.config_path = os.path.join(self.root_dir, 'llm_config.yaml')

        # Load existing .env if it exists
        if os.path.exists(self.env_path):
            load_dotenv(self.env_path)

    def get_api_key(self, key_name):
        return os.environ.get(key_name)

    def set_api_key(self, key_name, key_value):
        # Create .env if it doesn't exist
        if not os.path.exists(self.env_path):
            with open(self.env_path, 'w'):
                pass

        set_key(self.env_path, key_name, key_value)
        os.environ[key_name] = key_value

    def load_config(self):
        if not os.path.exists(self.config_path):
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError:
                return {}

    def save_config(self, config_data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False)

    def get_provider_config(self, provider):
        config = self.load_config()
        return config.get('providers', {}).get(provider, {})

    def set_provider_config(self, provider, provider_config):
        config = self.load_config()
        if 'providers' not in config:
            config['providers'] = {}

        config['providers'][provider] = provider_config
        self.save_config(config)

    def get_active_provider(self):
        config = self.load_config()
        return config.get('active_provider')

    def set_active_provider(self, provider):
        config = self.load_config()
        config['active_provider'] = provider
        self.save_config(config)

def configure_llm_providers():
    import sys
    import subprocess

    print("\nBrain: LLM Provider Configuration")
    providers = []

    def get_input(prompt, default=None):
        if default:
            user_input = input(f"{prompt} [{default}]: ")
            return user_input if user_input.strip() else default
        return input(f"{prompt}: ")

    print("Select the LLM providers you intend to use. Enter 'y' to install dependencies and configure.")

    if get_input("Use OpenAI?", "y").lower() == 'y':
        providers.append('openai')
        api_key = get_input("OpenAI API Key (leave blank to set later)", "")
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            mgr = LLMConfigManager()
            mgr.set_api_key('OPENAI_API_KEY', api_key)
        print("Installing openai sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "openai"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install openai sdk. Please install manually: pip install openai")

    if get_input("Use Gemini?", "n").lower() == 'y':
        providers.append('gemini')
        api_key = get_input("Gemini API Key (leave blank to set later)", "")
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
            mgr = LLMConfigManager()
            mgr.set_api_key('GEMINI_API_KEY', api_key)
        print("Installing google-genai sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "google-genai"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install google-genai sdk. Please install manually: pip install google-genai")

    if get_input("Use Jules API?", "n").lower() == 'y':
        providers.append('jules')
        api_key = get_input("Jules API Key (leave blank to set later)", "")
        if api_key:
            os.environ['JULES_API_KEY'] = api_key
            mgr = LLMConfigManager()
            mgr.set_api_key('JULES_API_KEY', api_key)

    if get_input("Use Ollama (Local)?", "n").lower() == 'y':
        providers.append('ollama')
        model = get_input("Ollama Default Model", "llama3")
        mgr = LLMConfigManager()
        mgr.set_api_key('OLLAMA_MODEL', model)
        print("Installing ollama sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "ollama"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install ollama sdk. Please install manually: pip install ollama")

    if get_input("Use Llama.cpp (Local)?", "n").lower() == 'y':
        providers.append('llamacpp')
        model_path = get_input("Llama.cpp Model Path", "./models/model.gguf")
        mgr = LLMConfigManager()
        mgr.set_api_key('LLAMACPP_MODEL_PATH', model_path)
        print("Installing llama-cpp-python sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install llama-cpp-python sdk. Please install manually: pip install llama-cpp-python")

    if providers:
        print("\nBrain: Generating llm_config.yaml for active provider...")
        active = providers[0]
        mgr = LLMConfigManager()

        config = mgr.load_config()
        config['active_provider'] = active
        if 'providers' not in config:
            config['providers'] = {}
        for p in providers:
            if p not in config['providers']:
                config['providers'][p] = {}
        mgr.save_config(config)
        print(f"✅ Set active LLM provider to: {active}")
