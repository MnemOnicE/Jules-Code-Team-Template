import re

file_path = 'template_source/.agents/engine/core/llm_config.py'
with open(file_path, 'r') as f:
    content = f.read()

# Replace openai
content = re.sub(
    r'print\("Installing openai sdk\.\.\."\)\s+subprocess\.run\(\[sys\.executable, "-m", "pip", "install", "openai"\], check=False\)',
    r'''print("Installing openai sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "openai"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install openai. Please install it manually.")''',
    content
)

# Replace google-genai
content = re.sub(
    r'print\("Installing google-genai sdk\.\.\."\)\s+subprocess\.run\(\[sys\.executable, "-m", "pip", "install", "google-genai"\], check=False\)',
    r'''print("Installing google-genai sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "google-genai"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install google-genai. Please install it manually.")''',
    content
)

# Replace ollama
content = re.sub(
    r'print\("Installing ollama sdk\.\.\."\)\s+subprocess\.run\(\[sys\.executable, "-m", "pip", "install", "ollama"\], check=False\)',
    r'''print("Installing ollama sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "ollama"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install ollama. Please install it manually.")''',
    content
)

# Replace llama-cpp-python
content = re.sub(
    r'print\("Installing llama-cpp-python sdk\.\.\."\)\s+subprocess\.run\(\[sys\.executable, "-m", "pip", "install", "llama-cpp-python"\], check=False\)',
    r'''print("Installing llama-cpp-python sdk...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install llama-cpp-python. Please install it manually.")''',
    content
)

with open(file_path, 'w') as f:
    f.write(content)
print("Replaced successfully!")
