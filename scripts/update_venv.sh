#!/bin/bash
# Script to update the virtual environment with the latest LangChain dependencies
# This script should be run from the root directory of the project

set -e # Exit on error

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating a new one..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source venv/bin/activate
fi

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing/Upgrading dependencies from requirements.txt..."
pip install -r requirements.txt --upgrade

# Check if models need to be downloaded
if ! python -c "import nltk; nltk.data.find('tokenizers/punkt')" 2>/dev/null; then
    echo "Downloading NLTK data..."
    python -c "import nltk; nltk.download('punkt')"
fi

if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "Downloading spaCy model..."
    python -m spacy download en_core_web_sm
fi

echo "Environment updated successfully!"
echo "To activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"