file_path = '.github/workflows/vibe_check.yml'
with open(file_path, 'r') as f:
    content = f.read()

# Fix the working directory for npm install and npm run check:complexity
search_install = """      - name: Install Node Dependencies
        run: |
          npm install --prefer-offline --no-audit"""
replace_install = """      - name: Install Node Dependencies
        working-directory: ./template_source
        run: |
          npm install --prefer-offline --no-audit"""

search_run = """      - name: Architectural Complexity Check
        run: npm run check:complexity"""
replace_run = """      - name: Architectural Complexity Check
        working-directory: ./template_source
        run: npm run check:complexity"""

content = content.replace(search_install, replace_install)
content = content.replace(search_run, replace_run)

with open(file_path, 'w') as f:
    f.write(content)
