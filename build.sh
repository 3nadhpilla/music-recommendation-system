#!/usr/bin/env bash

echo "--- Starting Render Build ---"
echo "Current Working Directory: $(pwd)"
echo "Python version (from 'python'):"
python --version
echo "Python version (from 'python3'):"
python3 --version
echo "Pip version:"
pip --version
echo "--- Installing dependencies from requirements.txt ---"
pip install --no-cache-dir -r requirements.txt
echo "--- Dependency installation complete ---"