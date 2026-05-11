#!/bin/bash
set -e

# Create an isolated dummy directory to mimic user's existing repo
mkdir dummy_playtest_repo
cd dummy_playtest_repo
git init
git remote add origin https://github.com/dummy/playtest.git

# Create some fake code
mkdir src
echo "def hello(): print('Hello World')" > src/hello.py
echo "numpy" > requirements.txt

# Simulate user downloading the template
cp -r ../template_source ./template_source

echo "Running init_project in Migration mode..."
# Simulate user answers
python3 template_source/scripts/init_project.py <<'INPUT'
Dummy Project
Web App
Democracy
Low
n
n
n
n
n
n
INPUT

echo ""
echo "Verifying structural changes in the user repo..."
ls -la
ls -la .agents/engine/

echo ""
echo "Testing squad wrapper..."
./squad --help

echo ""
echo "Testing missing SDK error messages..." >&2
./squad --task "write a script" --llm openai || true
./squad --task "write a script" --llm gemini || true

echo ""
echo "Testing validate_stack.py..."
python3 scripts/validate_stack.py

echo ""
echo "Cleaning up..."
cd ..
rm -rf dummy_playtest_repo
echo "Playtest automated steps finished."
