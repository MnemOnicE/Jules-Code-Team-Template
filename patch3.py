with open('template_source/scripts/validate_stack.py', 'r') as f:
    content = f.read()

content = content.replace("es6_matches = re.findall(r'import\\s+.*?from\\s+[\\'\\\"]([@a-zA-Z0-9_/-]+)[\\'\\\"]', content)", "es6_matches = JS_ES6_IMPORT_RE.findall(content)")
content = content.replace("cjs_matches = re.findall(r'require\\s*\\(\\s*[\\'\\\"]([@a-zA-Z0-9_/-]+)[\\'\\\"]\\s*\\)', content)", "cjs_matches = JS_CJS_IMPORT_RE.findall(content)")

with open('template_source/scripts/validate_stack.py', 'w') as f:
    f.write(content)
