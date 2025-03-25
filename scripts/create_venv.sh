#!/bin/bash
# Script to set up the virtual environment using Python 3.11
# This script should be run from the root directory of the project

set -e # Exit on error

# Use python3.11 specifically
PYTHON_PATH=$(which python3.11)
if [ -z "$PYTHON_PATH" ]; then
    echo "Error: Python 3.11 not found. Please make sure it's installed and in your PATH."
    exit 1
fi

echo "Using Python at: $PYTHON_PATH"

# Remove existing venv if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

echo "Creating a fresh virtual environment with Python 3.11..."
$PYTHON_PATH -m venv venv

# Activate virtual environment
source venv/bin/activate

echo "Installing pip, setuptools, and wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing core dependencies first..."
python -m pip install python-dotenv requests pydantic

echo "Installing LangChain and OpenAI..."
python -m pip install "langchain>=0.3.0" "langchain-openai>=0.1.0" "langgraph>=0.1.0" "openai>=1.6.0"

echo "Installing NLTK and spaCy..."
python -m pip install nltk spacy

echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt')"

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Installing remaining dependencies from requirements.txt..."
python -m pip install -r requirements.txt

echo "Environment created successfully with Python 3.11!"
echo "To activate: source venv/bin/activate"