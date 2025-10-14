#!/bin/bash
# Build script for macOS

echo "=========================================="
echo "Building SSR JSON Editor for macOS"
echo "=========================================="

# Activate virtual environment
source SSRVenv/bin/activate

# Install PyInstaller if not already installed
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the macOS app
echo "Building macOS application..."
pyinstaller build_spec.spec

# Check if build was successful
if [ -d "dist/SSR JSON Editor.app" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Build successful!"
    echo "=========================================="
    echo ""
    echo "macOS App Location: dist/SSR JSON Editor.app"
    echo ""
    echo "To install:"
    echo "1. Open the 'dist' folder"
    echo "2. Drag 'SSR JSON Editor.app' to your Applications folder"
    echo ""
    echo "Note: On first launch, you may need to:"
    echo "  - Right-click the app and select 'Open'"
    echo "  - Or go to System Preferences > Security & Privacy"
    echo "    and allow the app to run"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    echo ""
fi
