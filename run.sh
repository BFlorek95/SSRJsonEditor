#!/bin/bash
# Launch script for SSR JSON Editor (Mac/Linux)

echo "Starting SSR JSON Editor..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.7 or higher from https://www.python.org/"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import ijson" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Run the application
python3 json_editor.py
