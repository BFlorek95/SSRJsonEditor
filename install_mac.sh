#!/bin/bash
# macOS Installation Script for SSR JSON Editor

echo "SSR JSON Editor - macOS Installation"
echo "====================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is not installed."
    echo "Please install Homebrew first: https://brew.sh"
    exit 1
fi

echo "✓ Homebrew found"

# Check for Python with tkinter support
echo ""
echo "Checking Python installation..."

# First, let's try to import tkinter
if python3 -c "import tkinter" 2>/dev/null; then
    echo "✓ Python with tkinter is already installed"
else
    echo "❌ tkinter not found in current Python"
    echo ""
    echo "Installing Python with tkinter support..."

    # Install python-tk using Homebrew
    brew install python-tk@3.13

    # Verify installation
    if python3 -c "import tkinter" 2>/dev/null; then
        echo "✓ tkinter installed successfully"
    else
        echo ""
        echo "⚠️  Alternative solution needed..."
        echo "Trying to reinstall Python..."
        brew reinstall python@3.13

        if python3 -c "import tkinter" 2>/dev/null; then
            echo "✓ tkinter now available"
        else
            echo ""
            echo "❌ Could not install tkinter automatically."
            echo ""
            echo "Please try one of these solutions:"
            echo ""
            echo "Option 1: Install python-tk"
            echo "  brew install python-tk@3.13"
            echo ""
            echo "Option 2: Use system Python"
            echo "  /usr/bin/python3 -m pip install --user ijson"
            echo "  /usr/bin/python3 json_editor.py"
            echo ""
            echo "Option 3: Install Python from python.org"
            echo "  Download from: https://www.python.org/downloads/"
            echo "  (includes tkinter by default)"
            exit 1
        fi
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test the application
echo ""
echo "Testing application..."
if python3 -c "import tkinter; import ijson; print('✓ All modules available')" 2>/dev/null; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Installation complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To run the application:"
    echo "  ./run.sh"
    echo ""
    echo "Or directly:"
    echo "  python3 json_editor.py"
    echo ""
else
    echo "❌ Module test failed"
    exit 1
fi
