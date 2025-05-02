#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name=venv --display-name "Python (venv)"
echo "✅ Virtual environment set up and Jupyter kernel registered!"
