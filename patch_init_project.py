import re

file_path = 'template_source/scripts/init_project.py'
with open(file_path, 'r') as f:
    content = f.read()

search = """    if missing:
        print("\\n\\033[1;31m❌ CRITICAL: Missing Required Dependencies\\033[0m")
        print("The Coding Squad engine requires the following packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\\nTo safely install these without polluting your global environment, please run:")
        print("\\033[1;36m  python3 -m venv venv")
        print("  source venv/bin/activate  # Or venv\\\\Scripts\\\\activate on Windows")
        print("  pip install " + " ".join(required_packages.values()) + "\\033[0m\\n")
        print("Or if you already have a virtual environment active, simply install the requirements.")
        sys.exit(1)"""

replace = """    if missing:
        print("\\n\\033[1;33m⚠️ Missing Required Dependencies detected.\\033[0m")
        print("Attempting to auto-install the following packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
            print("\\033[1;32m✅ Dependencies installed successfully.\\033[0m\\n")
        except subprocess.CalledProcessError as e:
            print("\\n\\033[1;31m❌ CRITICAL: Failed to auto-install dependencies.\\033[0m")
            print("Please ensure you have internet access and the correct permissions, or run:")
            print("\\033[1;36m  python3 -m venv venv")
            print("  source venv/bin/activate  # Or venv\\\\Scripts\\\\activate on Windows")
            print("  pip install " + " ".join(missing) + "\\033[0m\\n")
            sys.exit(1)"""

new_content = content.replace(search, replace)
if new_content == content:
    print("Failed to replace!")
else:
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("Replaced successfully!")
