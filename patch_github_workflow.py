import re

file_path = ".github/workflows/vibe_check.yml"
with open(file_path, "r") as f:
    content = f.read()

# Update node-version
content = content.replace("node-version: '18'", "node-version: '20'")

# Add working-directory to npm install step
npm_target = """      - name: Install Node Dependencies
        run: |
          npm install --prefer-offline --no-audit"""
npm_replacement = """      - name: Install Node Dependencies
        working-directory: template_source
        run: |
          npm install --prefer-offline --no-audit"""
content = content.replace(npm_target, npm_replacement)

# Update complexity check directory
comp_target = """      - name: Architectural Complexity Check
        run: npm run check:complexity"""
comp_replacement = """      - name: Architectural Complexity Check
        working-directory: template_source
        run: npm run check:complexity"""
content = content.replace(comp_target, comp_replacement)

with open(file_path, "w") as f:
    f.write(content)
